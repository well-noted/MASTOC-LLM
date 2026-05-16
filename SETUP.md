# MASTOC-LLM Setup Guide

> CAS 520 — Agent-Based Modeling | Arizona State University  
> Research question: Do Ostrom-style commons institutions emerge from language-capable agents under resource pressure?

---

## Quick-start (5 steps)

### 1. Install NetLogo 6.4

Download from [ccl.northwestern.edu/netlogo/download.shtml](https://ccl.northwestern.edu/netlogo/download.shtml).  
**NetLogo 6.2 or later is required** — the `py` extension that bridges to Python was not available in the original MASTOC's NetLogo 4.0.2.

### 2. Install Python dependencies

```bash
pip install anthropic openai pandas matplotlib seaborn
```

For headless batch runs (optional):
```bash
pip install pynetlogo jpype1
```

### 3. Set your API key

**Anthropic (default backend):**
```bash
# Windows
set ANTHROPIC_API_KEY=sk-ant-...

# macOS / Linux
export ANTHROPIC_API_KEY=sk-ant-...
```

**Ollama (local models — no key needed):**
```bash
# Install Ollama from https://ollama.com, then pull a model:
ollama pull llama3.2
# Ollama starts an OpenAI-compatible endpoint at localhost:11434
```

### 4. Create the required output directory

```bash
mkdir Data
mkdir logs
```

### 5. Open and run in NetLogo

1. Open `MASTOC-LLM.nlogo` in NetLogo 6.4
2. Select a **Condition** (`baseline`, `full-gabm`, or `hybrid`)
3. Select **LLM Backend** (`anthropic` or `ollama`)
4. Verify model name in the **anthropic-model-name** or **ollama-model-name** box
5. Click **Setup**, then **Simulation**

---

## File layout

```
MASTOC-LLM/
├── MASTOC-LLM.nlogo          NetLogo model (open this in NetLogo)
├── mastoc_llm_bridge.py      Python LLM bridge (auto-imported by NetLogo)
├── experiment_runner.py      Batch runner + analysis tool
├── config.json               Parameter reference / documentation
├── requirements.txt          Python dependencies
├── SETUP.md                  This file
├── Data/                     MASTOC-compatible flat-file outputs (create manually)
└── logs/                     Rich CSV outputs (created automatically)
    └── {run_id}/
        ├── run_meta.json     Run metadata (condition, model, start time)
        ├── resources.csv     Pool size, cows, pressure per tick
        ├── decisions.csv     Agent decisions, reasoning, messages per tick
        └── institutions.csv  Ostrom institution detection scores
```

---

## NetLogo interface controls

| Control | Type | Description |
|---|---|---|
| **Condition** | Chooser | `baseline` / `full-gabm` / `hybrid` |
| **LLM Backend** | Chooser | `anthropic` / `ollama` |
| **anthropic-model-name** | Input | e.g. `claude-sonnet-4-6` |
| **ollama-model-name** | Input | e.g. `llama3.2` |
| **hybrid-fraction** | Slider | Fraction of agents that are LLM-based (0–1) |
| **memory-length** | Slider | Rounds each agent remembers (1–10) |
| **detect-institutions** | Switch | Run secondary Ostrom classifier each round |
| **institution-check-interval** | Slider | Run classifier every N ticks |
| *All MASTOC sliders* | Sliders | fairness, cooperation, reciprocity, conformity, risk-aversion |

---

## Three experimental conditions

### Condition 1: Baseline
- All agents use the **rule-based best-response heuristic** — no LLM calls
- Reproduces the classical Tragedy of the Commons as a control
- No Python bridge is initialised; runs at normal NetLogo speed
- Key expected outcome: grazing pressure → 1.0, grass depleted by ~tick 30–50

### Condition 2: Full GABM
- All 3 agents use the **LLM bridge** every tick
- Each agent receives: pool state, own herd, neighbour actions, rolling 5-round memory, and any incoming messages
- Each agent returns: action (−1/0/+1) and an optional message to neighbours
- LLM cost: ~3 calls/tick × 120 ticks × N repetitions
- Key research question: does the pool survive? Do norms emerge in messages?

### Condition 3: Hybrid
- `hybrid-fraction` of agents (default 1/3 → 1 agent) use the LLM
- Rule-based agents still log to the Python bridge for consistent output
- Tests whether a single "institutional entrepreneur" LLM agent shifts the equilibrium
- Comparable to Ostrom's finding that heterogeneous groups can self-organise

---

## Understanding the outputs

### `resources.csv`
| Column | Description |
|---|---|
| `tick` | Simulation step |
| `pool_patches` | Remaining green patches |
| `pool_pct` | % of max patches still green |
| `total_cows` | Total herd size across all agents |
| `pressure` | Fraction of patches grazed (0–1) |
| `agent0_cows` … `agent2_cows` | Individual herd sizes |

### `decisions.csv`
| Column | Description |
|---|---|
| `tick`, `agent_id` | When and who |
| `action` | −1 / 0 / 1 (remove / keep / add) |
| `action_name` | REMOVE / KEEP / ADD |
| `message` | Agent's outgoing message to neighbours |
| `reasoning` | Full LLM chain-of-thought (for qualitative coding) |
| `pool_pct` | Pool state seen by this agent this tick |
| `payoff_add/keep/remove` | Payoff forecasts used in the prompt |

### `institutions.csv`
| Column | Description |
|---|---|
| `tick` | When the detection ran |
| `institution_score` | 0–10 score of institutional activity this round |
| `categories` | Pipe-delimited: NORM_PROPOSAL, SANCTION, COORDINATION, DEFECTION, TRUST_BUILDING |
| `round_summary` | One-sentence narrative from the classifier |

**Ostrom institution categories:**
- `NORM_PROPOSAL` — agent proposes a rule, limit, or fair-share arrangement
- `SANCTION` — agent threatens, warns, or criticises over-use
- `COORDINATION` — non-binding call to act together ("let's all cut back")
- `DEFECTION` — agent announces or justifies adding cows despite pressure
- `TRUST_BUILDING` — expressions of goodwill, reciprocity commitment, praise

---

## Running experiments

### Option A: NetLogo GUI (recommended for development)
Run each condition manually. After each run, `logs/` will contain a new `{run_id}/` folder.

### Option B: BehaviorSpace XML (recommended for replication)
```bash
python experiment_runner.py --mode xml
# Produces: behaviourspace.xml
# In NetLogo: Tools → BehaviorSpace → Import → behaviourspace.xml
```

### Option C: Headless via pynetlogo (batch runs)
```bash
pip install pynetlogo jpype1
python experiment_runner.py --mode run --netlogo-path "C:/Program Files/NetLogo 6.4.0"
```

### Analyse results
```bash
python experiment_runner.py --mode analyse --log-dir logs
# Produces: results_resources.csv, results_institutions.csv
#           figures/resource_dynamics.png, figures/institution_emergence.png
```

### Estimate API cost before running
```bash
python experiment_runner.py --mode cost
```

---

## Troubleshooting

**`py:python3` not found**  
NetLogo can't locate your Python 3 install. Set the path in NetLogo preferences:  
Edit → Preferences → Python path → point to your `python3` executable.

**`import mastoc_llm_bridge` fails**  
The bridge file must be in the **same directory** as `MASTOC-LLM.nlogo`. NetLogo sets its working directory to the model's folder on load, and the bridge's `sys.path.insert(0, os.getcwd())` relies on this.

**`ANTHROPIC_API_KEY` not set / authentication error**  
Set the environment variable before launching NetLogo (the variable must be set in the shell that launches NetLogo, not in a separate terminal).

**Ollama connection refused**  
Ensure Ollama is running (`ollama serve` in a terminal) and the model is pulled (`ollama pull llama3.2`).

**`Data/` directory not found**  
Create `Data/` manually in the same folder as the `.nlogo` file before clicking Setup.

**NetLogo 4.0.2 compatibility**  
The original MASTOC ran on NetLogo 4.0.2 and used the `nash` extension. MASTOC-LLM targets **NetLogo 6.4** and replaces the Nash solver with a Python best-response heuristic (baseline) or LLM calls (GABM/hybrid). The `.nlogo` file will not open correctly in NetLogo 4.

---

## Connecting to your scientific question

To test whether Ostrom's institutions emerge, look for:

1. **Pool survival** — does `pool_pct` in `resources.csv` stay above 0 in Full GABM vs collapse in Baseline?

2. **Norm proposals** — search `decisions.csv` for rows where `message` contains "limit", "rule", "fair", "agree", "maximum"

3. **Institution score trajectory** — plot `institution_score` from `institutions.csv` over ticks. Does it rise as the pool declines (crisis-driven institution formation)?

4. **Behavioural convergence** — do agents' actions synchronise after norm proposals? Look for runs of consecutive REMOVE or KEEP actions across all agents.

5. **Hybrid leverage** — in condition 3, does the single LLM agent's message content influence the rule-based agents' payoff structure? (Rule-based agents see LLM-agent herds; if the LLM agent consistently removes cows, others face higher relative payoffs for keeping.)

---

## Citation

If you use this model in your research, please cite both:

```
Bais, A. et al. (2023). MASTOC v1.1.0. CoMSES Computational Model Library.
https://www.comses.net/codebases/2283/releases/1.1.0/

Jimenez-Romero, C. et al. (2025). Multi-agent systems powered by large language models.
Frontiers in Artificial Intelligence. https://doi.org/10.3389/frai.2025.1593017
```
