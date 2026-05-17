"""
mastoc_llm_bridge.py
====================
Python bridge between NetLogo MASTOC-LLM model and LLM backends.

Responsibilities:
  - Agent decision-making via LLM (Anthropic or Ollama/OpenAI-compat)
  - Rolling per-agent memory (last N rounds)
  - Agent-to-agent message passing (communication layer)
  - Per-tick logging: decisions, reasoning traces, resource state
  - Ostrom institution detection via a secondary LLM classification pass
  - Baseline best-response heuristic (approximates original Nash behaviour)

Called from NetLogo via the `py` extension:
    py:set "ctx"  <list of values>
    let action    py:runresult "bridge.decide_from_context(ctx)"
    let msg       py:runresult "bridge.get_outgoing_message(agent_id)"
    py:run        "bridge.deliver_message(from_id, to_id, msg)"
    py:run        "bridge.end_round(tick, pool_patches, pool_max, total_cows,
                                   pressure, c0, c1, c2)"
"""

from __future__ import annotations

import csv
import json
import os
import re
import time
from collections import defaultdict, deque
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ── Load .env file from the project directory (if present) ───────────────────
# This lets API keys live in a local .env file rather than requiring system-wide
# environment variables — important because NetLogo's py: extension doesn't
# inherit variables from the terminal that launched it.
def _load_dotenv() -> None:
    """Load KEY=VALUE pairs from a .env file next to this module, if it exists."""
    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        return
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:   # don't override existing env vars
                os.environ[key] = value

_load_dotenv()

# ──────────────────────────────────────────────────────────────────────────────
# Module-level state (reset by configure())
# ──────────────────────────────────────────────────────────────────────────────
_cfg: Dict[str, Any] = {}
_client = None                        # LLM client object (institution detector / fallback)
_agent_clients: Dict[int, Any] = {}      # per-agent LLM client
_agent_backends_map: Dict[int, str] = {} # per-agent backend name
_agent_models_map: Dict[int, str] = {}   # per-agent model string
_agent_memory: Dict[int, deque] = {}  # rolling round summaries
_msg_buffer: Dict[int, List[str]] = defaultdict(list)   # incoming msgs / round
_msg_outbox: Dict[int, str] = {}      # outgoing msg this round
_log_handles: Dict[str, Tuple] = {}   # (file_handle, csv_writer)
_run_id: str = ""
_tick: int = 0
_round_messages: List[Dict] = []      # all messages this round (for institution detection)
_call_count: int = 0                  # total LLM calls (for rate-limit awareness)


# ──────────────────────────────────────────────────────────────────────────────
# SETUP
# ──────────────────────────────────────────────────────────────────────────────

