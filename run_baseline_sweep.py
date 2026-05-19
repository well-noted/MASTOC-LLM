"""
run_baseline_sweep.py
=====================
Run a batch of baseline simulations with varied random seeds via NetLogo headless.

Each repetition automatically gets a different random seed from NetLogo's
BehaviorSpace engine, giving you genuine statistical spread without any
LLM API calls.

Strategy: inject a custom "baseline-sweep" experiment into a *temp copy* of the
.nlogox file, then invoke netlogo-headless against that copy.  The original
model file is never modified.

Usage
-----
  python run_baseline_sweep.py                          # 30 runs, default params
  python run_baseline_sweep.py --runs 50
  python run_baseline_sweep.py --runs 20 --ticks 60
  python run_baseline_sweep.py --grassland 50,75,100    # sweep three starting conditions
  python run_baseline_sweep.py --netlogo-path "C:/Program Files/NetLogo 7.0.4"
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


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _short_path(p: Path | str) -> str:
    """
    Return the 8.3 short path for a Windows path so Java never sees a space.
    Falls back to the original string on non-Windows or if conversion fails.
    """
    if os.name != "nt":
        return str(p)
    try:
        buf = ctypes.create_unicode_buffer(32768)
        if ctypes.windll.kernel32.GetShortPathNameW(str(p), buf, 32768):
            return buf.value
    except Exception:
        pass
    return str(p)


def _find_netlogo(hint: str | None) -> Path:
    """Return the NetLogo install directory, searching common locations if needed."""
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
    """
    Find a java executable.  Prefer NetLogo's own bundled JDK so we use the
    exact JVM version NetLogo was tested against.
    """
    for rel in ["jdk/bin/java.exe", "runtime/bin/java.exe",
                "jdk/bin/java",    "runtime/bin/java"]:
        candidate = netlogo_dir / rel
        if candidate.exists():
            return _short_path(candidate)
    # Fall back to JAVA_HOME or system java
    java_home = os.environ.get("JAVA_HOME")
    if java_home:
        candidate = Path(java_home) / "bin" / "java.exe"
        if candidate.exists():
            return _short_path(candidate)
    return "java"


def _find_netlogo_jar(netlogo_dir: Path) -> Path:
    """Return the main netlogo-*.jar (it embeds its own dependency manifest)."""
    jars = sorted((netlogo_dir / "app").glob("netlogo-*.jar"))
    if not jars:
        sys.exit(f"No netlogo-*.jar found under {netlogo_dir / 'app'}")
    return jars[-1]   # highest version if multiple


def _find_extensions_dir(netlogo_dir: Path) -> str:
    """
    Return a semicolon-separated list of extensions directories that together
    cover both the NetLogo install extensions and user-installed extensions
    (e.g. the Python 'py' extension installed via the Extensions Manager).

    Search order:
      1. <netlogo_install>/extensions   (built-in)
      2. %USERPROFILE%/Documents/NetLogo*/extensions  (Extensions Manager default)
      3. %APPDATA%/NetLogo/extensions   (alternative user location)
    """
    dirs: list[str] = []

    def _add(p: Path) -> None:
        if p.exists() and str(p) not in dirs:
            dirs.append(_short_path(p))

    _add(netlogo_dir / "extensions")

    # User documents — Extensions Manager installs here
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

    # Verify py is actually reachable
    py_found = any((Path(d.replace("\\", "/")) / "py").exists()
                   or (Path(d) / "py").exists() for d in dirs)
    if not py_found:
        print(f"WARNING: 'py' extension not found in any of: {dirs}")
        print("         If the run fails, check where NetLogo installed it.")

    return found


# ──────────────────────────────────────────────────────────────────────────────
# Experiment XML builder
# ──────────────────────────────────────────────────────────────────────────────

def _build_experiment_xml(
    runs: int,
    ticks: int,
    grassland_values: list[int],
    forage: float,
    growth_rate: float,
    coop: float,
    neg_r: float,
    risk: float,
    fairness_me: float,
    fairness_oth: float,
) -> str:
    """Return a single <experiment> XML element to inject into the .nlogox."""

    grassland_values_xml = "\n          ".join(
        f'<value value="{g}"></value>' for g in grassland_values
    )

    return textwrap.dedent(f"""\
        <experiment name="baseline-sweep"
                    repetitions="{runs}"
                    sequentialRunOrder="false"
                    runMetricsEveryStep="true"
                    timeLimit="{ticks}">
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
              <value value="&quot;baseline&quot;"></value>
            </enumeratedValueSet>
            <enumeratedValueSet variable="cow-forage-requirement">
              <value value="{forage}"></value>
            </enumeratedValueSet>
            <enumeratedValueSet variable="initial-grassland">
              {grassland_values_xml}
            </enumeratedValueSet>
            <enumeratedValueSet variable="initial-grass-growth-rate">
              <value value="{growth_rate}"></value>
            </enumeratedValueSet>
            <enumeratedValueSet variable="cooperation-level">
              <value value="{coop}"></value>
            </enumeratedValueSet>
            <enumeratedValueSet variable="negative-reciprocity">
              <value value="{neg_r}"></value>
            </enumeratedValueSet>
            <enumeratedValueSet variable="positive-reciprocity">
              <value value="1"></value>
            </enumeratedValueSet>
            <enumeratedValueSet variable="risk-aversion-level">
              <value value="{risk}"></value>
            </enumeratedValueSet>
            <enumeratedValueSet variable="fairness-concerning-me">
              <value value="{fairness_me}"></value>
            </enumeratedValueSet>
            <enumeratedValueSet variable="fairness-concerning-others">
              <value value="{fairness_oth}"></value>
            </enumeratedValueSet>
            <enumeratedValueSet variable="conformity-level">
              <value value="0"></value>
            </enumeratedValueSet>
            <enumeratedValueSet variable="memory-length">
              <value value="5"></value>
            </enumeratedValueSet>
            <enumeratedValueSet variable="detect-institutions">
              <value value="true"></value>
            </enumeratedValueSet>
            <enumeratedValueSet variable="institution-check-interval">
              <value value="5"></value>
            </enumeratedValueSet>
            <enumeratedValueSet variable="num-llm-agents">
              <value value="1"></value>
            </enumeratedValueSet>
            <enumeratedValueSet variable="agent0-backend">
              <value value="&quot;anthropic&quot;"></value>
            </enumeratedValueSet>
            <enumeratedValueSet variable="agent0-model">
              <value value="&quot;claude-sonnet-4-6&quot;"></value>
            </enumeratedValueSet>
            <enumeratedValueSet variable="agent1-backend">
              <value value="&quot;anthropic&quot;"></value>
            </enumeratedValueSet>
            <enumeratedValueSet variable="agent1-model">
              <value value="&quot;claude-sonnet-4-6&quot;"></value>
            </enumeratedValueSet>
            <enumeratedValueSet variable="agent2-backend">
              <value value="&quot;anthropic&quot;"></value>
            </enumeratedValueSet>
            <enumeratedValueSet variable="agent2-model">
              <value value="&quot;claude-sonnet-4-6&quot;"></value>
            </enumeratedValueSet>
            <enumeratedValueSet variable="system-prompt-override">
              <value value="&quot;&quot;"></value>
            </enumeratedValueSet>
          </constants>
        </experiment>""")


def _inject_experiment(model_content: str, experiment_xml: str) -> str:
    """
    Insert (or replace) the 'baseline-sweep' experiment inside the model's
    <experiments> block.  The original model XML is left unchanged.
    """
    # Remove any existing baseline-sweep experiment
    model_content = re.sub(
        r'\s*<experiment name="baseline-sweep".*?</experiment>',
        "",
        model_content,
        flags=re.DOTALL,
    )

    # Indent the experiment block to match the surrounding XML (4 spaces)
    indented = "\n".join("    " + line for line in experiment_xml.splitlines())

    # Insert just before </experiments>
    if "</experiments>" not in model_content:
        sys.exit("Could not find </experiments> in the model file — is this a valid .nlogox?")

    return model_content.replace(
        "</experiments>",
        f"{indented}\n  </experiments>",
        1,
    )


# ──────────────────────────────────────────────────────────────────────────────
# Runner
# ──────────────────────────────────────────────────────────────────────────────

def run(args: argparse.Namespace) -> None:
    netlogo_dir = _find_netlogo(args.netlogo_path)
    model_path  = Path(args.model).resolve()
    if not model_path.exists():
        sys.exit(f"Model file not found: {model_path}")

    grassland_values = [int(g.strip()) for g in args.grassland.split(",")]
    total_runs = args.runs * len(grassland_values)

    print("Baseline sweep plan:")
    print(f"  Repetitions per grassland value : {args.runs}")
    print(f"  Grassland values                : {grassland_values}")
    print(f"  Total runs                      : {total_runs}")
    print(f"  Max ticks per run               : {args.ticks}")
    print(f"  Forage requirement              : {args.forage}")
    print(f"  Cooperation level               : {args.coop}")
    print(f"  Negative reciprocity            : {args.neg_r}")
    print(f"  Model                           : {model_path}")
    print(f"  NetLogo                         : {netlogo_dir}")
    print()

    # ── Build the patched model ───────────────────────────────────────────────
    experiment_xml = _build_experiment_xml(
        runs=args.runs,
        ticks=args.ticks,
        grassland_values=grassland_values,
        forage=args.forage,
        growth_rate=args.growth_rate,
        coop=args.coop,
        neg_r=args.neg_r,
        risk=args.risk,
        fairness_me=args.fairness_me,
        fairness_oth=args.fairness_oth,
    )

    original_content = model_path.read_text(encoding="utf-8")
    patched_content  = _inject_experiment(original_content, experiment_xml)

    # Write temp model next to the original (keeps relative paths intact)
    tmp_model = model_path.with_name("_baseline_sweep_tmp.nlogox")
    tmp_model.write_text(patched_content, encoding="utf-8")
    print(f"Temp model written to: {tmp_model}")

    table_path = model_path.parent / "baseline_sweep_table.csv"

    # ── Build the Java command directly (bypasses netlogo-headless.bat which
    # has a quoting bug when NetLogo is installed under "Program Files") ───────
    java_exe   = _find_java(netlogo_dir)
    nl_jar     = _find_netlogo_jar(netlogo_dir)
    s_nl       = _short_path(netlogo_dir)   # short path for all -D flags
    ext_dirs   = _find_extensions_dir(netlogo_dir)
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

    print(f"Java     : {java_exe}")
    print(f"NL jar   : {nl_jar.name}")
    print(f"Launching: {' '.join(cmd[:4])} ... org.nlogo.headless.Main --model ...\n")
    print("=" * 60)

    try:
        result = subprocess.run(cmd, check=False)
        print("=" * 60)
        if result.returncode == 0:
            print(f"\nDone. BehaviorSpace table : {table_path}")
            print(f"Per-run logs              : {model_path.parent / 'logs'}")
        else:
            print(f"\nNetLogo exited with code {result.returncode}.")
    except KeyboardInterrupt:
        print("\nInterrupted.")
    finally:
        tmp_model.unlink(missing_ok=True)
        print("Temp model cleaned up.")


# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────

def main() -> None:
    p = argparse.ArgumentParser(
        description="Batch baseline runs for MASTOC-LLM with varied random seeds.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              python run_baseline_sweep.py --runs 30
              python run_baseline_sweep.py --runs 20 --grassland 50,75,100
              python run_baseline_sweep.py --runs 10 --ticks 60 --forage 4
        """),
    )

    p.add_argument("--runs",         type=int,   default=30,
                   help="Repetitions per parameter combo (each gets a unique seed). Default: 30")
    p.add_argument("--ticks",        type=int,   default=120,
                   help="Max ticks per run. Default: 120")
    p.add_argument("--grassland",    type=str,   default="100",
                   help="Initial grassland %% — single value or comma-separated list. Default: 100")
    p.add_argument("--forage",       type=float, default=2.0,
                   help="Cow forage requirement. Default: 2")
    p.add_argument("--growth-rate",  type=float, default=0.001, dest="growth_rate",
                   help="Grass growth rate. Default: 0.001")
    p.add_argument("--coop",         type=float, default=1.0,
                   help="Cooperation level. Default: 1.0")
    p.add_argument("--neg-r",        type=float, default=0.0, dest="neg_r",
                   help="Negative reciprocity level. Default: 0.0")
    p.add_argument("--risk",         type=float, default=1.0,
                   help="Risk aversion level. Default: 1.0")
    p.add_argument("--fairness-me",  type=float, default=0.0, dest="fairness_me",
                   help="Fairness concerning me. Default: 0.0")
    p.add_argument("--fairness-oth", type=float, default=1.0, dest="fairness_oth",
                   help="Fairness concerning others. Default: 1.0")
    p.add_argument("--model",        type=str,   default="MASTOC-LLM.nlogox",
                   help="Path to .nlogox model file. Default: MASTOC-LLM.nlogox")
    p.add_argument("--netlogo-path", type=str,   default=None, dest="netlogo_path",
                   help='Path to NetLogo install dir, e.g. "C:/Program Files/NetLogo 7.0.4"')

    args = p.parse_args()
    run(args)


if __name__ == "__main__":
    main()
