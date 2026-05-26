#!/usr/bin/env python3
"""
inspect_logs.py -- MASTOC-LLM log reader

Usage:
    python inspect_logs.py                    # print full run index to terminal
    python inspect_logs.py --md               # also write index to logs/index.md
    python inspect_logs.py --run <run_id>     # drill down into a single run
    python inspect_logs.py --run <run_id> --md  # drill-down + write to logs/<run_id>.md
    python inspect_logs.py --model gpt-5.5    # filter index to one model
    python inspect_logs.py --collapse         # filter to collapsed runs only
    python inspect_logs.py --survived         # filter to survived runs only

The run_id can be a full folder name (20260515_233233_full-gabm) or a prefix.
"""

import os
import sys
import json
import csv
import argparse
import textwrap
from collections import Counter, defaultdict
from datetime import datetime

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR   = os.path.join(SCRIPT_DIR, "logs")


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_meta(run_dir):
    path = os.path.join(run_dir, "run_meta.json")
    if not os.path.exists(path):
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def load_csv(run_dir, filename):
    path = os.path.join(run_dir, filename)
    if not os.path.exists(path):
        return []
    try:
        with open(path, encoding="utf-8") as f:
            return list(csv.DictReader(f))
    except Exception:
        return []


def infer_model(decisions, meta):
    """Best-effort model name from decisions rows or meta."""
    if decisions:
        m = decisions[0].get("model", "")
        if m and m not in ("model", "?", ""):
            return m
    # Newer meta format
    am = meta.get("agent_models", [])
    if am and isinstance(am, list):
        m = am[0].get("model", "") if am else ""
        if m:
            return m
    # Old meta format
    return meta.get("model", "?") or "?"


def infer_condition(folder_name, meta):
    cond = meta.get("condition", "")
    if cond:
        return cond
    for c in ("full-gabm", "hybrid", "baseline"):
        if c in folder_name:
            return c
    return "?"


def get_experiment_params(meta):
    """Return experiment_params dict, falling back to top-level keys."""
    ep = meta.get("experiment_params", {}) or {}
    return ep


def action_counts(decisions):
    return Counter(r.get("action_name", r.get("action", "?")) for r in decisions)


def resource_summary(resources):
    """Return dict with collapse, collapse_tick, final_pool, final_ticks, final_herds."""
    if not resources:
        return dict(collapse=None, collapse_tick=None, final_pool=None,
                    final_ticks=0, final_herds=None, peak_herd=None)

    final = resources[-1]
    try:
        final_pool = float(final.get("pool_pct", 0) or 0)
    except ValueError:
        final_pool = None

    collapse = (final_pool == 0.0) if final_pool is not None else None
    final_ticks = len(resources)

    # Find first tick where pool hit 0
    collapse_tick = None
    if collapse:
        for row in resources:
            try:
                if float(row.get("pool_pct", 1) or 1) == 0.0:
                    collapse_tick = int(row.get("tick", 0))
                    break
            except ValueError:
                pass

    # Final herds
    try:
        final_herds = (
            int(final.get("agent0_cows") or 0),
            int(final.get("agent1_cows") or 0),
            int(final.get("agent2_cows") or 0),
        )
    except (ValueError, TypeError):
        final_herds = None

    # Peak total herd
    peak_herd = 0
    for row in resources:
        try:
            tc = int(row.get("total_cows") or 0)
            if tc > peak_herd:
                peak_herd = tc
        except ValueError:
            pass

    return dict(
        collapse=collapse,
        collapse_tick=collapse_tick,
        final_pool=final_pool,
        final_ticks=final_ticks,
        final_herds=final_herds,
        peak_herd=peak_herd,
    )