def configure(
    backend: str = "anthropic",
    anthropic_model: str = "claude-sonnet-4-6",
    ollama_model: str = "llama3.2",
    agent_backends: list = None,
    agent_models: list = None,
    system_prompt_override: str = "",
    memory_length: int = 5,
    log_dir: str = "logs",
    run_id: Optional[str] = None,
    condition: str = "full-gabm",
    detect_institutions: bool = True,
    institution_every_n_ticks: int = 5,
    ollama_base_url: str = "http://localhost:11434/v1",
) -> str:
    """
    Initialise the bridge. Call once from NetLogo before the first tick.

    Parameters
    ----------
    backend : "anthropic" | "ollama"
    anthropic_model : Anthropic model string
    ollama_model    : Ollama model name (must be running locally)
    ollama_base_url : Base URL for Ollama's OpenAI-compatible endpoint
    memory_length   : Number of past rounds each agent remembers
    log_dir         : Directory for output CSVs
    run_id          : Unique run identifier (auto-generated if None)
    condition       : "baseline" | "full-gabm" | "hybrid"
    detect_institutions : Run secondary LLM institution classifier each round?
    institution_every_n_ticks : Run institution detection every N ticks (cost control)
    """
    global _cfg, _client, _agent_memory, _msg_buffer, _msg_outbox
    global _log_handles, _run_id, _tick, _round_messages, _call_count
    global _agent_clients, _agent_backends_map, _agent_models_map

    _cfg = dict(
        backend=str(backend),
        anthropic_model=str(anthropic_model),
        ollama_model=str(ollama_model),
        ollama_base_url=str(ollama_base_url).strip(),
        memory_length=int(memory_length),
        log_dir=str(log_dir),
        condition=str(condition),
        detect_institutions=bool(detect_institutions),
        institution_every_n_ticks=int(institution_every_n_ticks),
        system_prompt_override=str(system_prompt_override).strip(),
    )

    _run_id = run_id or datetime.now().strftime("%Y%m%d_%H%M%S") + f"_{condition}"
    _tick = 0
    _round_messages = []
    _call_count = 0

    # Reset per-agent state
    _agent_memory.clear()
    _msg_buffer.clear()
    _msg_outbox.clear()

    # Build per-agent client map
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "")
    openai_key    = os.environ.get("OPENAI_API_KEY", "")
    google_key    = os.environ.get("GOOGLE_API_KEY", "")
    n_agents = 3
    default_model = anthropic_model if backend == "anthropic" else ollama_model
    backends = list(agent_backends) if agent_backends else [backend] * n_agents
    models   = list(agent_models)   if agent_models   else [default_model] * n_agents

    _agent_clients.clear()
    _agent_backends_map.clear()
    _agent_models_map.clear()

    for i, (b, m) in enumerate(zip(backends, models)):
        b = str(b).strip().lower()
        m = str(m).strip()
        if b == "anthropic":
            import anthropic
            _agent_clients[i] = anthropic.Anthropic(api_key=anthropic_key)
        elif b == "openai":
            from openai import OpenAI
            _agent_clients[i] = OpenAI(api_key=openai_key)
        elif b == "google":
            import google.generativeai as genai
            genai.configure(api_key=google_key)
            _agent_clients[i] = genai.GenerativeModel(m)  # model baked into client
        elif b == "ollama-native":
            # Native Ollama /api/chat endpoint — required for thinking-format models
            # (e.g. gemma4) whose output is silently dropped by the OpenAI-compat shim.
            # No client object needed; requests are made directly in _call_llm.
            _agent_clients[i] = None
        else:  # ollama or any OpenAI-compatible local endpoint
            from openai import OpenAI
            _agent_clients[i] = OpenAI(base_url=str(ollama_base_url), api_key="ollama")
        _agent_backends_map[i] = b
        _agent_models_map[i]   = m

    # Default client for institution detector = agent 0's client
    _client = _agent_clients.get(0)

    # Initialise log files
    log_path = Path(log_dir) / _run_id
    log_path.mkdir(parents=True, exist_ok=True)
    _close_logs()
    _init_logs(log_path)

    return f"Bridge ready | run_id={_run_id} | backend={backend} | condition={condition}"


def init_agent(agent_id: int) -> None:
    """Register an LLM agent. Call for each LLM agent during NetLogo setup."""
    agent_id = int(agent_id)
    _agent_memory[agent_id] = deque(maxlen=_cfg.get("memory_length", 5))
    _msg_buffer[agent_id] = []
    _msg_outbox[agent_id] = ""


def log_params(params: dict) -> None:
    """
    Append arbitrary experiment parameters to run_meta.json.
    Call once after configure() with a dict of all slider/env values so every
    log folder is fully self-describing for reproducibility.
    """
    meta_path = Path(_cfg["log_dir"]) / _run_id / "run_meta.json"
    try:
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
        meta["experiment_params"] = {str(k): v for k, v in params.items()}
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)
    except Exception as exc:
        print(f"[log_params] Warning: could not write params to run_meta.json: {exc}")


# ──────────────────────────────────────────────────────────────────────────────
# DECISION — main entry point from NetLogo
# ──────────────────────────────────────────────────────────────────────────────

