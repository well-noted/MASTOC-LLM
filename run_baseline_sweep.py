"""
run_baseline_sweep.py
=====================
Batch sweep runner for MASTOC-LLM.

Supports all three conditions:
  baseline   — rule-based agents, no API calls, fast
  full-gabm  — all 3 agents use an LLM
  hybrid     — N agents use an LLM, the rest are rule-based

For LLM conditions, a cost estimate is printed and you must confirm before
any NetLogo process (or API call) is launched.  Pass --yes to skip the
prompt (useful for scripted pipelines).

Pass --stop-on-collapse to end each run as soon as grassland drops below 5 %
instead of running to --ticks.

Usage examples
--------------
  # 30 baseline runs, default psychosocial params
  python run_baseline_sweep.py

  # Vary neg-r and cooperation across a 3×3 grid (baseline)
  python run_baseline_sweep.py --runs 20 --neg-r 0.5 --coop 0.5

  # 10 full-gabm runs with Claude Sonnet — shows cost estimate first
  python run_baseline_sweep.py --condition full-gabm --runs 10 --backend anthropic --llm-model claude-sonnet-4-6

  # Hybrid: 1 LLM agent, 2 rule-based, using a local Ollama model (free)
  python run_baseline_sweep.py --condition hybrid --num-llm-agents 1 --backend ollama --llm-model llama3

  # Stop each run as soon as the commons collapses
  python run_baseline_sweep.py --condition full-gabm --runs 5 --stop-on-collapse
"""

from __future__ import annotations

import argparse
import ctypes
import os
import re
import subprocess
import sys
import textwrap
from pathlib import Path


# ─── Pricing table (USD per million tokens, May 2026) ────────────────────────
# { model_id: (input_per_M_usd, output_per_M_usd) }
PRICING: dict[str, tuple[float, float]] = {
    # Anthropic
    "claude-opus-4-6":              (15.00, 75.00),
    "claude-sonnet-4-6":            ( 3.00, 15.00),
    "claude-haiku-4-5":             ( 0.25,  1.25),
    "claude-haiku-4-5-20251001":    ( 0.25,  1.25),
    # OpenAI
    "gpt-4o":                       ( 2.50, 10.00),
    "gpt-4o-mini":                  ( 0.15,  0.60),
    "gpt-4-turbo":                  (10.00, 30.00),
    "gpt-3.5-turbo":                ( 0.50,  1.50),
    # Google (via Ollama or API — list common ones)
    "gemma2:27b":                   ( 0.00,  0.00),
    "gemma3:27b":                   ( 0.00,  0.00),
    # Ollama local models (always free — matched by backend, not model name)
}

# Token estimates per LLM call, based on observed MASTOC-LLM bridge logs.
# Input grows with memory_length (each stored round ≈ 55 tokens).
# Output is stable: JSON with action + reasoning + message.
_BASE_INPUT_TOKENS  = 480
_PER_MEMORY_TOKENS  =  55
_BASE_OUTPUT_TOKENS = 155
_OUTPUT_TOKEN_HIGH  = 220   # upper bound for range display


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _short_path(p: "Path | str") -> str:
    """8.3 short path so Java never sees a space in Program Files."""
    if os.name != "nt":
        return str(p)
    try:
        buf = ctypes.create_unicode_buffer(32768)
        if ctypes.windll.kernel32.GetShortPathNameW(str(p), buf, 32768):
            return buf.value
    except Exception:
        pass
    return str(p)


def _find_netlogo(hint: "str | None") -> Path:
    candidates = []
    if hint:
        candidates.append(Path(hint))
    if os.name == "nt":
        for base in [r"C:\Program Files", r"C:\Program Files (x86)"]:
            p = Path(base)
            if p.exists():
                for d in sorted(p.iterdir(), reverse=True):
                    if d.name.lower().startswith("netlogo"):
                        candidates.append(d)
    for c in candidates:
        if (c / "netlogo-headless.bat").exists() or (c / "netlogo-headless.sh").exists():
            return c
    sys.exit(
        "Could not find NetLogo. Pass --netlogo-path, e.g.:\n"
        '  python run_baseline_sweep.py --netlogo-path "C:/Program Files/NetLogo 7.0.4"'
    )


def _find_java(netlogo_dir: Path) -> str:
    for rel in ["jdk/bin/java.exe", "runtime/bin/java.exe",
                "jdk/bin/java",    "runtime/bin/java"]:
        c = netlogo_dir / rel
        if c.exists():
            return _short_path(c)
    java_home = os.environ.get("JAVA_HOME")
    if java_home:
        c = Path(java_home) / "bin" / "java.exe"
        if c.exists():
            return _short_path(c)
    return "java"


