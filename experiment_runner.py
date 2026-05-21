"""
experiment_runner.py
====================
Batch runner and analysis tool for MASTOC-LLM experiments.

Modes
-----
  run     -- launch headless NetLogo runs via pynetlogo (one per condition)
  analyse -- aggregate logs/ CSVs and produce summary figures
  xml     -- write a BehaviorSpace XML file for GUI batch runs
  cost    -- estimate Anthropic API cost for planned runs

Usage examples
--------------
  python experiment_runner.py --mode run --netlogo-path "C:/Program Files/NetLogo 7.0.4"
  python experiment_runner.py --mode run --netlogo-path "C:/Program Files/NetLogo 7.0.4" --conditions full-gabm
  python experiment_runner.py --mode analyse --log-dir logs
  python experiment_runner.py --mode xml
  python experiment_runner.py --mode cost
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from pathlib import Path


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _short_path_windows(p: str) -> str:
    """
    On Windows, convert a path that contains spaces to its 8.3 short-name
    equivalent so JPype / Java can use it without splitting on the space.
    Falls back to the original path if the conversion fails.
    """
    if os.name != "nt":
        return p
    try:
        import ctypes
        buf = ctypes.create_unicode_buffer(32768)
        get_short = ctypes.windll.kernel32.GetShortPathNameW
        if get_short(str(p), buf, 32768):
            return buf.value
    except Exception:
        pass
    return p


def _load_config(config_path: str = "config.json") -> dict:
    try:
        with open(config_path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


# ──────────────────────────────────────────────────────────────────────────────
# MODE: run
# ──────────────────────────────────────────────────────────────────────────────

ALL_CONDITIONS = ["baseline", "full-gabm", "hybrid"]


def _detect_netlogo_version(netlogo_path: str) -> tuple:
    """Return (major, minor) version tuple from the NetLogo install path string."""
    import re
    m = re.search(r'(\d+)\.(\d+)', str(netlogo_path))
    if m:
        return int(m.group(1)), int(m.group(2))
    return (0, 0)


def run_experiments(
    netlogo_path: str,
    conditions: list,
    ticks: int,
    backend: str,
    model: str,
    memory_length: int,
    log_dir: str,
    nlogo_file: str,
    detect_institutions: bool,
    institution_interval: int,
) -> None:
    """
    Launch headless NetLogo runs via pynetlogo (NetLogo 6.x only) or
    NetLogo's native headless script (NetLogo 7.x).

    pynetlogo does not support NetLogo 7.x due to internal XML format changes.
    For NetLogo 7.x the runner falls back to the native netlogo-headless script
    paired with a generated BehaviorSpace experiment.
    """
    major, minor = _detect_netlogo_version(netlogo_path)

    if major >= 7:
        print(
            "\nNOTE: pynetlogo does not support NetLogo 7.x (internal XML format\n"
            "changed in 7.0). Falling back to NetLogo's native headless runner.\n"
            "\nThis requires BehaviorSpace experiments defined in the .nlogo file.\n"
            "Run  --mode xml  first, then import the XML into the model via:\n"
            "  NetLogo GUI -> Tools -> BehaviorSpace -> Import -> behaviourspace.xml\n"
            "and save the model. Then re-run this command.\n"
            "\nAlternatively, run each condition manually in the NetLogo GUI:\n"
            "  1. Open MASTOC-LLM.nlogo\n"
            "  2. Set Condition chooser to the desired condition\n"
            "  3. Click Setup, then Simulation\n"
            "  4. Logs are written to logs/ automatically\n"
        )
        _run_native_headless(netlogo_path, conditions, nlogo_file)
        return

    # ── NetLogo 6.x path via pynetlogo ───────────────────────────────────────
    try:
        import pynetlogo
    except ImportError:
        print("ERROR: pynetlogo not installed. Run: pip install pynetlogo jpype1")
        sys.exit(1)

    nl_home   = _short_path_windows(str(Path(netlogo_path).resolve()))
    nlogo_abs = str(Path(nlogo_file).resolve())

    print(f"NetLogo home : {nl_home}")
    print(f"Model file   : {nlogo_abs}")
    print(f"Conditions   : {conditions}")
    print(f"Ticks        : {ticks}")
    print(f"Backend      : {backend} / {model}")
    print()

    for condition in conditions:
        print(f"{'='*60}")
        print(f"Starting condition: {condition}")
        print(f"{'='*60}")

        try:
            netlogo = pynetlogo.NetLogoLink(netlogo_home=nl_home, gui=False)
            netlogo.load_model(nlogo_abs)
        except Exception as exc:
            print(f"ERROR: Could not start NetLogo: {exc}")
            sys.exit(1)

        try:
            netlogo.command(f'set condition "{condition}"')
            netlogo.command(f'set llm-backend "{backend}"')
            netlogo.command(f'set anthropic-model-name "{model}"')
            netlogo.command(f'set memory-length {memory_length}')
            netlogo.command(
                f'set detect-institutions {"true" if detect_institutions else "false"}'
            )
            netlogo.command(f'set institution-check-interval {institution_interval}')
            netlogo.command("setup")
            print(f"Setup complete. Running {ticks} ticks...")

            for tick in range(1, ticks + 1):
                netlogo.command("go")
                if tick % 10 == 0:
                    pool = netlogo.report("pool-patches")
                    cows = netlogo.report("total-cows")
                    print(f"  tick {tick:3d} | pool={pool} | cows={cows}")

            print(f"Condition '{condition}' complete.")

        except Exception as exc:
            print(f"ERROR during simulation: {exc}")
            raise

        finally:
            try:
                netlogo.kill_workspace()
            except Exception:
                pass

    print()
    print("All conditions complete. Run --mode analyse to generate figures.")


def _run_native_headless(netlogo_path: str, conditions: list, nlogo_file: str) -> None:
    """
    Attempt to run via NetLogo 7.x native headless script.
    Requires BehaviorSpace experiments to be embedded in the .nlogo file.
    """
    import subprocess

    nl_path   = Path(netlogo_path)
    nlogo_abs = str(Path(nlogo_file).resolve())

    # NetLogo 7.x headless script name
    script = nl_path / "netlogo-headless.bat"
    if not script.exists():
        script = nl_path / "netlogo-headless.sh"

    if not script.exists():
        print(f"ERROR: Could not find netlogo-headless script in {nl_path}")
        print("Run the simulation manually in the NetLogo GUI instead.")
        return

    experiment_names = {
        "baseline":  "MASTOC-LLM Baseline",
        "full-gabm": "MASTOC-LLM Full-GABM",
        "hybrid":    "MASTOC-LLM Hybrid",
    }

    for condition in conditions:
        exp_name = experiment_names.get(condition, condition)
        print(f"\nLaunching headless run: {exp_name}")
        cmd = [
            str(script),
            "--model",      nlogo_abs,
            "--experiment", exp_name,
            "--table",      f"headless_{condition}.csv",
        ]
        print(f"Command: {' '.join(cmd)}")
        result = subprocess.run(cmd)
        if result.returncode != 0:
            print(
                f"\nHeadless run failed (exit {result.returncode}).\n"
                "Make sure the BehaviorSpace experiments are embedded in the .nlogo\n"
                "file (run --mode xml, import into NetLogo GUI, save).\n"
                "Or run the simulation directly in the NetLogo GUI."
            )


# ──────────────────────────────────────────────────────────────────────────────
# MODE: analyse
# ──────────────────────────────────────────────────────────────────────────────

def _parse_data_dir(data_dir: str = "Data") -> list:
    """
    Parse the MASTOC flat-file Data/ outputs (baseline / rule-based runs).

    Each file contains one or more runs stacked vertically, separated by
    'Condition: X' header lines.  The pressure file also has a metadata block
    (key: value lines) before the numeric data.

    Returns a list of resource rows in the same dict format as resources.csv.
    """
    data_path = Path(data_dir)
    if not data_path.exists():
        return []

    def _split_runs(filepath):
        """Split a flat file into (condition, [numeric_values]) blocks."""
        blocks = []
        current_cond = None
        current_vals = []
        with open(filepath, encoding="utf-8", errors="replace") as f:
            for raw in f:
                line = raw.strip()
                if line.lower().startswith("condition:"):
                    if current_cond is not None:
                        blocks.append((current_cond, current_vals))
                    current_cond = line.split(":", 1)[1].strip()
                    current_vals = []
                elif current_cond is not None:
                    # Skip metadata lines (contain letters/colons but aren't numeric)
                    try:
                        current_vals.append(float(line))
                    except ValueError:
                        pass  # metadata line — skip
        if current_cond is not None:
            blocks.append((current_cond, current_vals))
        return blocks

    cows_file     = data_path / "1-count-cows.txt"
    pressure_file = data_path / "Sensitivity-pressure.txt"
    agent_files   = [data_path / f"1-gain-agent{i}.txt" for i in range(3)]

    if not cows_file.exists():
        return []

    cows_runs     = _split_runs(cows_file)
    pressure_runs = _split_runs(pressure_file) if pressure_file.exists() else []
    agent_runs    = [_split_runs(f) if f.exists() else [] for f in agent_files]

    rows = []
    run_counters = {}

    for run_idx, (condition, cows_vals) in enumerate(cows_runs):
        # Match up pressure and agent data by position within each condition
        run_counters[condition] = run_counters.get(condition, 0) + 1
        rep = run_counters[condition]
        run_id = f"data_{condition}_rep{rep}"

        # Find matching pressure run (same condition, same position)
        cond_pressure = [v for c, v in pressure_runs if c == condition]
        rep_idx = rep - 1
        pressure_vals = cond_pressure[rep_idx] if rep_idx < len(cond_pressure) else []

        cond_agents = []
        for agent_run_list in agent_runs:
            cond_a = [v for c, v in agent_run_list if c == condition]
            cond_agents.append(cond_a[rep_idx] if rep_idx < len(cond_a) else [])

        # Build one row per tick
        pool_max = 1089  # standard MASTOC default (33x33 grid)
        for tick_idx, total_cows in enumerate(cows_vals):
            tick = tick_idx + 1
            pressure = (pressure_vals[tick_idx]
                        if tick_idx < len(pressure_vals) else "")
            agent_cows = [
                int(cond_agents[i][tick_idx])
                if tick_idx < len(cond_agents[i]) else ""
                for i in range(3)
            ]
            # Estimate pool from pressure (pressure = grazed / max)
            # pool_pct = 100 * (1 - pressure) when grass is depleted linearly
            if pressure != "":
                pool_patches = max(0, int(round(pool_max * (1.0 - float(pressure)))))
                pool_pct     = round(100.0 * pool_patches / pool_max, 1)
            else:
                pool_patches = ""
                pool_pct     = ""

            rows.append({
                "tick":         tick,
                "pool_patches": pool_patches,
                "pool_pct":     pool_pct,
                "total_cows":   int(total_cows),
                "pressure":     round(float(pressure), 4) if pressure != "" else "",
                "agent0_cows":  agent_cows[0],
                "agent1_cows":  agent_cows[1],
                "agent2_cows":  agent_cows[2],
                "run_id":       run_id,
                "condition":    condition,
                "source":       "Data/",
            })

    return rows


def analyse_results(log_dir: str, data_dir: str = "Data") -> None:
    """
    Aggregate run data from both sources:
      logs/  — rich CSV outputs from LLM runs (full-gabm, hybrid)
      Data/  — MASTOC flat-file outputs from baseline (rule-based) runs
    Produces merged summary CSVs and comparison figures.
    """
    resources_rows = []
    decision_rows  = []
    institution_rows = []

    # ── Source 1: logs/ (LLM runs) ────────────────────────────────────────────
    log_path = Path(log_dir)
    run_dirs = sorted(log_path.iterdir()) if log_path.exists() else []

    for run_dir in run_dirs:
        if not run_dir.is_dir():
            continue
        meta_file = run_dir / "run_meta.json"
        if not meta_file.exists():
            continue
        with open(meta_file, encoding="utf-8") as f:
            meta = json.load(f)
        run_id           = meta.get("run_id", run_dir.name)
        condition        = meta.get("condition", "unknown")
        carrying_capacity = meta.get("carrying_capacity", None)

        res_file = run_dir / "resources.csv"
        if res_file.exists() and res_file.stat().st_size > 0:
            with open(res_file, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    row["run_id"]            = run_id
                    row["condition"]         = condition
                    row["source"]            = "logs/"
                    row["carrying_capacity"] = carrying_capacity
                    resources_rows.append(row)

        dec_file = run_dir / "decisions.csv"
        if dec_file.exists() and dec_file.stat().st_size > 0:
            with open(dec_file, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    row["run_id"]    = run_id
                    row["condition"] = condition
                    decision_rows.append(row)

        inst_file = run_dir / "institutions.csv"
        if inst_file.exists() and inst_file.stat().st_size > 0:
            with open(inst_file, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    row["run_id"]    = run_id
                    row["condition"] = condition
                    institution_rows.append(row)

    # ── Source 2: Data/ (baseline flat files) ─────────────────────────────────
    data_rows = _parse_data_dir(data_dir)
    if data_rows:
        n_runs = len(set(r["run_id"] for r in data_rows))
        print(f"Loaded {len(data_rows)} rows from Data/ "
              f"({n_runs} baseline run(s))")
        resources_rows.extend(data_rows)
    else:
        print("No Data/ flat-file runs found.")

    if not resources_rows:
        print("No data found in logs/ or Data/. Have any runs completed?")
        return

    # Write aggregated CSVs
    _write_csv("results_resources.csv", resources_rows)
    print(f"Written: results_resources.csv  ({len(resources_rows)} rows)")

    if decision_rows:
        _write_csv("results_decisions.csv", decision_rows)
        print(f"Written: results_decisions.csv  ({len(decision_rows)} rows)")

    if institution_rows:
        _write_csv("results_institutions.csv", institution_rows)
        print(f"Written: results_institutions.csv  ({len(institution_rows)} rows)")

    # Attempt to generate figures (graceful skip if matplotlib not available)
    try:
        _generate_figures(resources_rows, institution_rows)
    except ImportError:
        print("matplotlib/seaborn not installed — skipping figures.")
        print("  pip install matplotlib seaborn pandas")


def _write_csv(filename: str, rows: list[dict]) -> None:
    if not rows:
        return
    # Union all keys across all rows — some runs log extra fields (e.g. backend, model)
    # that are absent from earlier log formats; preserve insertion order.
    seen: dict = {}
    for row in rows:
        for k in row:
            seen.setdefault(k, None)
    fieldnames = list(seen.keys())
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _generate_figures(resources_rows: list, institution_rows: list) -> None:
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mticker

    figures_dir = Path("figures")
    figures_dir.mkdir(exist_ok=True)

    # ── Figure 1: Resource dynamics (pool_pct over time per condition) ───────
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle("MASTOC-LLM: Commons Dynamics", fontsize=14, fontweight="bold")

    # Group by (condition, run_id)
    from collections import defaultdict
    res_by_run: dict = defaultdict(lambda: defaultdict(list))
    for row in resources_rows:
        key = (row["condition"], row["run_id"])
        try:
            res_by_run[key]["tick"].append(int(row["tick"]))
            res_by_run[key]["pool_pct"].append(float(row["pool_pct"]))
            res_by_run[key]["total_cows"].append(int(row["total_cows"]))
        except (ValueError, KeyError):
            pass

    condition_colors = {
        "baseline": "#d62728",
        "full-gabm": "#2ca02c",
        "hybrid": "#1f77b4",
    }

    ax1 = axes[0]
    ax2 = axes[1]

    plotted_conditions: set = set()
    for (condition, run_id), data in sorted(res_by_run.items()):
        color = condition_colors.get(condition, "grey")
        label = condition if condition not in plotted_conditions else None
        plotted_conditions.add(condition)
        ax1.plot(data["tick"], data["pool_pct"],
                 color=color, alpha=0.8, linewidth=1.5, label=label)
        ax2.plot(data["tick"], data["total_cows"],
                 color=color, alpha=0.8, linewidth=1.5)

    ax1.set_xlabel("Tick")
    ax1.set_ylabel("Pool health (%)")
    ax1.set_title("Grassland remaining")
    ax1.set_ylim(0, 105)
    ax1.legend(title="Condition")
    ax1.grid(True, alpha=0.3)

    ax2.set_xlabel("Tick")
    ax2.set_ylabel("Total cows")
    ax2.set_title("Herd sizes over time")
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    out1 = figures_dir / "resource_dynamics.png"
    plt.savefig(out1, dpi=150)
    plt.close()
    print(f"Saved: {out1}")

    # ── Figure 2: Institution emergence ──────────────────────────────────────
    if institution_rows:
        fig2, ax3 = plt.subplots(figsize=(10, 4))
        inst_by_run: dict = defaultdict(lambda: defaultdict(list))
        for row in institution_rows:
            key = (row["condition"], row["run_id"])
            try:
                inst_by_run[key]["tick"].append(int(row["tick"]))
                inst_by_run[key]["score"].append(float(row["institution_score"]))
            except (ValueError, KeyError):
                pass

        plotted_conditions2: set = set()
        for (condition, run_id), data in sorted(inst_by_run.items()):
            color = condition_colors.get(condition, "grey")
            label = condition if condition not in plotted_conditions2 else None
            plotted_conditions2.add(condition)
            ax3.plot(data["tick"], data["score"],
                     color=color, alpha=0.8, linewidth=1.5,
                     marker="o", markersize=3, label=label)

        ax3.set_xlabel("Tick")
        ax3.set_ylabel("Institution score (0–10)")
        ax3.set_title("Ostrom Institution Emergence")
        ax3.set_ylim(0, 10.5)
        ax3.legend(title="Condition")
        ax3.grid(True, alpha=0.3)
        plt.tight_layout()
        out2 = figures_dir / "institution_emergence.png"
        plt.savefig(out2, dpi=150)
        plt.close()
        print(f"Saved: {out2}")

    # ── Figure 3: Individual herds per agent (full-gabm runs) ────────────────
    gabm_runs = [(k, v) for k, v in res_by_run.items() if k[0] == "full-gabm"]
    if gabm_runs:
        # Collect per-agent herd data (only runs with actual data)
        agent_data: dict = {}
        for row in resources_rows:
            if row.get("condition") != "full-gabm":
                continue
            rid = row["run_id"]
            if rid not in agent_data:
                agent_data[rid] = {"tick": [], "a0": [], "a1": [], "a2": []}
            try:
                agent_data[rid]["tick"].append(int(row["tick"]))
                for i in range(3):
                    agent_data[rid][f"a{i}"].append(int(row[f"agent{i}_cows"]))
            except (ValueError, KeyError):
                pass

        # Drop runs with fewer than 2 ticks (empty / aborted)
        agent_data = {rid: d for rid, d in agent_data.items() if len(d["tick"]) >= 2}

        if agent_data:
            n_runs = len(agent_data)
            n_cols = min(n_runs, 4)           # max 4 panels per row
            n_rows = (n_runs + n_cols - 1) // n_cols
            fig3, axes3 = plt.subplots(
                n_rows, n_cols,
                figsize=(5 * n_cols, 4 * n_rows),
                squeeze=False
            )
            agent_colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]
            for idx, (rid, data) in enumerate(agent_data.items()):
                row_i, col_i = divmod(idx, n_cols)
                ax = axes3[row_i][col_i]
                for i in range(3):
                    ax.plot(data["tick"], data[f"a{i}"],
                            color=agent_colors[i], linewidth=1.5, label=f"Agent {i}")
                ax.set_xlabel("Tick")
                ax.set_ylabel("Cows")
                # Truncate run_id label so long IDs don't overflow
                label = rid if len(rid) <= 22 else rid[:10] + "…" + rid[-10:]
                ax.set_title(label, fontsize=7)
                ax.legend(fontsize=7)
                ax.grid(True, alpha=0.3)

            # Hide any unused subplot cells
            for idx in range(n_runs, n_rows * n_cols):
                row_i, col_i = divmod(idx, n_cols)
                axes3[row_i][col_i].set_visible(False)

            plt.suptitle("Full-GABM: Individual Agent Herds", fontsize=13, fontweight="bold")
            plt.tight_layout()
            out3 = figures_dir / "agent_herds.png"
            plt.savefig(out3, dpi=120)
            plt.close()
            print(f"Saved: {out3}  ({n_runs} runs, {n_rows}×{n_cols} grid)")


# ──────────────────────────────────────────────────────────────────────────────
# MODE: xml
# ──────────────────────────────────────────────────────────────────────────────

def write_behaviourspace_xml(output: str = "behaviourspace.xml") -> None:
    """Generate a BehaviorSpace XML for use inside the NetLogo GUI."""
    xml = (
        '<?xml version="1.0" encoding="us-ascii"?>\n'
        '<!DOCTYPE experiments SYSTEM "behaviorspace.dtd">\n'
        '<experiments>\n'
        '  <experiment name="MASTOC-LLM Baseline" repetitions="3" runMetricsEveryStep="true">\n'
        '    <setup>setup</setup>\n'
        '    <go>go</go>\n'
        '    <timeLimit steps="120"/>\n'
        '    <metric>pool-patches</metric>\n'
        '    <metric>total-cows</metric>\n'
        '    <metric>pressure</metric>\n'
        '    <enumeratedValueSet variable="condition">\n'
        '      <value value="&quot;baseline&quot;"/>\n'
        '    </enumeratedValueSet>\n'
        '    <enumeratedValueSet variable="llm-backend">\n'
        '      <value value="&quot;anthropic&quot;"/>\n'
        '    </enumeratedValueSet>\n'
        '  </experiment>\n'
        '  <experiment name="MASTOC-LLM Full-GABM" repetitions="3" runMetricsEveryStep="true">\n'
        '    <setup>setup</setup>\n'
        '    <go>go</go>\n'
        '    <timeLimit steps="120"/>\n'
        '    <metric>pool-patches</metric>\n'
        '    <metric>total-cows</metric>\n'
        '    <metric>pressure</metric>\n'
        '    <enumeratedValueSet variable="condition">\n'
        '      <value value="&quot;full-gabm&quot;"/>\n'
        '    </enumeratedValueSet>\n'
        '    <enumeratedValueSet variable="llm-backend">\n'
        '      <value value="&quot;anthropic&quot;"/>\n'
        '    </enumeratedValueSet>\n'
        '  </experiment>\n'
        '  <experiment name="MASTOC-LLM Hybrid" repetitions="3" runMetricsEveryStep="true">\n'
        '    <setup>setup</setup>\n'
        '    <go>go</go>\n'
        '    <timeLimit steps="120"/>\n'
        '    <metric>pool-patches</metric>\n'
        '    <metric>total-cows</metric>\n'
        '    <metric>pressure</metric>\n'
        '    <enumeratedValueSet variable="condition">\n'
        '      <value value="&quot;hybrid&quot;"/>\n'
        '    </enumeratedValueSet>\n'
        '    <enumeratedValueSet variable="llm-backend">\n'
        '      <value value="&quot;anthropic&quot;"/>\n'
        '    </enumeratedValueSet>\n'
        '  </experiment>\n'
        '</experiments>\n'
    )
    with open(output, "w", encoding="utf-8") as f:
        f.write(xml)
    print(f"Written: {output}")
    print("In NetLogo: Tools -> BehaviorSpace -> Import -> select this file")


# ──────────────────────────────────────────────────────────────────────────────
# MODE: cost
# ──────────────────────────────────────────────────────────────────────────────

def estimate_cost(conditions, ticks, model):
    in_toks, out_toks = 700, 150
    in_price, out_price = 3.00, 15.00
    agent_calls = {"baseline": 0, "full-gabm": 3, "hybrid": 1}
    inst_calls  = {"baseline": 0, "full-gabm": 0.2, "hybrid": 0.2}

    print(f"\nCost estimate | model: {model} | ticks: {ticks}")
    print(f"{'Condition':<15} {'Calls':>8} {'Est. cost':>12}")
    print("-" * 40)
    total = 0.0
    for cond in conditions:
        calls = (agent_calls.get(cond, 0) + inst_calls.get(cond, 0)) * ticks
        cost  = (calls * in_toks / 1e6 * in_price +
                 calls * out_toks / 1e6 * out_price)
        total += cost
        print(f"{cond:<15} {calls:>8.0f} ${cost:>10.3f}")
    print("-" * 40)
    print(f"{'TOTAL':<15} {'':<8} ${total:>10.3f}")
    print("(Prices based on claude-sonnet-4-6, May 2025)")


# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────

def main():
    cfg     = _load_config()
    sim_cfg = cfg.get("simulation", {})
    llm_cfg = cfg.get("llm", {})

    parser = argparse.ArgumentParser(description="MASTOC-LLM experiment runner")
    parser.add_argument("--mode", required=True,
                        choices=["run", "analyse", "xml", "cost"])
    parser.add_argument("--netlogo-path",
                        default="C:/Program Files/NetLogo 7.0.4")
    parser.add_argument("--nlogo-file", default="MASTOC-LLM.nlogo")
    parser.add_argument("--conditions", nargs="+", default=ALL_CONDITIONS,
                        choices=ALL_CONDITIONS)
    parser.add_argument("--ticks", type=int,
                        default=sim_cfg.get("ticks", 120))
    parser.add_argument("--backend",
                        default=llm_cfg.get("backend", "anthropic"),
                        choices=["anthropic", "ollama"])
    parser.add_argument("--model",
                        default=llm_cfg.get("anthropic_model", "claude-sonnet-4-6"))
    parser.add_argument("--memory-length", type=int,
                        default=sim_cfg.get("memory_length", 5))
    parser.add_argument("--log-dir",
                        default=cfg.get("logging", {}).get("log_dir", "logs"))
    parser.add_argument("--xml-output", default="behaviourspace.xml")
    parser.add_argument("--no-institutions", action="store_true")
    parser.add_argument("--institution-interval", type=int,
                        default=sim_cfg.get("institution_check_interval", 5))

    args = parser.parse_args()

    if args.mode == "run":
        run_experiments(
            netlogo_path=args.netlogo_path,
            conditions=args.conditions,
            ticks=args.ticks,
            backend=args.backend,
            model=args.model,
            memory_length=args.memory_length,
            log_dir=args.log_dir,
            nlogo_file=args.nlogo_file,
            detect_institutions=not args.no_institutions,
            institution_interval=args.institution_interval,
        )
    elif args.mode == "analyse":
        analyse_results(log_dir=args.log_dir)
    elif args.mode == "xml":
        write_behaviourspace_xml(output=args.xml_output)
    elif args.mode == "cost":
        estimate_cost(conditions=args.conditions, ticks=args.ticks, model=args.model)


if __name__ == "__main__":
    main()