def decide_from_context(ctx: list) -> int:
    """
    Unpack a flat list passed from NetLogo via py:set and make a decision.

    ctx layout (20 elements, indices 0–19):
      [0]  agent_id          int
      [1]  tick              int
      [2]  pool_patches      int   (green patches remaining)
      [3]  pool_max          int   (total patches)
      [4]  own_herd          int   (ki)
      [5]  last_action       int   (-1 / 0 / 1)
      [6]  last_payoff       float
      [7]  neighbor_ids      list[int]
      [8]  neighbor_herds    list[int]
      [9]  neighbor_actions  list[int]
      [10] payoff_add        float  (estimated payoff if adding a cow)
      [11] payoff_keep       float  (estimated payoff if keeping herd)
      [12] payoff_remove     float  (estimated payoff if removing a cow)
      [13] fairness_me       float  (0-1 slider value)
      [14] fairness_others   float
      [15] coop_level        float
      [16] neg_recip         float
      [17] pos_recip         float
      [18] conformity        float
      [19] risk_aversion     float
    """
    global _tick, _call_count

    (agent_id, tick, pool_patches, pool_max,
     own_herd, last_action, last_payoff,
     neighbor_ids, neighbor_herds, neighbor_actions,
     payoff_add, payoff_keep, payoff_remove,
     fairness_me, fairness_others, coop_level,
     neg_recip, pos_recip, conformity, risk_aversion) = (
        int(ctx[0]), int(ctx[1]), int(ctx[2]), int(ctx[3]),
        int(ctx[4]), int(ctx[5]), float(ctx[6]),
        list(ctx[7]), list(ctx[8]), list(ctx[9]),
        float(ctx[10]), float(ctx[11]), float(ctx[12]),
        float(ctx[13]), float(ctx[14]), float(ctx[15]),
        float(ctx[16]), float(ctx[17]), float(ctx[18]), float(ctx[19]),
    )

    _tick = tick
    pool_pct = round(100.0 * pool_patches / max(pool_max, 1), 1)

    # Build context dict for prompt
    context = dict(
        agent_id=agent_id, tick=tick,
        pool_patches=pool_patches, pool_pct=pool_pct, pool_max=pool_max,
        own_herd=own_herd,
        last_action_name=_action_name(last_action),
        last_payoff=round(last_payoff, 3),
        neighbor_ids=[int(x) for x in neighbor_ids],
        neighbor_herds=[int(x) for x in neighbor_herds],
        neighbor_actions=[_action_name(int(x)) for x in neighbor_actions],
        payoff_add=round(payoff_add, 3),
        payoff_keep=round(payoff_keep, 3),
        payoff_remove=round(payoff_remove, 3),
        memory=list(_agent_memory.get(agent_id, [])),
        incoming_messages=list(_msg_buffer.get(agent_id, [])),
        personality=_describe_personality(
            fairness_me, fairness_others, coop_level,
            neg_recip, pos_recip, conformity, risk_aversion
        ),
    )

    # Call LLM
    system_prompt = _system_prompt()
    user_prompt = _user_prompt(context)
    response_text, thinking = _call_llm(system_prompt, user_prompt, agent_id=agent_id)
    _call_count += 1

    # Parse response
    action, message, reasoning = _parse_response(response_text)

    # Store outgoing message and log
    _msg_outbox[agent_id] = message
    _round_messages.append({
        "tick": tick, "agent_id": agent_id,
        "action": action, "action_name": _action_name(action),
        "message": message,
    })

    # Update rolling memory
    mem_entry = (
        f"Tick {tick}: pool={pool_pct}%, herd={own_herd}, "
        f"action={_action_name(action)}, payoff={round(last_payoff,2)}"
        + (f", said: \"{message[:40]}\"" if message.strip() else "")
    )
    _agent_memory[agent_id].append(mem_entry)

    # Logging
    _log_decision(
        tick, agent_id, action, message, reasoning, thinking, response_text,
        pool_pct, own_herd, payoff_add, payoff_keep, payoff_remove,
    )

    # Clear inbox for next round
    _msg_buffer[agent_id] = []

    return action


# ──────────────────────────────────────────────────────────────────────────────
# BASELINE BEST-RESPONSE (no LLM call — approximates Nash for control condition)
# ──────────────────────────────────────────────────────────────────────────────

