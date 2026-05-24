# MASTOC-LLM Setup Guide

> Research question: Do Ostrom-style commons institutions emerge from language-capable agents under resource pressure?

---

## Quick-start (5 steps)

### 1. Install NetLogo 7.0.4

Download from [ccl.northwestern.edu/netlogo/download.shtml](https://ccl.northwestern.edu/netlogo/download.shtml).

**NetLogo 7.0.4 or later is required.** MASTOC-LLM uses the `.nlogox` format introduced in NetLogo 7, which is not backward-compatible with NetLogo 6.x. The model file is `MASTOC-LLM.nlogox`.

### 2. Install Python dependencies

```bash
pip install anthropic openai
pip install google-generativeai   # only if using Google Gemini
```

For running and analysing results:
```bash
pip install pandas matplotlib seaborn
```

### 3. Set your API key

**Anthropic (default backend):**
```
# Windows
set ANTHROPIC_API_KEY=sk-ant-...

# macOS / Linux
export ANTHROPIC_API_KEY=sk-ant-...
```

**OpenAI:**
```
set OPENAI_API_KEY=sk-...
```

**Google Gemini:**
```
set GOOGLE_API_KEY=...
```

**Ollama (local models — no key needed):**
```bash
# Install from https://ollama.com, then pull a model:
ollama pull llama3.2
# or for a remote server:
# the --ollama-url flag in run_baseline_sweep.py handles this
```

> The API key must be set in the environment that **launches NetLogo**, not in a separate terminal. On Windows, set it before opening NetLogo from the same PowerShell session.

### 4. Open and run in NetLogo

1. Open `MASTOC-LLM.nlogox` in NetLogo 7.0.4
2. Select a **Condition** (`baseline`, `full-gabm`, or `hybrid`)
3. For LLM conditions: select **Backend** and verify the **model name** input box
4. Click **Setup**, then **Simulation**

Logs write to `logs/` automatically. The `Data/` directory does not need to be created manually.

---

## File layout

```
MASTOC-LLM/
├── MASTOC-LLM.nlogox          NetLogo 7 model — open this in NetLogo
├── mastoc_llm_bridge.py       Python LLM bridge (auto-imported by NetLogo)
├── run_baseline_sweep.py      Headless batch sweep runner (baseline + LLM)
├── run_full_baseline_sweep.ps1  Pre-built comprehensive psychosocial sweep
├── experiment_runner.py       Analysis tool — merges logs, produces figures
├── config.json                Parameter reference
├── requirements.txt           Python dependencies
├── SETUP.md                   This file
├── baseline_results/          Per-condition CSVs from run_full_baseline_sweep.ps1
├── baseline_sweep_master.csv  Concatenated BehaviorSpace output
├── logs/                      Rich per-run CSV logs (created at runtime)
│   └── {run_id}/
│       ├── run_meta.json      Run metadata (condition, model, start time)
│       ├── resources.csv      Pool size, cows, pressure per tick
│       ├── decisions.csv      Agent decisions, reasoning, messages per tick
│       └── institutions.csv   Ostrom institution detection scores
└── Data/                      MASTOC-compatible flat-file outputs
```

---

## NetLogo interface controls

| Control | Type | Description |
|---|---|---|
| **Condition** | Chooser | `baseline` / `full-gabm` / `hybrid` |
| **Backend** | Chooser (per agent) | `anthropic` / `openai` / `google` / `ollama` |
| **Model name** | Input (per agent) | e.g. `claude-sonnet-4-6`, `llama3.2` |
| **num-llm-agents** | Slider | How many agents use LLM in hybrid mode (1–3) |
| **memory-length** | Slider | Rounds each agent remembers (0–15) |
| **communication?** | Switch | Whether agents can send messages to neighbours |
| **detect-institutions** | Switch | Run secondary Ostrom classifier each round |
| **institution-check-interval** | Slider | Run classifier every N ticks |

> **Which backend does the institution detector use?** The classifier always uses **agent 0's backend and model**. In a uniform run (all agents on the same provider) this is invisible. In a hypothetical mixed-backend run, the detector silently inherits agent 0's provider — there is currently no separate configuration for it.
| **cooperation-level** | Slider | Self-interest ↔ cooperative framing in prompt |
| **negative-reciprocity** | Slider | Retaliatory response to others removing cows |
| **positive-reciprocity** | Slider | Cooperative response to others removing cows |
| **risk-aversion-level** | Slider | Probability of downgrading ADD → KEEP |
| **fairness-concerning-me** | Slider | Envy weighting in payoff |
| **fairness-concerning-others** | Slider | Guilt weighting in payoff |
| **conformity-level** | Slider | Weight on matching neighbours' actions |

---

## Three experimental conditions

### Condition 1: Baseline
- All agents use the **rule-based best-response heuristic** — no LLM calls, no API cost
- Best response is computed by comparing the *mean* expected payoff across all possible neighbour-state combinations for each possible action (ADD / KEEP / REMOVE)
- Psychosocial parameters (cooperation, reciprocity, fairness, conformity, risk aversion) shift the payoff matrix exactly as in the original MASTOC model (Schindler, 2013)
- No Python bridge is initialised; runs at normal NetLogo speed
- Use `run_baseline_sweep.py` or `run_full_baseline_sweep.ps1` for headless batch runs

### Condition 2: Full GABM
- All 3 agents use the **LLM bridge** every tick
- Each agent receives: pool state, own herd, neighbour herds and actions, rolling memory of past N rounds, and incoming messages from neighbours
- Each agent returns: action (REMOVE / KEEP / ADD) plus an optional message to neighbours
- API cost: ~3 calls/tick × ticks × runs — use `run_baseline_sweep.py --condition full-gabm` to get a cost estimate before running

### Condition 3: Hybrid
- `num-llm-agents` agents (1–3) use the LLM; remaining agents are rule-based
- Rule-based agents still execute the psychosocial payoff heuristic; they cannot receive or act on messages
- Tests whether a coalition of language-capable agents can prevent tragedy when partnered with rule-based agents

---

## Running headless batch sweeps

For baseline runs (no API calls), the fastest path is `run_baseline_sweep.py`, which injects a BehaviorSpace experiment into a temporary copy of the model and invokes NetLogo's Java headless runner directly. This bypasses the quoting bug in `netlogo-headless.bat` on Windows and runs without opening the NetLogo GUI.

### Why direct Java invocation?

NetLogo 7 ships `netlogo-headless.bat` for running BehaviorSpace from the command line, but on Windows it fails when NetLogo is installed in a path containing spaces (e.g. `C:\Program Files\...`) because the batch file does not correctly quote the classpath argument. `run_baseline_sweep.py` works around this by:

1. Computing the 8.3 short path for the NetLogo installation directory using the Windows `GetShortPathNameW` API, which eliminates spaces from the path entirely.
2. Building and executing the Java command directly: `java ... org.nlogo.headless.Main --model ... --experiment ... --table ...`
3. Writing output to `baseline_sweep_table.csv` (BehaviorSpace table format) plus per-run logs under `logs/`.
4. Cleaning up the temporary `.nlogox` file after the run.

The `'py' extension not found` warning that appears in the console is harmless for baseline runs — the Python extension is declared in the model but never called in baseline mode. It will appear regardless and can be ignored.

### Basic baseline sweep

```powershell
# 30 runs at default parameters
python run_baseline_sweep.py

# Vary neg_r and pos_r
python run_baseline_sweep.py --runs 20 --neg-r 0.5 --pos-r 0.75

# Stop each run as soon as the commons collapses (<5% grassland)
python run_baseline_sweep.py --runs 30 --neg-r 1.0 --stop-on-collapse

# Multiple starting grassland levels in one sweep
python run_baseline_sweep.py --runs 20 --grassland 50,75,100
```

### Comprehensive psychosocial sweep

`run_full_baseline_sweep.ps1` runs six pre-designed sweep families covering the full psychosocial parameter space. It saves one CSV per condition to `baseline_results/` and concatenates all results into `baseline_sweep_master.csv`. Running time is approximately 60–90 minutes on a modern desktop.

```powershell
cd C:\path\to\MASTOC-LLM
.\run_full_baseline_sweep.ps1
```

The seven sweep families are:

| Sweep | What varies | Fixed | Conditions |
|---|---|---|---|
| A | `neg_r` 0.0 → 1.0 in 0.1 steps | `pos_r=1.0` | 11 |
| B | `pos_r` 0.0 → 1.0, at `neg_r`=0 and 0.5 | — | 10 |
| C | `neg_r` × `pos_r` full 5×5 grid | — | 25 |
| D | `risk` 0.0 → 1.0 in 0.1 steps | `neg_r=0` | 11 |
| E | `conformity` × `neg_r` (0, 0.5, 1.0) | — | 15 |
| F | `grassland` (50, 75, 100) × `neg_r` | — | 15 |
| G | `risk` × `neg_r` (boundary region: 0.75–1.0) | `pos_r=1.0` | 20 |

Total: 107 conditions × 20 runs = 2,140 runs.

Sweep G specifically addresses whether risk aversion shifts the `pos_r > neg_r` collapse threshold. Sweeps A and D establish that risk has no effect at the safe interior (neg_r=0) and that the transition starts around neg_r=0.8; Sweep G tests whether risk can widen the stable zone at the boundary.

### LLM conditions

`run_baseline_sweep.py` also supports `full-gabm` and `hybrid` conditions. For these, a cost estimate is printed and you must confirm before the sweep launches.

```powershell
# Full-GABM with Claude Sonnet (shows cost estimate first)
python run_baseline_sweep.py --condition full-gabm --runs 10 `
    --backend anthropic --llm-model claude-sonnet-4-6

# Hybrid: 1 LLM agent, remote Ollama server (no API cost)
python run_baseline_sweep.py --condition hybrid --num-llm-agents 1 `
    --backend ollama --llm-model gemma3:27b `
    --ollama-url http://192.168.86.26:11434/v1 --yes
```

Pass `--yes` to skip the confirmation prompt (useful for scripted pipelines). For LLM conditions, the script automatically sets `sequentialRunOrder=true` and `--threads 1` to prevent concurrent API calls from colliding.

Pass `--verbose` (or `-v`) to stream NetLogo's print/show output live — the equivalent of watching the Command Center during a GUI run. This also enables per-agent bridge logging (connection attempts, token counts, response timing). Without `--verbose`, NetLogo stdout is captured silently and only shown if the process exits with an error. This flag is strongly recommended when running LLM conditions for the first time or debugging unexpected behaviour.

```powershell
# LLM run with live output
python run_baseline_sweep.py --condition full-gabm --runs 3 `
    --backend ollama --llm-model deepseek-r1:32b `
    --ollama-url http://192.168.86.26:11434/v1 --verbose
```

### All flags

| Flag | Default | Description |
|---|---|---|
| `--condition` | `baseline` | `baseline`, `full-gabm`, or `hybrid` |
| `--backend` | `anthropic` | LLM backend: `anthropic`, `openai`, `ollama` |
| `--llm-model` | `claude-sonnet-4-6` | Model name |
| `--num-llm-agents` | 1 | LLM agents in hybrid mode (1–3) |
| `--runs N` | 30 | Repetitions per parameter combo |
| `--ticks T` | 120 | Max ticks per run |
| `--stop-on-collapse` | off | End each run when grassland drops below 5% |
| `--yes` / `-y` | off | Skip cost confirmation prompt |
| `--verbose` / `-v` | off | Stream NetLogo print/show output live (Command Center equivalent) and enable per-agent LLM logging (connection, tokens, timing). Without this flag, NetLogo stdout is captured silently and only surfaced on failure. |
| `--grassland G` | 100 | Initial grassland % (comma-separated for sweep) |
| `--coop F` | 1.0 | Cooperation level |
| `--neg-r F` | 0.0 | Negative reciprocity |
| `--pos-r F` | 1.0 | Positive reciprocity |
| `--risk F` | 1.0 | Risk aversion |
| `--fairness-me F` | 0.0 | Fairness concerning self |
| `--fairness-oth F` | 1.0 | Fairness concerning others |
| `--conformity F` | 0.0 | Conformity level |
| `--memory-length N` | 5 | Agent memory length (used in LLM cost estimate) |
| `--forage F` | 2.0 | Cow forage requirement |
| `--ollama-url URL` | `http://localhost:11434/v1` | Ollama server base URL |
| `--netlogo-path PATH` | auto | NetLogo install directory |

---

## Understanding the outputs

### BehaviorSpace table (`baseline_sweep_table.csv`)

Standard NetLogo BehaviorSpace CSV format. Each row is one tick of one run. Contains all parameter values as columns (as configured in the experiment) plus the metrics reported each tick:

| Metric | Description |
|---|---|
| `count patches with [pcolor = green - 2]` | Green patches remaining (max 1089) |
| `count cows` | Total herd size across all agents |
| `pressure` | Fraction of patches grazed this tick |
| `count cows with [owner = human N]` | Individual herd sizes for agents 0, 1, 2 |

### Per-run logs (`logs/{run_id}/`)

LLM conditions additionally write rich per-run logs:

**`resources.csv`**

| Column | Description |
|---|---|
| `tick` | Simulation step |
| `pool_pct` | Grassland health as % of maximum |
| `total_cows`, `agent0_cows` … `agent2_cows` | Herd sizes |
| `pressure` | Grazing pressure (0–1) |

**`decisions.csv`**

| Column | Description |
|---|---|
| `action_name` | REMOVE / KEEP / ADD |
| `message` | Agent's outgoing message to neighbours |
| `reasoning` | Full LLM chain-of-thought |
| `payoff_add/keep/remove` | Payoff forecasts used in the prompt |

**`institutions.csv`**

| Column | Description |
|---|---|
| `institution_score` | 0–10 score of institutional activity this round |
| `categories` | NORM_PROPOSAL, SANCTION, COORDINATION, DEFECTION, TRUST_BUILDING |
| `round_summary` | One-sentence narrative from the secondary classifier |

### Analysing results

```bash
python experiment_runner.py --mode analyse
```

Reads both `logs/` (LLM runs) and `Data/` (legacy flat files) and produces merged CSVs and figures in `figures/`.

---

## Key findings from baseline psychosocial sweep

A comprehensive sweep of 1,740 baseline runs across 87 parameter combinations reveals a clean stability condition grounded directly in the corrected payoff formula.

**The stability rule: `pos_r > neg_r`**

The collapse rate across the `neg_r × pos_r` grid follows an almost perfectly sharp boundary:

| | pos_r=0 | pos_r=0.25 | pos_r=0.50 | pos_r=0.75 | pos_r=1.0 |
|---|---|---|---|---|---|
| **neg_r=0.00** | 100% | 0% | 0% | 0% | 0% |
| **neg_r=0.25** | 100% | 100% | 0% | 0% | 0% |
| **neg_r=0.50** | 100% | 100% | 100% | 0% | 0% |
| **neg_r=0.75** | 100% | 100% | 100% | 100% | ~1% |
| **neg_r=1.00** | 100% | 100% | 100% | 100% | 100% |

When `pos_r > neg_r`, collapse rate is 0% (or ~1% at the extreme near-boundary). When `pos_r ≤ neg_r`, collapse rate is 100%. The stability condition maps directly onto Ostrom's account: cooperative reciprocity must dominate retaliatory reciprocity for self-governance to emerge.

**The neg_r threshold at pos_r=1.0** is between 0.8 (10% collapse) and 0.9 (45% collapse), reflecting the stochastic boundary where both forces are near-equal.

**Risk aversion has no independent effect.** Sweeping risk aversion from 0.0 to 1.0 with neg_r=0 and pos_r=1.0 produces 0% collapse at every level with an identical equilibrium of 9 cows. Risk aversion modulates the speed of herd adjustment but does not determine whether the commons is sustainable.

**Conformity amplifies instability at moderate neg_r.** At neg_r=0.5, conformity=0 produces 0% collapse; conformity=0.75 produces 35% collapse. At neg_r=1.0, high conformity slightly reduces collapse (75% vs 100%) — consistent with conformity dampening the retaliation spiral when collapse is otherwise certain.

**Starting grassland level does not change qualitative outcome.** Under neg_r=1.0, collapse occurs at 100% probability regardless of whether grass starts at 50%, 75%, or 100% — only the timing differs (~47 ticks from 50% start vs ~38 ticks from 100% start).

---

## Running LLM agents without a local GPU (free via Kaggle)

If you don't have a GPU-equipped machine available, you can run the LLM conditions for free using [Kaggle](https://www.kaggle.com) -- Google's data-science platform -- as a remote Ollama server, accessed via ngrok. The free tier gives you **30 GPU hours per week** (NVIDIA T4 × 2, 32 GB VRAM combined), which is enough to run substantial full-GABM or hybrid sweeps. Each session can run for up to 12 hours before timing out.

The architecture is: Kaggle notebook runs Ollama → ngrok exposes it as a public URL → MASTOC-LLM's `--ollama-url` flag points at that URL. No API key, no cost.

### What you need

1. A [Kaggle account](https://www.kaggle.com) — sign up with email or Google. **Verify your phone number** to unlock GPU access (required).
2. An [ngrok account](https://ngrok.com) — free tier is sufficient. After signing up, copy your **auth token** from the ngrok dashboard.

### Step 1 — Create a Kaggle notebook

In Kaggle, click **New → Notebook**. Give it a name (e.g. `mastoc-ollama`).

Under **Settings → Accelerator**, select **GPU T4 × 2**. This gives you 32 GB of VRAM — enough for models up to ~27B parameters in 4-bit quantisation.

### Step 2 — Add the notebook code cells

Kaggle adds a placeholder Python cell by default. Replace it with the following four cells, running each one in order by clicking the ▶ button beside it.

**Cell 1 — Install dependencies:**
```python
!apt-get install -y zstd
!pip install pyngrok
!curl -fsSL https://ollama.com/install.sh | sh
```

**Cell 2 — Authenticate ngrok** (replace the token with yours):
```python
from pyngrok import ngrok
ngrok.set_auth_token("paste-your-ngrok-auth-token-here")
```

**Cell 3 — Start Ollama and pull a model:**
```python
import subprocess, time, os
os.environ["OLLAMA_HOST"] = "0.0.0.0"
os.environ["OLLAMA_ORIGINS"] = "*"
subprocess.Popen(["ollama", "serve"])
time.sleep(5)
!ollama pull llama3.2
```

Replace `llama3.2` with whichever model you want to run. Any model listed on [ollama.com/library](https://ollama.com/library) works — for example `deepseek-r1:32b`, `gemma3:27b`, or `llama3.2:3b`. Kaggle's 1–2 GBps download speeds make even large model pulls fast.

**Cell 4 — Get the public URL:**
```python
import subprocess, time, requests
subprocess.Popen(["ngrok", "http", "11434", "--request-header-add", "ngrok-skip-browser-warning:true"])
time.sleep(3)
tunnels = requests.get("http://localhost:4040/api/tunnels").json()
print(tunnels["tunnels"][0]["public_url"])
```

This prints a URL like `https://abc123.ngrok-free.app`. **Copy it** — this is your Ollama endpoint.

### Step 3 — Point MASTOC-LLM at the Kaggle server

Use the `--ollama-url` flag with the URL printed in Cell 4:

```powershell
# Full-GABM sweep using the Kaggle-hosted model
python run_baseline_sweep.py --condition full-gabm --runs 5 `
    --backend ollama --llm-model llama3.2 `
    --ollama-url https://abc123.ngrok-free.app --yes

# Hybrid condition with a larger model
python run_baseline_sweep.py --condition hybrid --num-llm-agents 1 `
    --backend ollama --llm-model deepseek-r1:32b `
    --ollama-url https://abc123.ngrok-free.app --yes
```

The model name in `--llm-model` must match what you pulled in Cell 3.

For interactive GUI runs, open `MASTOC-LLM.nlogox` in NetLogo, set **Backend** to `ollama`, and paste the ngrok URL into the **Ollama URL** input field.

### Practical notes

- **Session limit.** Each Kaggle session runs for up to 12 hours before timing out. When it times out, Cell 4 will give you a new ngrok URL — update `--ollama-url` accordingly for subsequent runs.
- **Weekly quota.** The free tier provides 30 GPU hours per week. CPU usage is unlimited and unmetered. Baseline sweeps (no LLM calls) run fine without touching the GPU quota.
- **Cost.** Ollama runs are always free — the `run_baseline_sweep.py` cost estimator reports $0.00 for Ollama backends, so you can pass `--yes` to skip the confirmation prompt.
- **Model size limit.** The T4 × 2 configuration provides 32 GB of VRAM combined. In practice this caps you at roughly **32B-parameter models in 4-bit quantisation** (e.g. `deepseek-r1:32b`, `gemma3:27b`). Larger models (70B+) will fail to load. Smaller models (`llama3.2:3b`, `llama3.2`, `gemma3:4b`) run comfortably and generate tokens faster. Check the model's listed size on [ollama.com/library](https://ollama.com/library) before pulling.
- **Keeping the session alive.** Kaggle notebooks time out if left idle. If you're running a long sweep headlessly, the session will stay active as long as a cell is executing.

---

## Troubleshooting

**`'py' extension not found` warning**
Harmless for baseline runs. NetLogo loads all declared extensions at startup; the Python extension is declared in the model but never called during baseline. Ignore this warning.

**NetLogo doesn't find the model / `file not found` error**
Ensure you run `run_baseline_sweep.py` from the same directory as `MASTOC-LLM.nlogox`, or pass `--model path/to/MASTOC-LLM.nlogox` explicitly.

**`py:python3` not found (GUI runs)**
NetLogo can't locate your Python 3 install. Set the path in NetLogo preferences: Edit → Preferences → Python path → point to your `python3` executable.

**`import mastoc_llm_bridge` fails**
The bridge file must be in the **same directory** as `MASTOC-LLM.nlogox`. NetLogo sets its working directory to the model's folder on load.

**`ANTHROPIC_API_KEY` not set / authentication error**
Set the environment variable before launching NetLogo. On Windows, set it in the same PowerShell session that opens NetLogo.

**Ollama connection refused**
Ensure Ollama is running (`ollama serve`) and the model is pulled (`ollama pull modelname`). For a remote server, verify the URL with `--ollama-url http://host:11434/v1`.

**`Cannot remove item ... being used by another process` (PowerShell sweep)**
NetLogo hasn't released the CSV file handle yet. The sweep script retries up to 5 times with 500ms delays — if it still fails, the individual CSV has already been copied to `baseline_results/` so no data is lost. The master concatenation may be missing that condition's rows; re-run just that condition if needed.

**NetLogo 6.x / `.nlogo` file**
MASTOC-LLM targets NetLogo 7.0.4. The `.nlogox` format is not backward-compatible with NetLogo 6. If you must use NetLogo 6, the legacy `.nlogo` file may be available in earlier releases but is no longer maintained.

---

## Citation

If you use this model in your research, please cite:

```
Julia Schindler (2013, April 27). “MASTOC - A Multi-Agent System of the Tragedy Of The Commons” (Version 1.1.0). CoMSES Computational Model Library.
Retrieved from: https://www.comses.net/codebases/2283/releases/1.1.0/

Jimenez-Romero, C. et al. (2025). Multi-agent systems powered by large language models.
Frontiers in Artificial Intelligence. https://doi.org/10.3389/frai.2025.1593017
```