def load_run(folder_name):
    """Load everything for one run folder. Returns a dict."""
    run_dir   = os.path.join(LOGS_DIR, folder_name)
    meta      = load_meta(run_dir)
    decisions = load_csv(run_dir, "decisions.csv")
    resources = load_csv(run_dir, "resources.csv")
    insts     = load_csv(run_dir, "institutions.csv")

    model     = infer_model(decisions, meta)
    condition = infer_condition(folder_name, meta)
    ep        = get_experiment_params(meta)
    acts      = action_counts(decisions)
    res_sum   = resource_summary(resources)

    return dict(
        folder=folder_name,
        run_id=meta.get("run_id", folder_name),
        label=meta.get("label", ""),
        condition=condition,
        model=model,
        meta=meta,
        ep=ep,
        decisions=decisions,
        resources=resources,
        institutions=insts,
        acts=acts,
        **res_sum,
    )


def all_runs(filter_model=None, filter_collapse=None):
    """Yield run dicts for every folder that has decision data."""
    if not os.path.isdir(LOGS_DIR):
        print(f"ERROR: logs directory not found at {LOGS_DIR}", file=sys.stderr)
        sys.exit(1)

    folders = sorted(
        f for f in os.listdir(LOGS_DIR)
        if os.path.isdir(os.path.join(LOGS_DIR, f))
    )

    for folder in folders:
        dec_path = os.path.join(LOGS_DIR, folder, "decisions.csv")
        if not os.path.exists(dec_path):
            continue
        # Must have at least one data row
        try:
            with open(dec_path, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                first = next(reader, None)
            if first is None:
                continue
        except Exception:
            continue

        run = load_run(folder)

        if filter_model and filter_model.lower() not in run["model"].lower():
            continue
        if filter_collapse is True and not run["collapse"]:
            continue
        if filter_collapse is False and run["collapse"] is not False:
            continue

        yield run


def find_run(run_id_prefix):
    """Find a run folder by full name or prefix."""
    for folder in sorted(os.listdir(LOGS_DIR)):
        if folder == run_id_prefix or folder.startswith(run_id_prefix):
            dec_path = os.path.join(LOGS_DIR, folder, "decisions.csv")
            if os.path.exists(dec_path):
                return folder
    return None


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def fmt_pool(pool):
    if pool is None:
        return "  ?"
    return f"{pool:5.1f}%"


def fmt_acts(acts):
    parts = []
    for name in ("ADD", "KEEP", "REMOVE"):
        v = acts.get(name, 0)
        if v:
            parts.append(f"{name}:{v}")
    return "  ".join(parts) if parts else "—"


def fmt_herds(herds):
    if herds is None:
        return "?"
    return "/".join(str(h) for h in herds)


def fmt_param(ep, key, default="?"):
    v = ep.get(key, default)
    if v == default or v is None:
        return str(default)
    if isinstance(v, float):
        return f"{v:.2f}"
    return str(v)


def outcome_str(run):
    if run["collapse"]:
        tick = run["collapse_tick"] or "?"
        return f"COLLAPSE t{tick}"
    elif run["collapse"] is False:
        return f"survived  t{run['final_ticks']}"
    return "unknown"


def shorten_model(model):
    replacements = {
        "claude-sonnet-4-6": "Sonnet 4.6",
        "claude-haiku-4-5": "Haiku 4.5",
        "claude-haiku-4-5-20251001": "Haiku 4.5",
        "gpt-5.5": "gpt-5.5",
        "gpt-5.4-mini": "gpt-5.4-mini",
        "gpt-4o-mini": "gpt-4o-mini",
        "deepseek-r1:32b": "DeepSeek R1:32b",
        "gemma4:e4b": "gemma4:e4b",
        "llama3.2:3b-instruct-q4_0": "Llama 3.2 3B",
        "llama3.2:3b": "Llama 3.2 3B",
    }
    return replacements.get(model, model[:18])


# ---------------------------------------------------------------------------
# Index table
# ---------------------------------------------------------------------------

INDEX_HEADER = (
    f"{'RUN ID':<34} {'MODEL':<16} {'COND':<10} "
    f"{'COOP':>4} {'MEM':>3} {'COM':>3} {'GRASS':>5} "
    f"{'OUTCOME':<16} {'POOL%':>6} {'ACTIONS'}"
)
INDEX_SEP = "-" * 120


def run_index_row(run):
    ep   = run["ep"]
    coop = fmt_param(ep, "cooperation_level", "?")
    mem  = fmt_param(ep, "memory_length", run["meta"].get("memory_length", "?"))
    comm = ep.get("communication", run["meta"].get("communication", "?"))
    comm_str = "on" if comm is True else ("off" if comm is False else str(comm)[:3])
    grass = fmt_param(ep, "initial_grassland", "?")
    pool  = fmt_pool(run["final_pool"])
    acts  = fmt_acts(run["acts"])
    model = shorten_model(run["model"])
    cond  = run["condition"][:9]
    out   = outcome_str(run)

    return (
        f"{run['folder']:<34} {model:<16} {cond:<10} "
        f"{coop:>4} {str(mem):>3} {comm_str:>3} {str(grass):>5} "
        f"{out:<16} {pool:>6}  {acts}"
    )


def print_index(runs, out_lines=None):
    """Print run index. If out_lines is a list, append to it too."""
    def emit(line):
        print(line)
        if out_lines is not None:
            out_lines.append(line)

    # Group by model for readability
    by_model = defaultdict(list)
    for r in runs:
        by_model[r["model"]].append(r)

    total = sum(len(v) for v in by_model.values())
    emit(f"\nMASTOC-LLM Run Index  --  {total} runs with data  "
         f"(generated {datetime.now().strftime('%Y-%m-%d %H:%M')})\n")
    emit(INDEX_SEP)
    emit(INDEX_HEADER)
    emit(INDEX_SEP)

    for model in sorted(by_model):
        model_runs = by_model[model]
        emit(f"\n  {shorten_model(model)}  ({len(model_runs)} runs)\n")
        for r in model_runs:
            emit("  " + run_index_row(r))

    emit("")
    emit(INDEX_SEP)

    # Quick stats footer
    all_r = [r for runs_list in by_model.values() for r in runs_list]
    n_collapse  = sum(1 for r in all_r if r["collapse"] is True)
    n_survived  = sum(1 for r in all_r if r["collapse"] is False)
    n_unknown   = total - n_collapse - n_survived
    emit(f"\n  Totals: {total} runs | {n_collapse} collapsed | "
         f"{n_survived} survived | {n_unknown} unknown/incomplete\n")


# ---------------------------------------------------------------------------
# Per-run drill-down
# ---------------------------------------------------------------------------

DRILL_SEP   = "=" * 80
DRILL_SEP2  = "-" * 80


def sample_quotes(decisions, n=6):
    """
    Pick n representative agent quotes across the run timeline:
    first tick, a few middle ticks, last non-empty tick.
    Returns list of (tick, agent_id, action_name, pool_pct, message/reasoning).
    """
    # Filter to rows with a message or reasoning
    with_msg = [
        r for r in decisions
        if (r.get("message") or "").strip() or (r.get("reasoning") or "").strip()
    ]
    if not with_msg:
        return []

    ticks = sorted(set(int(r["tick"]) for r in with_msg if r.get("tick")))
    if not ticks:
        return []

    # Select evenly spaced tick indices
    chosen_ticks = set()
    chosen_ticks.add(ticks[0])
    chosen_ticks.add(ticks[-1])
    if len(ticks) > 2:
        step = max(1, len(ticks) // (n - 2))
        for i in range(step, len(ticks) - 1, step):
            chosen_ticks.add(ticks[i])
            if len(chosen_ticks) >= n:
                break

    quotes = []
    seen_ticks = set()
    for r in with_msg:
        t = int(r.get("tick", 0))
        if t in chosen_ticks and t not in seen_ticks:
            msg = (r.get("message") or "").strip()
            rsn = (r.get("reasoning") or "").strip()
            text = msg or rsn
            if text:
                quotes.append((
                    t,
                    r.get("agent_id", "?"),
                    r.get("action_name", r.get("action", "?")),
                    r.get("pool_pct", "?"),
                    text,
                ))
                seen_ticks.add(t)

    return sorted(quotes, key=lambda x: x[0])


def resource_table(resources, max_rows=12):
    """
    Return a list of formatted table lines for the resource trajectory.
    Shows first few, evenly-sampled middle, and last few ticks.
    """
    if not resources:
        return ["  (no resource data)"]

    lines = []
    header = f"  {'Tick':>4}  {'Pool%':>6}  {'Total cows':>10}  {'A0':>5}  {'A1':>5}  {'A2':>5}  {'Pressure':>8}"
    lines.append(header)
    lines.append("  " + "-" * 54)

    n = len(resources)
    # Choose which rows to show
    show_idx = set()
    show_idx.update(range(min(3, n)))            # first 3
    show_idx.update(range(max(0, n-3), n))       # last 3
    step = max(1, n // (max_rows - 6))
    for i in range(0, n, step):
        show_idx.add(i)
    show_idx = sorted(show_idx)

    prev_idx = -2
    for idx in show_idx:
        if idx - prev_idx > 1 and prev_idx >= 0:
            lines.append("  ...")
        row = resources[idx]
        try:
            tick     = int(row.get("tick", 0))
            pool     = float(row.get("pool_pct", 0) or 0)
            total    = int(row.get("total_cows", 0) or 0)
            a0       = int(row.get("agent0_cows", 0) or 0)
            a1       = int(row.get("agent1_cows", 0) or 0)
            a2       = int(row.get("agent2_cows", 0) or 0)
            pressure = float(row.get("pressure", 0) or 0)
            lines.append(
                f"  {tick:>4}  {pool:>6.1f}%  {total:>10}  {a0:>5}  {a1:>5}  {a2:>5}  {pressure:>8.4f}"
            )
        except (ValueError, TypeError):
            lines.append(f"  {row}")
        prev_idx = idx

    return lines


def institution_summary(institutions):
    """Return a compact summary of institution scores across the run."""
    if not institutions:
        return ["  (no institution data)"]

    scores = []
    for row in institutions:
        try:
            s = int(row.get("institution_score") or 0)
            scores.append(s)
        except ValueError:
            pass

    if not scores:
        return ["  (no scores)"]

    # Show trajectory: sample ~6 points
    n = len(institutions)
    step = max(1, n // 6)
    lines = []
    prev_score = None
    for i in range(0, n, step):
        row = institutions[i]
        try:
            tick  = int(row.get("tick", 0))
            score = int(row.get("institution_score") or 0)
            cats  = row.get("categories", "") or ""
            summ  = (row.get("round_summary") or "").strip()
            # Truncate long summaries
            if len(summ) > 90:
                summ = summ[:87] + "..."
            lines.append(f"  tick {tick:>3}: score {score}/10  [{cats}]")
            if summ:
                lines.append(f"           \"{summ}\"")
        except (ValueError, TypeError):
            pass

    avg = sum(scores) / len(scores)
    peak = max(scores)
    lines.insert(0, f"  Score range: {min(scores)}–{peak}  avg {avg:.1f}  over {n} snapshots\n")
    return lines


def print_run_drilldown(run, out_lines=None):
    """Print full drill-down for a single run."""

    def emit(line=""):
        print(line)
        if out_lines is not None:
            out_lines.append(line)

    ep    = run["ep"]
    meta  = run["meta"]
    model = run["model"]

    emit(DRILL_SEP)
    emit(f"  {run['folder']}")
    if run.get("label"):
        emit(f"  label: {run['label']}")
    emit(DRILL_SEP)

    # -- Parameters --
    emit("\nPARAMETERS")
    emit(DRILL_SEP2)
    emit(f"  condition       : {run['condition']}")
    emit(f"  model           : {model}")

    am = meta.get("agent_models")
    if am and isinstance(am, list) and len(am) > 1:
        models = [a.get("model", "?") for a in am]
        if len(set(models)) > 1:
            emit(f"  agent models    : {', '.join(models)}")

    emit(f"  cooperation     : {fmt_param(ep, 'cooperation_level')}")
    emit(f"  memory_length   : {fmt_param(ep, 'memory_length', meta.get('memory_length', '?'))}")
    comm = ep.get("communication", meta.get("communication", "?"))
    emit(f"  communication   : {comm}")
    emit(f"  initial_grass   : {fmt_param(ep, 'initial_grassland')}%")
    emit(f"  forage_req      : {fmt_param(ep, 'cow_forage_requirement')}")
    emit(f"  neg_reciprocity : {fmt_param(ep, 'negative_reciprocity')}")
    emit(f"  pos_reciprocity : {fmt_param(ep, 'positive_reciprocity')}")
    emit(f"  fairness_me     : {fmt_param(ep, 'fairness_concerning_me')}")
    emit(f"  fairness_others : {fmt_param(ep, 'fairness_concerning_others')}")
    emit(f"  risk_aversion   : {fmt_param(ep, 'risk_aversion_level')}")
    carrying = meta.get("carrying_capacity")
    if carrying:
        emit(f"  carrying cap.   : {carrying} cows")

    # -- Outcome --
    emit("\nOUTCOME")
    emit(DRILL_SEP2)
    emit(f"  result          : {outcome_str(run)}")
    emit(f"  final pool      : {fmt_pool(run['final_pool'])}")
    emit(f"  final herds     : {fmt_herds(run['final_herds'])}")
    emit(f"  peak total herd : {run['peak_herd']}")
    emit(f"  ticks logged    : {run['final_ticks']}")

    acts = run["acts"]
    total_acts = sum(acts.values())
    if total_acts:
        emit(f"\n  Action breakdown ({total_acts} total decisions):")
        for name in ("ADD", "KEEP", "REMOVE"):
            v = acts.get(name, 0)
            pct = 100 * v / total_acts if total_acts else 0
            bar = "█" * int(pct / 4)
            emit(f"    {name:<6} {v:>4}  ({pct:5.1f}%)  {bar}")

    # -- Resource trajectory --
    emit("\nRESOURCE TRAJECTORY")
    emit(DRILL_SEP2)
    for line in resource_table(run["resources"]):
        emit(line)

    # -- Institution scores --
    if run["institutions"]:
        # Filter out baseline empty rows
        real_insts = [
            r for r in run["institutions"]
            if (r.get("categories") or "").strip() or
               (r.get("round_summary") or "No messages" not in r.get("round_summary", ""))
        ]
        if real_insts:
            emit("\nINSTITUTION SCORES (Ostrom classifier)")
            emit(DRILL_SEP2)
            for line in institution_summary(real_insts):
                emit(line)

    # -- Agent quotes --
    quotes = sample_quotes(run["decisions"])
    if quotes:
        emit("\nAGENT QUOTES (sampled across run)")
        emit(DRILL_SEP2)
        for tick, agent_id, action, pool_pct, text in quotes:
            try:
                pool_str = f"{float(pool_pct):.1f}%"
            except (ValueError, TypeError):
                pool_str = str(pool_pct)
            emit(f"\n  Tick {tick:>3} | Agent {agent_id} | {action:<6} | pool {pool_str}")
            # Word-wrap the text
            wrapped = textwrap.fill(text, width=76, initial_indent="    ",
                                    subsequent_indent="    ")
            emit(f'    "{wrapped.strip()}"')

    emit("")
    emit(DRILL_SEP)
    emit("")


# ---------------------------------------------------------------------------
# Markdown writer
# ---------------------------------------------------------------------------

def to_md_index(runs):
    """Convert index output to markdown."""
    lines = []
    lines.append("# MASTOC-LLM Run Index\n")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

    by_model = defaultdict(list)
    for r in runs:
        by_model[r["model"]].append(r)

    total = sum(len(v) for v in by_model.values())
    n_collapse = sum(1 for rs in by_model.values() for r in rs if r["collapse"] is True)
    n_survived = sum(1 for rs in by_model.values() for r in rs if r["collapse"] is False)
    lines.append(f"**{total} runs** | {n_collapse} collapsed | {n_survived} survived\n")

    for model in sorted(by_model):
        model_runs = by_model[model]
        lines.append(f"\n## {shorten_model(model)} ({len(model_runs)} runs)\n")
        lines.append("| Run ID | Cond | Coop | Mem | Comm | Grass | Outcome | Pool% | Actions |")
        lines.append("|--------|------|------|-----|------|-------|---------|-------|---------|")
        for r in model_runs:
            ep = r["ep"]
            coop  = fmt_param(ep, "cooperation_level", "?")
            mem   = fmt_param(ep, "memory_length", r["meta"].get("memory_length", "?"))
            comm  = ep.get("communication", r["meta"].get("communication", "?"))
            comm_str = "on" if comm is True else ("off" if comm is False else str(comm)[:3])
            grass = fmt_param(ep, "initial_grassland", "?")
            pool  = f"{r['final_pool']:.1f}%" if r["final_pool"] is not None else "?"
            acts  = fmt_acts(r["acts"])
            out   = outcome_str(r)
            lines.append(
                f"| `{r['folder']}` | {r['condition'][:9]} | {coop} | {mem} | "
                f"{comm_str} | {grass}% | {out} | {pool} | {acts} |"
            )
    return "\n".join(lines) + "\n"


def to_md_drilldown(run):
    """Convert drill-down output to markdown."""
    ep   = run["ep"]
    meta = run["meta"]
    lines = []

    lines.append(f"# Run: {run['folder']}\n")
    if run.get("label"):
        lines.append(f"**Label:** {run['label']}\n")

    lines.append("## Parameters\n")
    lines.append("| Parameter | Value |")
    lines.append("|-----------|-------|")
    lines.append(f"| condition | {run['condition']} |")
    lines.append(f"| model | {run['model']} |")
    lines.append(f"| cooperation | {fmt_param(ep, 'cooperation_level')} |")
    lines.append(f"| memory_length | {fmt_param(ep, 'memory_length', meta.get('memory_length','?'))} |")
    comm = ep.get("communication", meta.get("communication", "?"))
    lines.append(f"| communication | {comm} |")
    lines.append(f"| initial_grass | {fmt_param(ep, 'initial_grassland')}% |")
    lines.append(f"| forage_req | {fmt_param(ep, 'cow_forage_requirement')} |")
    lines.append(f"| neg_reciprocity | {fmt_param(ep, 'negative_reciprocity')} |")
    lines.append(f"| pos_reciprocity | {fmt_param(ep, 'positive_reciprocity')} |")
    lines.append(f"| fairness_me | {fmt_param(ep, 'fairness_concerning_me')} |")
    lines.append(f"| fairness_others | {fmt_param(ep, 'fairness_concerning_others')} |")
    lines.append(f"| risk_aversion | {fmt_param(ep, 'risk_aversion_level')} |")

    lines.append("\n## Outcome\n")
    lines.append(f"- **Result:** {outcome_str(run)}")
    lines.append(f"- **Final pool:** {fmt_pool(run['final_pool'])}")
    lines.append(f"- **Final herds:** {fmt_herds(run['final_herds'])}")
    lines.append(f"- **Peak total herd:** {run['peak_herd']}")
    lines.append(f"- **Ticks logged:** {run['final_ticks']}")

    acts = run["acts"]
    total_acts = sum(acts.values())
    if total_acts:
        lines.append("\n**Action breakdown:**\n")
        lines.append("| Action | Count | % |")
        lines.append("|--------|-------|---|")
        for name in ("ADD", "KEEP", "REMOVE"):
            v = acts.get(name, 0)
            pct = 100 * v / total_acts if total_acts else 0
            lines.append(f"| {name} | {v} | {pct:.1f}% |")

    # Resource trajectory
    lines.append("\n## Resource Trajectory\n")
    lines.append("| Tick | Pool% | Total Cows | A0 | A1 | A2 | Pressure |")
    lines.append("|------|-------|------------|----|----|----|---------| ")

    resources = run["resources"]
    n = len(resources)
    show_idx = set()
    show_idx.update(range(min(4, n)))
    show_idx.update(range(max(0, n-4), n))
    step = max(1, n // 12)
    for i in range(0, n, step):
        show_idx.add(i)

    prev_idx = -2
    for idx in sorted(show_idx):
        if idx - prev_idx > 1 and prev_idx >= 0:
            lines.append("| ... | ... | ... | ... | ... | ... | ... |")
        row = resources[idx]
        try:
            tick     = int(row.get("tick", 0))
            pool     = float(row.get("pool_pct", 0) or 0)
            total    = int(row.get("total_cows", 0) or 0)
            a0       = int(row.get("agent0_cows", 0) or 0)
            a1       = int(row.get("agent1_cows", 0) or 0)
            a2       = int(row.get("agent2_cows", 0) or 0)
            pressure = float(row.get("pressure", 0) or 0)
            lines.append(f"| {tick} | {pool:.1f}% | {total} | {a0} | {a1} | {a2} | {pressure:.4f} |")
        except (ValueError, TypeError):
            pass
        prev_idx = idx

    # Institution scores
    real_insts = [
        r for r in run["institutions"]
        if (r.get("categories") or "").strip()
    ]
    if real_insts:
        lines.append("\n## Institution Scores\n")
        lines.append("| Tick | Score | Categories | Summary |")
        lines.append("|------|-------|------------|---------|")
        step = max(1, len(real_insts) // 8)
        for row in real_insts[::step]:
            try:
                tick  = int(row.get("tick", 0))
                score = int(row.get("institution_score") or 0)
                cats  = row.get("categories", "") or ""
                summ  = (row.get("round_summary") or "").strip()
                if len(summ) > 80:
                    summ = summ[:77] + "..."
                lines.append(f"| {tick} | {score}/10 | {cats} | {summ} |")
            except (ValueError, TypeError):
                pass

    # Agent quotes
    quotes = sample_quotes(run["decisions"])
    if quotes:
        lines.append("\n## Agent Quotes\n")
        for tick, agent_id, action, pool_pct, text in quotes:
            try:
                pool_str = f"{float(pool_pct):.1f}%"
            except (ValueError, TypeError):
                pool_str = str(pool_pct)
            lines.append(
                f"\n**Tick {tick} | Agent {agent_id} | {action} | pool {pool_str}**\n"
            )
            lines.append(f"> {text}\n")

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="MASTOC-LLM log inspector",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--run", metavar="RUN_ID",
        help="Drill down into a specific run (full folder name or prefix)"
    )
    parser.add_argument(
        "--md", action="store_true",
        help="Also write output to a markdown file in logs/"
    )
    parser.add_argument(
        "--model", metavar="MODEL",
        help="Filter index to runs matching this model name substring"
    )
    parser.add_argument(
        "--collapse", action="store_true",
        help="Filter index to collapsed runs only"
    )
    parser.add_argument(
        "--survived", action="store_true",
        help="Filter index to survived runs only"
    )
    args = parser.parse_args()

    filter_collapse = None
    if args.collapse:
        filter_collapse = True
    elif args.survived:
        filter_collapse = False

    # -- Drill-down mode --
    if args.run:
        folder = find_run(args.run)
        if not folder:
            print(f"ERROR: no run found matching '{args.run}'", file=sys.stderr)
            sys.exit(1)
        run = load_run(folder)
        md_lines = [] if args.md else None
        print_run_drilldown(run, out_lines=md_lines)
        if args.md:
            out_path = os.path.join(LOGS_DIR, f"{folder}.md")
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(to_md_drilldown(run))
            print(f"  -> written to {out_path}")
        return

    # -- Index mode --
    runs = list(all_runs(filter_model=args.model, filter_collapse=filter_collapse))
    if not runs:
        print("No runs found matching the given filters.")
        return

    md_lines = [] if args.md else None
    print_index(runs, out_lines=md_lines)

    if args.md:
        out_path = os.path.join(LOGS_DIR, "index.md")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(to_md_index(runs))
        print(f"  -> index written to {out_path}")


if __name__ == "__main__":
    main()