def baseline_decide(ctx: list) -> int:
    """
    Myopic best-response heuristic for rule-based agents.
    Chooses the action with the highest expected payoff given others' last actions.
    Applies risk-aversion weighting consistent with the original MASTOC model.

    Uses the same ctx layout as decide_from_context().
    Returns action: -1 | 0 | 1
    """
    (agent_id, tick, pool_patches, pool_max,
     own_herd, last_action, last_payoff,
     neighbor_ids, neighbor_herds, neighbor_actions,
     payoff_add, payoff_keep, payoff_remove,
     fairness_me, fairness_others, coop_level,
     neg_recip, pos_recip, conformity, risk_aversion) = (
        int(ctx[0]), int(ctx[1]), int(ctx[2]), int(ctx[3]),
        int(ctx[4]), int(ctx[5]), float(ctx[6]),
        list(ctx[7]), list(ctx[8]), list(ctx[9]),
        float(ctx[10]), float(ctx[11]), float(ctx[12]),
        float(ctx[13]), float(ctx[14]), float(ctx[15]),
        float(ctx[16]), float(ctx[17]), float(ctx[18]), float(ctx[19]),
    )

    # Risk-aversion weighting: blend best-case with worst-case (cautious payoff)
    ra = float(risk_aversion)

    def cautious_payoff(p_best, p_worst_frac):
        """Higher risk_aversion → more weight on worst-case proportional payoff."""
        return (1 - ra) * p_best + ra * p_best * p_worst_frac

    # Proportional worst-case fractions (mirrors MASTOC generate-payoffs logic)
    total = abs(payoff_add) + abs(payoff_keep) + abs(payoff_remove)
    if total == 0:
        total = 1.0
    frac_add    = abs(payoff_add) / total
    frac_keep   = abs(payoff_keep) / total
    frac_remove = abs(payoff_remove) / total

    score_add    = cautious_payoff(payoff_add, frac_add)
    score_keep   = cautious_payoff(payoff_keep, frac_keep)
    score_remove = cautious_payoff(payoff_remove, frac_remove)

    best_action = max(
        [(-1, score_remove), (0, score_keep), (1, score_add)],
        key=lambda x: x[1],
    )[0]

    return best_action


# ──────────────────────────────────────────────────────────────────────────────
# COMMUNICATION
# ──────────────────────────────────────────────────────────────────────────────

def get_outgoing_message(agent_id: int) -> str:
    """Return the message this agent wants to send to neighbors this round."""
    return _msg_outbox.get(int(agent_id), "")


def deliver_message(from_agent_id: int, to_agent_id: int, message: str) -> None:
    """Deliver a message to an agent's inbox. Called from NetLogo per neighbor."""
    to_id = int(to_agent_id)
    if message and message.strip():
        label = f"Agent {int(from_agent_id)}: {message.strip()}"
        _msg_buffer[to_id].append(label)


# ──────────────────────────────────────────────────────────────────────────────
# END-OF-ROUND: resource logging + institution detection
# ──────────────────────────────────────────────────────────────────────────────

def end_round(
    tick: int,
    pool_patches: int,
    pool_max: int,
    total_cows: int,
    pressure: float,
    agent0_cows: int,
    agent1_cows: int,
    agent2_cows: int,
) -> str:
    """
    Call once at the end of each NetLogo tick.
    Logs resource state, runs institution detection (every N ticks), flushes logs.
    Returns a short status string.
    """
    tick = int(tick)
    pool_pct = round(100.0 * int(pool_patches) / max(int(pool_max), 1), 1)

    _log_resources(tick, pool_patches, pool_pct, total_cows, pressure,
                   agent0_cows, agent1_cows, agent2_cows)

    status = f"tick={tick} pool={pool_pct}% cows={total_cows}"

    # Institution detection
    every_n = _cfg.get("institution_every_n_ticks", 5)
    if _cfg.get("detect_institutions", True) and tick % every_n == 0:
        result = _detect_institutions(tick)
        score = result.get("institution_score", 0)
        status += f" inst_score={score}"

    # Clear round message buffer
    _round_messages.clear()

    _flush_logs()
    return status


# ──────────────────────────────────────────────────────────────────────────────
# INSTITUTION DETECTION
# ──────────────────────────────────────────────────────────────────────────────

