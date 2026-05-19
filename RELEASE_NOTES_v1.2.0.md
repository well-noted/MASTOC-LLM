# MASTOC-LLM v1.2.0 — Release Notes

## Summary

This release corrects a mathematical error in the baseline best-response decision rule, upgrades the batch sweep runner to support LLM conditions with cost estimation, and documents the first systematic psychosocial parameter sweep of the corrected baseline.

---

## Breaking change: baseline best-response decision rule corrected (`min` → `mean`)

**What changed.** The `rule-based-decide` procedure in `MASTOC-LLM.nlogox` evaluated the payoff of each possible action (ADD / KEEP / REMOVE) by taking the *minimum* payoff across all neighbour-state combinations in its adj-list. This implemented worst-case (maximin) reasoning rather than the expected-value best-response assumed by the original MASTOC model (Schindler, 2013). The fix replaces `min` with `mean`, so each action is evaluated by its *expected* payoff under the current neighbour distribution.

**Why it matters.** Under the previous rule, baseline agents always chose REMOVE regardless of resource state — not because the commons logic drove them there, but because REMOVE had the least-bad worst case in all configurations. This meant the baseline was not a valid control condition for LLM comparisons: it did not represent a rational-but-non-communicating agent; it represented an agent hard-wired to deplete regardless of context. The corrected rule produces a genuine best-response agent whose behavior depends on psychosocial parameters in the way the original MASTOC model intended.

**Effect on existing results.** The growth rate sweep and risk aversion tables published in v1.1.0 were collected under the original pure-payoff maximizer implementation (before psychosocial adjustment was added). Those results remain valid as control data for that implementation, but are not directly comparable to v1.2.0 baseline runs.

---

## New: baseline psychosocial parameter sweep

A systematic sweep of 18 psychosocial parameter combinations (20 replications per condition, ~131 total runs) confirms that the corrected baseline expresses the full Ostrom spectrum from institutional success to tragedy depending on parameter settings.

Key findings:

- **`neg_r=1.0` (high negative reciprocity) → 100% collapse** across all cooperation levels. Retaliatory reciprocity produces a race-to-REMOVE equilibrium in which each agent's best response to others removing is also to remove, depleting the resource rapidly.
- **Default parameters (`pos_r=1.0`, `neg_r=0.0`, `risk=1.0`) → 0% collapse**, sustainable K=9 equilibrium. Cooperative reciprocity rewards collective restraint; risk aversion provides an additional brake on ADD decisions.
- **`neg_r=0.5`, `coop=0.5` → 0% collapse, ~25 cows/agent** — the most productive sustainable baseline condition found. Moderate retaliatory sensitivity prevents free-riding without triggering a collapse spiral.
- **`risk=0`, `fair_oth=0` → 100% collapse** even at `neg_r=0`. Risk aversion is a structural stabiliser, not a peripheral parameter: disabling it (alongside fairness-toward-others) eliminates all brakes on ADD and produces tragedy regardless of cooperation level.

The corrected baseline is now a theoretically grounded Ostrom instrument: outcome varies systematically with psychosocial parameters in ways that map onto Ostrom's (1990) conditions for commons governance success and failure.

---

## Upgraded: `run_baseline_sweep.py`

The batch sweep runner has been substantially expanded. New capabilities:

**LLM condition support.** The `--condition` flag now accepts `baseline` (rule-based, no API cost), `full-gabm` (all 3 agents use an LLM), and `hybrid` (N LLM agents, rest rule-based via `--num-llm-agents`). For LLM conditions, the script sets `sequentialRunOrder="true"` and `--threads 1` in the BehaviorSpace invocation to prevent concurrent API calls.

**API cost estimator.** Before launching any LLM condition run, the script calculates and displays an estimated API cost based on run count, tick count, number of LLM agents, memory length, and the selected model's published per-token pricing. The estimate covers known Anthropic and OpenAI models; unknown models fall back to a mid-tier estimate with a warning. The user must confirm before the sweep launches. Pass `--yes` / `-y` to skip for scripting.

**Early-exit on collapse (`--stop-on-collapse`).** Injects a BehaviorSpace `<exitCondition>` that terminates each run as soon as grassland patches drop below 5%, saving time and API cost on parameter combinations that collapse quickly.

**Remote Ollama support (`--ollama-url`).** LLM sweeps can target an Ollama server on the local network rather than localhost. The URL is injected as a BehaviorSpace constant and picked up by the bridge at runtime. Ollama runs are always counted as $0 in the cost estimator.

**New psychosocial flags:** `--pos-r` (positive reciprocity, default 1.0) and `--risk` (risk aversion, default 1.0) are now exposed as CLI arguments, bringing the sweep script to full coverage of the psychosocial parameter space.

**Complete flag reference:**

| Flag | Default | Description |
|---|---|---|
| `--condition` | `baseline` | `baseline`, `full-gabm`, or `hybrid` |
| `--backend` | `anthropic` | `anthropic`, `openai`, or `ollama` |
| `--llm-model` | `claude-sonnet-4-6` | Model name |
| `--num-llm-agents` | 1 | LLM agents in hybrid mode (1–3) |
| `--runs N` | 30 | Repetitions per parameter combo |
| `--ticks T` | 120 | Max ticks per run |
| `--stop-on-collapse` | off | Exit each run at <5% grassland |
| `--yes` / `-y` | off | Skip cost confirmation |
| `--grassland G` | 100 | Initial grassland % (comma-separated for sweep) |
| `--coop F` | 1.0 | Cooperation level |
| `--neg-r F` | 0.0 | Negative reciprocity |
| `--pos-r F` | 1.0 | Positive reciprocity |
| `--risk F` | 1.0 | Risk aversion |
| `--fairness-me F` | 0.0 | Fairness concerning self |
| `--fairness-oth F` | 1.0 | Fairness concerning others |
| `--memory-length N` | 5 | Used for LLM cost estimate |
| `--forage F` | 2.0 | Cow forage requirement |
| `--ollama-url URL` | `http://localhost:11434/v1` | Ollama server URL |
| `--netlogo-path PATH` | auto | NetLogo install directory |

---

## Files changed

| File | Change |
|---|---|
| `MASTOC-LLM.nlogox` | `min` → `mean` in `rule-based-decide` (3 lines in adj-list comparisons) |
| `run_baseline_sweep.py` | Full rewrite: LLM conditions, cost estimator, `--stop-on-collapse`, `--ollama-url`, `--pos-r`, `--risk` |
| `README.md` | Updated baseline section with fix description and sweep results; updated Quick Start with new CLI flags |

---

## Recommended citation

Schindler, J., & (MASTOC-LLM contributors). MASTOC-LLM: A multi-agent system of the Tragedy of the Commons with LLM-powered agents. CoMSES Computational Model Library, v1.2.0.