def _find_netlogo_jar(netlogo_dir: Path) -> Path:
    jars = sorted((netlogo_dir / "app").glob("netlogo-*.jar"))
    if not jars:
        sys.exit(f"No netlogo-*.jar found under {netlogo_dir / 'app'}")
    return jars[-1]


def _find_extensions_dir(netlogo_dir: Path) -> str:
    dirs: list[str] = []

    def _add(p: Path) -> None:
        if p.exists() and str(p) not in dirs:
            dirs.append(_short_path(p))

    _add(netlogo_dir / "extensions")
    user_profile = Path(os.environ.get("USERPROFILE", ""))
    if user_profile.exists():
        docs = user_profile / "Documents"
        if docs.exists():
            for d in docs.iterdir():
                if d.is_dir() and d.name.lower().startswith("netlogo"):
                    _add(d / "extensions")
        appdata = Path(os.environ.get("APPDATA", ""))
        if appdata.exists():
            _add(appdata / "NetLogo" / "extensions")

    found = ";".join(dirs)
    py_found = any(
        (Path(d.replace("\\", "/")) / "py").exists() or (Path(d) / "py").exists()
        for d in dirs
    )
    if not py_found:
        print(f"WARNING: 'py' extension not found in: {dirs}")
    return found


# ─── Cost estimation ─────────────────────────────────────────────────────────

def _estimate_cost(
    runs: int,
    ticks: int,
    memory_length: int,
    n_llm_agents: int,
    backend: str,
    llm_model: str,
    stop_on_collapse: bool,
) -> None:
    """
    Print a cost estimate and prompt for confirmation.
    Returns normally if user confirms; calls sys.exit() if they decline.
    Skipped entirely for baseline condition (no API calls).
    """
    # Local backends are always free — skip cost check
    if backend == "ollama":
        print(f"  Backend: ollama (local) — no API charges.")
        print()
        return

    # Effective ticks may be lower if stop-on-collapse is on
    effective_ticks = ticks
    if stop_on_collapse:
        effective_ticks = int(ticks * 0.6)   # rough mid-point estimate
        ticks_note = f"~{effective_ticks} (collapse cutoff active; full run = {ticks})"
    else:
        ticks_note = str(ticks)

    total_calls = runs * effective_ticks * n_llm_agents

    input_tokens_per_call  = _BASE_INPUT_TOKENS + memory_length * _PER_MEMORY_TOKENS
    output_tokens_lo = _BASE_OUTPUT_TOKENS
    output_tokens_hi = _OUTPUT_TOKEN_HIGH

    total_input_lo  = total_calls * input_tokens_per_call
    total_output_lo = total_calls * output_tokens_lo
    total_output_hi = total_calls * output_tokens_hi

    # Pricing
    if llm_model in PRICING:
        price_in, price_out = PRICING[llm_model]
        known = True
    else:
        # Unknown model — warn and use rough mid-tier estimate
        price_in, price_out = 3.00, 15.00
        known = False

    cost_lo = (total_input_lo / 1_000_000) * price_in + (total_output_lo / 1_000_000) * price_out
    cost_hi = (total_input_lo / 1_000_000) * price_in + (total_output_hi / 1_000_000) * price_out

    print()
    print("  ┌─────────────────────────────────────────────────┐")
    print("  │              API COST ESTIMATE                  │")
    print("  ├─────────────────────────────────────────────────┤")
    print(f"  │  Model          : {llm_model:<30} │")
    print(f"  │  LLM agents/tick: {n_llm_agents:<30} │")
    print(f"  │  Runs × ticks   : {runs} × {ticks_note:<23} │")
    print(f"  │  Total API calls : {total_calls:>6,}                        │")
    print(f"  │  Input  tokens  : ~{total_input_lo / 1_000_000:>5.1f}M                       │")
    print(f"  │  Output tokens  : ~{total_output_lo/1_000_000:.1f}M – {total_output_hi/1_000_000:.1f}M                 │")
    if not known:
        print(f"  │  ⚠ Pricing unknown — using $3/$15 per M estimate  │")
    print(f"  │  Input  @ ${price_in:.2f}/M : ${(total_input_lo/1_000_000)*price_in:>7.2f}                     │")
    print(f"  │  Output @ ${price_out:.2f}/M : ${(total_output_lo/1_000_000)*price_out:.2f} – ${(total_output_hi/1_000_000)*price_out:.2f}               │")
    print(f"  │                                                 │")
    print(f"  │  ESTIMATED TOTAL : ${cost_lo:.2f} – ${cost_hi:.2f}             │")
    print("  └─────────────────────────────────────────────────┘")
    print()

    answer = input("  Proceed? [y/N] ").strip().lower()
    if answer not in ("y", "yes"):
        print("Aborted.")
        sys.exit(0)
    print()