def _detect_institutions(tick: int) -> dict:
    """
    Classify agent messages for Ostrom-style institutional signals.
    Categories:
      NORM_PROPOSAL  - proposing a rule or limit
      SANCTION       - threatening or criticising over-use
      COORDINATION   - non-binding call to coordinate
      DEFECTION      - announcing or justifying over-grazing
      TRUST_BUILDING - expressions of reciprocity / goodwill
      NONE           - no institutional content
    """
    messages = [m for m in _round_messages if m.get("message", "").strip()]
    if not messages:
        _log_institution_row(tick, 0, "", "No messages this round")
        return {}

    messages_text = "\n".join(
        f"Agent {m['agent_id']} ({m['action_name']}): {m['message']}"
        for m in messages
    )

    prompt = f"""You are a researcher studying commons governance. Analyse these round-{tick} messages:

{messages_text}

Classify each message for Ostrom-style institutional signals. Return ONLY valid JSON:
{{
  "messages": [
    {{
      "agent_id": <int>,
      "categories": ["NORM_PROPOSAL"|"SANCTION"|"COORDINATION"|"DEFECTION"|"TRUST_BUILDING"|"NONE"],
      "confidence": <0.0–1.0>,
      "excerpt": "<key phrase>"
    }}
  ],
  "round_summary": "<one sentence>",
  "institution_score": <0–10>
}}"""

    try:
        result_text, _ = _call_llm(
            "You are an expert analyst of common-pool resource governance.",
            prompt,
            max_tokens=600,
        )
        # Extract JSON from response
        m = re.search(r'\{.*\}', result_text, re.DOTALL)
        result = json.loads(m.group()) if m else {}
    except Exception as exc:
        result = {"error": str(exc), "institution_score": 0}

    score = result.get("institution_score", 0)
    cats: List[str] = []
    for item in result.get("messages", []):
        cats.extend(item.get("categories", []))
    summary = result.get("round_summary", "")

    _log_institution_row(tick, score, "|".join(sorted(set(cats))), summary)
    return result


# ──────────────────────────────────────────────────────────────────────────────
# LLM CALL
# ──────────────────────────────────────────────────────────────────────────────

def _call_llm(
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = 400,
    agent_id: int = None,
) -> Tuple[str, str]:
    """Dispatch to the appropriate LLM backend for this agent. Returns (response_text, reasoning)."""
    # Per-agent lookup; fall back to global _client for institution detector
    if agent_id is not None and agent_id in _agent_clients:
        backend = _agent_backends_map[agent_id]
        client  = _agent_clients[agent_id]
        model   = _agent_models_map[agent_id]
    else:
        backend = _agent_backends_map.get(0, _cfg.get("backend", "anthropic"))
        client  = _client
        model   = _agent_models_map.get(0,
                      _cfg.get("anthropic_model", "claude-sonnet-4-6")
                      if backend == "anthropic" else _cfg.get("ollama_model", "llama3.2"))

    if backend == "anthropic":
        import anthropic
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return response.content[0].text, ""

    elif backend == "google":
        # client is a google.generativeai.GenerativeModel with model already set
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        last_exc = None
        for attempt in range(4):  # up to 3 retries on rate-limit errors
            try:
                response = client.generate_content(
                    full_prompt,
                    generation_config={"max_output_tokens": max_tokens},
                )
                return response.text, ""
            except Exception as exc:
                last_exc = exc
                err_str = str(exc)
                is_rate_limit = (
                    "429" in err_str
                    or "quota" in err_str.lower()
                    or "ResourceExhausted" in type(exc).__name__
                )
                if is_rate_limit and attempt < 3:
                    # Try to extract retry_delay from error message
                    m = re.search(r'retry_delay\s*\{\s*seconds:\s*(\d+)', err_str)
                    wait = int(m.group(1)) + 2 if m else 15 * (attempt + 1)
                    agent_tag = f"agent {agent_id}" if agent_id is not None else "institution detector"
                    print(
                        f"[Google 429] Rate limit hit ({agent_tag}), "
                        f"waiting {wait}s (retry {attempt + 1}/3)…"
                    )
                    time.sleep(wait)
                else:
                    raise
        raise last_exc  # re-raise after exhausting retries

    elif backend == "ollama-native":
        # Use Ollama's native /api/chat endpoint directly.
        # The OpenAI-compat shim drops content for thinking-format models (e.g. gemma4);
        # the native endpoint returns it correctly, plus a separate "thinking" field.
        #
        # IMPORTANT: use stream=True so that the timeout applies per-chunk, not to
        # the entire response. Thinking-format models (gemma4, deepseek-r1) can
        # generate thousands of thinking tokens before the visible reply; with
        # stream=False Ollama buffers everything and the connection silently hangs
        # well past any reasonable read-timeout. Streaming keeps the socket alive
        # and lets us accumulate content as it arrives.
        import requests as _requests
        import json as _json
        native_base = _cfg.get("ollama_base_url", "http://localhost:11434").rstrip("/")
        if native_base.endswith("/v1"):
            native_base = native_base[:-3]
        resp = _requests.post(
            f"{native_base}/api/chat",
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "stream": True,
                "options": {"num_predict": max_tokens},
            },
            stream=True,
            timeout=300,
        )
        resp.raise_for_status()
        content = ""
        thinking = ""
        for raw_line in resp.iter_lines():
            if not raw_line:
                continue
            chunk = _json.loads(raw_line)
            msg = chunk.get("message", {})
            content  += msg.get("content",  "")
            thinking += msg.get("thinking", "")
            if chunk.get("done"):
                break
        return content, thinking

    else:
        # openai / ollama / any OpenAI-compatible endpoint
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content, ""