# ─── BehaviorSpace XML builder ────────────────────────────────────────────────

def _build_experiment_xml(args: argparse.Namespace) -> str:
    """Return a single <experiment> XML block to inject into the .nlogox."""

    grassland_values_xml = "\n          ".join(
        f'<value value="{g}"></value>'
        for g in [int(g.strip()) for g in args.grassland.split(",")]
    )

    # Stop condition (optional)
    exit_condition_xml = ""
    if args.stop_on_collapse:
        exit_condition_xml = (
            "\n  <exitCondition>"
            "count patches with [pcolor = green - 2] &lt; (max-patches * 0.05)"
            "</exitCondition>"
        )

    # For LLM conditions, run repetitions sequentially to avoid hammering the API
    sequential = "true" if args.condition != "baseline" else "false"

    # Agent backend/model blocks
    agent_blocks = ""
    for i in range(3):
        if args.condition == "baseline":
            backend = "anthropic"          # irrelevant in baseline — never called
            model   = "claude-sonnet-4-6"  # irrelevant
        else:
            backend = args.backend
            model   = args.llm_model
        agent_blocks += f"""\
            <enumeratedValueSet variable="agent{i}-backend">
              <value value="&quot;{backend}&quot;"></value>
            </enumeratedValueSet>
            <enumeratedValueSet variable="agent{i}-model">
              <value value="&quot;{model}&quot;"></value>
            </enumeratedValueSet>
"""

    return textwrap.dedent(f"""\
        <experiment name="baseline-sweep"
                    repetitions="{args.runs}"
                    sequentialRunOrder="{sequential}"
                    runMetricsEveryStep="true"
                    timeLimit="{args.ticks}">{exit_condition_xml}
          <setup>setup</setup>
          <go>simulation</go>
          <metrics>
            <metric>count patches with [pcolor = green - 2]</metric>
            <metric>count cows</metric>
            <metric>pressure</metric>
            <metric>count cows with [owner = human 0]</metric>
            <metric>count cows with [owner = human 1]</metric>
            <metric>count cows with [owner = human 2]</metric>
          </metrics>
          <constants>
            <enumeratedValueSet variable="condition">
              <value value="&quot;{args.condition}&quot;"></value>
            </enumeratedValueSet>
            <enumeratedValueSet variable="num-llm-agents">
              <value value="{args.num_llm_agents}"></value>
            </enumeratedValueSet>
            <enumeratedValueSet variable="cow-forage-requirement">
              <value value="{args.forage}"></value>
            </enumeratedValueSet>
            <enumeratedValueSet variable="initial-grassland">
              {grassland_values_xml}
            </enumeratedValueSet>
            <enumeratedValueSet variable="initial-grass-growth-rate">
              <value value="{args.growth_rate}"></value>
            </enumeratedValueSet>
            <enumeratedValueSet variable="cooperation-level">
              <value value="{args.coop}"></value>
            </enumeratedValueSet>
            <enumeratedValueSet variable="negative-reciprocity">
              <value value="{args.neg_r}"></value>
            </enumeratedValueSet>
            <enumeratedValueSet variable="positive-reciprocity">
              <value value="{args.pos_r}"></value>
            </enumeratedValueSet>
            <enumeratedValueSet variable="risk-aversion-level">
              <value value="{args.risk}"></value>
            </enumeratedValueSet>
            <enumeratedValueSet variable="fairness-concerning-me">
              <value value="{args.fairness_me}"></value>
            </enumeratedValueSet>
            <enumeratedValueSet variable="fairness-concerning-others">
              <value value="{args.fairness_oth}"></value>
            </enumeratedValueSet>
            <enumeratedValueSet variable="conformity-level">
              <value value="0"></value>
            </enumeratedValueSet>
            <enumeratedValueSet variable="memory-length">
              <value value="{args.memory_length}"></value>
            </enumeratedValueSet>
            <enumeratedValueSet variable="detect-institutions">
              <value value="true"></value>
            </enumeratedValueSet>
            <enumeratedValueSet variable="institution-check-interval">
              <value value="5"></value>
            </enumeratedValueSet>
            {agent_blocks.strip()}
            <enumeratedValueSet variable="ollama-base-url">
              <value value="&quot;{args.ollama_url}&quot;"></value>
            </enumeratedValueSet>
            <enumeratedValueSet variable="system-prompt-override">
              <value value="&quot;&quot;"></value>
            </enumeratedValueSet>
          </constants>
        </experiment>""")