# ──────────────────────────────────────────────────────────────────────────────
# PROMPT BUILDING
# ──────────────────────────────────────────────────────────────────────────────

_DEFAULT_SYSTEM_PROMPT = (
    "You are a herder managing your cattle on a shared grassland commons.\n"
    "Each round you observe the pasture state and your neighbours' behaviour,\n"
    "then decide whether to ADD a cow (+1), KEEP your herd (0), or REMOVE a cow (-1).\n"
    "You may also send a short message to your neighbours (max 60 words).\n\n"
    "Respond ONLY in this exact JSON format — no preamble, no trailing text:\n"
    "{\n"
    '  "reasoning": "<2–3 sentences explaining your decision>",\n'
    '  "action": <-1|0|1>,\n'
    '  "message": "<optional message to neighbours, or empty string>"\n'
    "}"
)

def _system_prompt() -> str:
    override = _cfg.get("system_prompt_override", "").strip()
    return override if override else _DEFAULT_SYSTEM_PROMPT


def _user_prompt(ctx: dict) -> str:
    memory_lines = (
        "\n".join(f"  • {m}" for m in ctx["memory"])
        if ctx["memory"] else "  (no prior rounds recorded)"
    )
    msg_lines = (
        "\n".join(f"  • {m}" for m in ctx["incoming_messages"])
        if ctx["incoming_messages"] else "  (no messages received)"
    )
    neighbour_lines = "\n".join(
        f"  • Agent {nid}: {nh} cows, last action = {na}"
        for nid, nh, na in zip(
            ctx["neighbor_ids"], ctx["neighbor_herds"], ctx["neighbor_actions"]
        )
    )

    return f"""=== ROUND {ctx['tick']} — You are Agent {ctx['agent_id']} ===

COMMONS STATE
  Grassland remaining : {ctx['pool_patches']} patches  ({ctx['pool_pct']}% of total)
  Your herd size      : {ctx['own_herd']} cows
  Your last action    : {ctx['last_action_name']}
  Your last payoff    : {ctx['last_payoff']}

YOUR NEIGHBOURS
{neighbour_lines}

PAYOFF FORECAST  (expected payoff given current conditions)
  If you ADD a cow    : {ctx['payoff_add']}
  If you KEEP herd   : {ctx['payoff_keep']}
  If you REMOVE a cow : {ctx['payoff_remove']}

YOUR PERSONALITY
  {ctx['personality']}

YOUR MEMORY (last {len(ctx['memory'])} rounds)
{memory_lines}

MESSAGES RECEIVED THIS ROUND
{msg_lines}

What do you decide?"""


# ──────────────────────────────────────────────────────────────────────────────
# RESPONSE PARSING
# ──────────────────────────────────────────────────────────────────────────────

def _parse_response(text: str) -> Tuple[int, str, str]:
    """Parse LLM JSON response into (action, message, reasoning). Defaults to action=0 on failure."""
    # Try structured JSON
    try:
        m = re.search(r'\{.*\}', text, re.DOTALL)
        if m:
            obj = json.loads(m.group())
            action = int(obj.get("action", 0))
            action = max(-1, min(1, action))  # clamp
            message = str(obj.get("message", ""))[:200].strip()
            reasoning = str(obj.get("reasoning", "")).strip()
            return action, message, reasoning
    except Exception:
        pass

    # Fallback: find first standalone -1, 0, or 1
    # Log a warning so format failures are visible rather than silent
    print(f"[_parse_response] WARNING: JSON parse failed, falling back to regex. Raw response: {text[:200]!r}")
    nums = re.findall(r'(?<![0-9])(-1|0|1)(?![0-9])', text)
    action = int(nums[0]) if nums else 0
    return action, "", ""


# ──────────────────────────────────────────────────────────────────────────────
# PERSONALITY DESCRIPTION
# ──────────────────────────────────────────────────────────────────────────────

def _describe_personality(fm, fo, coop, neg_r, pos_r, conf, risk) -> str:
    traits = []
    if coop > 0.6:
        traits.append("cooperative — values collective outcomes over personal gain")
    elif coop < 0.3:
        traits.append("self-interested — focused primarily on personal profit")
    if fm > 0.5:
        traits.append("envious — bothered when others earn more than you")
    if fo > 0.5:
        traits.append("guilt-averse — uncomfortable earning much more than others")
    if pos_r > 0.5:
        traits.append("reciprocal — you reward neighbours who reduce their herds")
    if neg_r > 0.5:
        traits.append("retaliatory — you punish neighbours who expand their herds")
    if conf > 0.5:
        traits.append("conformist — you tend to follow the crowd's behaviour")
    if risk > 0.5:
        traits.append("risk-averse — you prefer safer outcomes over risky high payoffs")
    if not traits:
        traits.append("balanced — no strong socio-psychological biases")
    return "; ".join(traits)


def _action_name(a: int) -> str:
    return {1: "ADD", 0: "KEEP", -1: "REMOVE"}.get(int(a), str(a))


# ──────────────────────────────────────────────────────────────────────────────
# LOGGING
# ──────────────────────────────────────────────────────────────────────────────

def _init_logs(log_path: Path) -> None:
    global _log_handles

    # decisions.csv — one row per agent per tick
    d_path = log_path / "decisions.csv"
    dh = open(d_path, "w", newline="", encoding="utf-8")
    dw = csv.writer(dh)
    dw.writerow([
        "tick", "agent_id", "backend", "model",
        "action", "action_name", "message", "reasoning", "thinking", "raw_response",
        "pool_pct", "own_herd", "payoff_add", "payoff_keep", "payoff_remove",
    ])
    _log_handles["decisions"] = (dh, dw)

    # resources.csv — one row per tick
    r_path = log_path / "resources.csv"
    rh = open(r_path, "w", newline="", encoding="utf-8")
    rw = csv.writer(rh)
    rw.writerow([
        "tick", "pool_patches", "pool_pct", "total_cows", "pressure",
        "agent0_cows", "agent1_cows", "agent2_cows",
    ])
    _log_handles["resources"] = (rh, rw)

    # institutions.csv — one row per detection event
    i_path = log_path / "institutions.csv"
    ih = open(i_path, "w", newline="", encoding="utf-8")
    iw = csv.writer(ih)
    iw.writerow(["tick", "institution_score", "categories", "round_summary"])
    _log_handles["institutions"] = (ih, iw)

    # Write run metadata
    meta_path = log_path / "run_meta.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump({
            "run_id": _run_id,
            "condition": _cfg.get("condition"),
            "agent_models": [
                {"backend": _agent_backends_map.get(i, "?"),
                 "model":   _agent_models_map.get(i, "?")}
                for i in range(3)
            ],
            "memory_length": _cfg.get("memory_length"),
            "started_at": datetime.now().isoformat(),
        }, f, indent=2)


def _log_decision(tick, agent_id, action, message, reasoning, thinking, raw_response,
                  pool_pct, own_herd, p_add, p_keep, p_remove) -> None:
    _, dw = _log_handles.get("decisions", (None, None))
    if dw:
        backend = _agent_backends_map.get(agent_id, "?")
        model   = _agent_models_map.get(agent_id, "?")
        dw.writerow([
            tick, agent_id, backend, model,
            action, _action_name(action), message, reasoning, thinking, raw_response,
            pool_pct, own_herd, round(p_add, 3), round(p_keep, 3), round(p_remove, 3),
        ])


def _log_resources(tick, pool_patches, pool_pct, total_cows, pressure,
                   c0, c1, c2) -> None:
    _, rw = _log_handles.get("resources", (None, None))
    if rw:
        rw.writerow([tick, pool_patches, pool_pct, total_cows,
                     round(float(pressure), 4), c0, c1, c2])


def _log_institution_row(tick, score, categories, summary) -> None:
    _, iw = _log_handles.get("institutions", (None, None))
    if iw:
        iw.writerow([tick, score, categories, summary])


def _flush_logs() -> None:
    for fh, _ in _log_handles.values():
        try:
            fh.flush()
        except Exception:
            pass


def _close_logs() -> None:
    for fh, _ in _log_handles.values():
        try:
            fh.close()
        except Exception:
            pass
    _log_handles.clear()


def close() -> str:
    """Call at end of simulation to flush and close all logs."""
    _flush_logs()
 