def _inject_experiment(model_content: str, experiment_xml: str) -> str:
    model_content = re.sub(
        r'\s*<experiment name="baseline-sweep".*?</experiment>',
        "",
        model_content,
        flags=re.DOTALL,
    )
    indented = "\n".join("    " + line for line in experiment_xml.splitlines())
    if "</experiments>" not in model_content:
        sys.exit("Could not find </experiments> in the model file.")
    return model_content.replace(
        "</experiments>",
        f"{indented}\n  </experiments>",
        1,
    )


# ─── Runner ──────────────────────────────────────────────────────────────────

def run(args: argparse.Namespace) -> None:
    netlogo_dir = _find_netlogo(args.netlogo_path)
    model_path  = Path(args.model).resolve()
    if not model_path.exists():
        sys.exit(f"Model file not found: {model_path}")

    grassland_values = [int(g.strip()) for g in args.grassland.split(",")]
    total_runs = args.runs * len(grassland_values)

    # Determine how many agents will call the LLM
    if args.condition == "baseline":
        n_llm_agents = 0
    elif args.condition == "full-gabm":
        n_llm_agents = 3
    else:  # hybrid
        n_llm_agents = args.num_llm_agents

    print()
    print("Sweep plan:")
    print(f"  Condition        : {args.condition}")
    if args.condition != "baseline":
        print(f"  Backend          : {args.backend}")
        print(f"  LLM model        : {args.llm_model}")
        print(f"  LLM agents/tick  : {n_llm_agents}")
    print(f"  Runs             : {args.runs}  ×  grassland={grassland_values}  =  {total_runs} total")
    print(f"  Ticks per run    : {args.ticks}")
    print(f"  Stop on collapse : {'yes (<5% grassland)' if args.stop_on_collapse else 'no'}")
    print(f"  coop={args.coop}  neg_r={args.neg_r}  pos_r={args.pos_r}  "
          f"risk={args.risk}  fair_me={args.fairness_me}  fair_oth={args.fairness_oth}")
    print(f"  Model file       : {model_path}")
    print(f"  NetLogo          : {netlogo_dir}")

    # ── Cost estimate & confirmation (LLM conditions only) ───────────────────
    if args.condition != "baseline" and not args.yes:
        _estimate_cost(
            runs=total_runs,
            ticks=args.ticks,
            memory_length=args.memory_length,
            n_llm_agents=n_llm_agents,
            backend=args.backend,
            llm_model=args.llm_model,
            stop_on_collapse=args.stop_on_collapse,
        )
    elif args.condition != "baseline" and args.yes:
        print("  (--yes flag set — skipping cost confirmation)")
    print()

    # ── Build the patched model ───────────────────────────────────────────────
    experiment_xml  = _build_experiment_xml(args)
    original_content = model_path.read_text(encoding="utf-8")
    patched_content  = _inject_experiment(original_content, experiment_xml)

    tmp_model = model_path.with_name("_baseline_sweep_tmp.nlogox")
    tmp_model.write_text(patched_content, encoding="utf-8")
    print(f"Temp model: {tmp_model}")

    table_path = model_path.parent / "baseline_sweep_table.csv"

    # ── Java command ─────────────────────────────────────────────────────────
    java_exe = _find_java(netlogo_dir)
    nl_jar   = _find_netlogo_jar(netlogo_dir)
    s_nl     = _short_path(netlogo_dir)
    ext_dirs = _find_extensions_dir(netlogo_dir)
    print(f"Extensions: {ext_dirs}")

    cmd = [
        java_exe,
        "-XX:MaxRAMPercentage=50",
        "-Dfile.encoding=UTF-8",
        f"-Dnetlogo.docs.dir={s_nl}",
        f"-Dnetlogo.models.dir={s_nl}models",
        f"-Dnetlogo.extensions.dir={ext_dirs}",
        "--add-exports=java.base/java.lang=ALL-UNNAMED",
        "--add-exports=java.desktop/sun.awt=ALL-UNNAMED",
        "--add-exports=java.desktop/sun.java2d=ALL-UNNAMED",
        "-classpath", _short_path(nl_jar),
        "org.nlogo.headless.Main",
        "--model",      str(tmp_model),
        "--experiment", "baseline-sweep",
        "--table",      str(table_path),
    ]

    # For LLM conditions, force single-threaded to avoid concurrent API calls
    if args.condition != "baseline":
        cmd += ["--threads", "1"]

    print(f"Launching NetLogo headless ({args.condition})...\n")
    print("=" * 60)

    try:
        result = subprocess.run(cmd, check=False)
        print("=" * 60)
        if result.returncode == 0:
            print(f"\nDone.")
            print(f"  BehaviorSpace table : {table_path}")
            print(f"  Per-run logs        : {model_path.parent / 'logs'}")
        else:
            print(f"\nNetLogo exited with code {result.returncode}.")
    except KeyboardInterrupt:
        print("\nInterrupted.")
    finally:
        tmp_model.unlink(missing_ok=True)
        print("Temp model cleaned up.")


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main() -> None:
    p = argparse.ArgumentParser(
        description="Batch sweep runner for MASTOC-LLM (baseline, full-gabm, hybrid).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              python run_baseline_sweep.py --runs 30
              python run_baseline_sweep.py --runs 20 --neg-r 0.5 --coop 0.5
              python run_baseline_sweep.py --condition full-gabm --runs 5 --backend anthropic --llm-model claude-sonnet-4-6
              python run_baseline_sweep.py --condition hybrid --num-llm-agents 1 --backend ollama --llm-model llama3 --stop-on-collapse
        """),
    )

    # ── Condition ──────────────────────────────────────────────────────────
    p.add_argument("--condition", choices=["baseline", "full-gabm", "hybrid"],
                   default="baseline",
                   help="Agent condition. Default: baseline")
    p.add_argument("--backend", choices=["anthropic", "openai", "ollama"],
                   default="anthropic",
                   help="LLM backend (full-gabm / hybrid only). Default: anthropic")
    p.add_argument("--llm-model", dest="llm_model", default="claude-sonnet-4-6",
                   help="LLM model name. Default: claude-sonnet-4-6")
    p.add_argument("--num-llm-agents", dest="num_llm_agents", type=int,
                   default=1, choices=[1, 2, 3],
                   help="Number of LLM agents in hybrid mode. Default: 1")

    # ── Run parameters ─────────────────────────────────────────────────────
    p.add_argument("--runs",    type=int,   default=30,
                   help="Repetitions per parameter combo. Default: 30")
    p.add_argument("--ticks",   type=int,   default=120,
                   help="Max ticks per run. Default: 120")
    p.add_argument("--stop-on-collapse", dest="stop_on_collapse",
                   action="store_true",
                   help="End each run early when grassland drops below 5%%.")
    p.add_argument("--yes", "-y", action="store_true",
                   help="Skip cost confirmation prompt (for scripting).")

    # ── Physical parameters ────────────────────────────────────────────────
    p.add_argument("--grassland",   type=str,   default="100",
                   help="Initial grassland %% (single value or comma list). Default: 100")
    p.add_argument("--forage",      type=float, default=2.0,
                   help="Cow forage requirement. Default: 2")
    p.add_argument("--growth-rate", type=float, default=0.001, dest="growth_rate",
                   help="Grass growth rate. Default: 0.001")
    p.add_argument("--memory-length", type=int, default=5, dest="memory_length",
                   help="Agent memory length (ticks). Default: 5")

    # ── Psychosocial parameters ────────────────────────────────────────────
    p.add_argument("--coop",        type=float, default=1.0,
                   help="Cooperation level. Default: 1.0")
    p.add_argument("--neg-r",       type=float, default=0.0, dest="neg_r",
                   help="Negative reciprocity. Default: 0.0")
    p.add_argument("--pos-r",       type=float, default=1.0, dest="pos_r",
                   help="Positive reciprocity. Default: 1.0")
    p.add_argument("--risk",        type=float, default=1.0,
                   help="Risk aversion. Default: 1.0")
    p.add_argument("--fairness-me", type=float, default=0.0, dest="fairness_me",
                   help="Fairness concerning me. Default: 0.0")
    p.add_argument("--fairness-oth",type=float, default=1.0, dest="fairness_oth",
                   help="Fairness concerning others. Default: 1.0")

    # ── Paths & endpoints ──────────────────────────────────────────────────
    p.add_argument("--model",        type=str, default="MASTOC-LLM.nlogox",
                   help="Path to .nlogox model file. Default: MASTOC-LLM.nlogox")
    p.add_argument("--netlogo-path", type=str, default=None, dest="netlogo_path",
                   help='NetLogo install dir. Default: auto-detect')
    p.add_argument("--ollama-url",   type=str, default="http://localhost:11434/v1",
                   dest="ollama_url",
                   help="Ollama base URL. Default: http://localhost:11434/v1")

    args = p.parse_args()
    run(args)


if __name__ == "__main__":
    main()
