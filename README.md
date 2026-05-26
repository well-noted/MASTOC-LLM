# MASTOC-LLM

**Multi-Agent System Tragedy of the Commons -- with Large Language Model Agents**

> Extending [MASTOC v1.1.0](https://www.comses.net/codebases/2283/releases/1.1.0/) (Schindler, 2013)

---

## What is this?

The classic MASTOC commons model gives its agents a payoff calculator and nothing else: no memory of past rounds, no capacity to explain a decision, no way to hear what a neighbor thinks. Every decision is computed fresh, in isolation, and then forgotten.

**MASTOC-LLM replaces that architecture with large language model (LLM) agents.**

Each reads the current state of the shared grassland, observes what its neighbors did, recalls a rolling memory of prior rounds, and -- critically -- communicates in natural language before deciding whether to add, keep, or remove a cow.

One question drives the project:

> *Do Ostrom-style commons institutions -- norms, coordination, sanctioning -- emerge spontaneously from language-capable agents under resource pressure?*

![MASTOC-LLM simulation demo](assets/mastoc_demo.gif)

---

## Contents

- [What is this?](#what-is-this)
- [Background](#background)
  - [Ostrom's Design Principles -- applicability to this model](#ostroms-design-principles----applicability-to-this-model)
- [How it works](#how-it-works)
  - [How personality parameters reach the LLM](#how-personality-parameters-reach-the-llm)
  - [The cost function and grassland dynamics](#the-cost-function-and-grassland-dynamics)
- [Repository structure](#repository-structure)
- [Quick start](#quick-start)
  - [Batch sweeps (baseline and LLM conditions)](#batch-sweeps-baseline-and-llm-conditions)
- [Experimental conditions](#experimental-conditions)
- [Collapse pattern taxonomy](#collapse-pattern-taxonomy)
  - [Pattern I -- Cooperative Paralysis](#pattern-i----cooperative-paralysis)
  - [Pattern II -- Defection Cascade](#pattern-ii----defection-cascade)
  - [Pattern III -- Overshoot-Panic](#pattern-iii----overshoot-panic)
  - [Pattern IV -- Hybrid Architecture Failure](#pattern-iv----hybrid-architecture-failure)
- [Preliminary results](#preliminary-results)
  - [Summary across conditions](#summary-across-conditions)
  - [Baseline: the Ostrom spectrum under psychosocial parameters](#baseline-the-ostrom-spectrum-under-psychosocial-parameters)
  - [Baseline psychosocial parameter sweep (v1.2.0)](#baseline-psychosocial-parameter-sweep-v120)
  - [Full-GABM: cooperative convergence](#full-gabm-cooperative-convergence-coop1-defaults----claude-sonnet-46)
  - [Hybrid: the limits of a single institutional entrepreneur](#hybrid-the-limits-of-a-single-institutional-entrepreneur----claude-sonnet-46)
  - [Hybrid (2 LLM): coalition formation, delayed tragedy](#hybrid-2-llm-coalition-formation-delayed-tragedy----claude-sonnet-46)
  - [Hybrid (LLM-advantaged): herd position doesn't change structural outcome](#hybrid-llm-advantaged-herd-position-doesnt-change-structural-outcome)
  - [Full-GABM (low guilt + low envy): fairness parameters shape cooperation quality](#full-gabm-low-guilt--low-envy-fairness-parameters-shape-cooperation-quality)
  - [Full-GABM (low cooperation): cooperation is robust to personality framing](#full-gabm-low-cooperation-cooperation-is-robust-to-personality-framing)
  - [Scarce commons: rapid recovery across personality conditions](#scarce-commons-rapid-recovery-across-personality-conditions)
  - [Full-GABM (Llama 3.2 3B): cooperative surface, no institutional depth](#full-gabm-llama-32-3b-cooperative-surface-no-institutional-depth)
  - [gpt-5.4-mini: KEEP-dominance across fairness configurations](#gpt-54-mini-keep-dominance-across-fairness-configurations)
  - [gpt-4o-mini: cooperative noise](#gpt-4o-mini-cooperative-noise----oscillatory-behavior-and-over-removal-under-cooperative-pressure)
  - [gpt-5.5: cooperation level governs fate](#gpt-55-cooperation-level-governs-fate-model-can-succeed-or-collapse-from-the-same-starting-point)
  - [gpt-5.5 amnesiac: equalization locks without memory](#gpt-55-amnesiac-equalization-locks-without-memory)
  - [DeepSeek R1:32b: reasoning model, KEEP-dominant behavior](#deepseek-r132b-reasoning-model-keep-dominant-behavior)
  - [gemma4:e4b: KEEP-dominant stasis, then overshoot-panic at mid cooperation](#gemma4e4b-keep-dominant-stasis-then-overshoot-panic-at-mid-cooperation)
  - [qwen2.5:14b: KEEP-dominant survival across cooperation levels](#qwen2514b-keep-dominant-survival-across-cooperation-levels)
  - [Thinking traces: what the deliberation reveals](#thinking-traces-what-the-deliberation-reveals)
    - [DeepSeek R1:32b: payoff-personality deadlock](#deepseek-r132b-payoff-personality-deadlock)
    - [gemma4:e4b: payoff maximization and social conformism](#gemma4e4b-payoff-maximization-and-social-conformism)
    - [Claude Haiku 4.5: trajectory-conditional reasoning](#claude-haiku-45-trajectory-conditional-reasoning)
    - [OpenAI gpt-5.4-mini: self-reported reasoning and the faithfulness problem](#openai-gpt-54-mini-self-reported-reasoning-and-the-faithfulness-problem)
  - [Claude Sonnet: mid cooperation and high negative reciprocity](#claude-sonnet-mid-cooperation-replicates-overshoot-panic-negative-reciprocity-produces-fastest-equalization)
  - [Cross-model comparison: neg\_r = 1](#cross-model-comparison-negr--1-with-gpt-55-produces-stability-but-not-equality)
  - [Memory and communication sweep: amnesiac vs. equipped agents](#memory-and-communication-sweep-amnesiac-vs-equipped-agents)
  - [Memory=1: delayed collapse via coordination without trend detection](#memory1-delayed-collapse-via-coordination-without-trend-detection)
  - [Memory=3: fragile survival at the threshold](#memory3-fragile-survival-at-the-threshold)
  - [Claude Haiku: memory × communication interaction](#claude-haiku-memory--communication-interaction)
  - [Memory=2: oscillating dynamics and the stochastic boundary](#memory2-oscillating-dynamics-and-the-stochastic-boundary)
- [Problem specification: correctly-specifying vs. misspecifying the commons game](#problem-specification-correctly-specifying-vs-misspecifying-the-commons-game)
  - [Correctly specifying: Sonnet targets the sustainable yield](#correctly-specifying-sonnet-targets-the-sustainable-yield)
  - [Misspecifying: gpt-5.5 solves for zero-growth equilibrium](#misspecifying-gpt-55-solves-for-zero-growth-equilibrium)
  - [Why the distinction matters for commons theory](#why-the-distinction-matters-for-commons-theory)
- [Working hypotheses and proposed experiments](#working-hypotheses-and-proposed-experiments)
  - [H1: Cooperation threshold](#h1----coop--049-is-a-tragedy-producing-threshold-at-standard-starting-conditions-consistent-across-models)
  - [H2: High coop necessary but not sufficient](#h2----high-cooperation-is-necessary-but-not-sufficient-fairoth-and-negr-determine-whether-stasis-paralysis-or-institution-emerges)
  - [H3: Negative reciprocity as paralysis antidote](#h3----negative-reciprocity-is-a-cooperative-paralysis-antidote)
  - [H4: Stressed starting conditions amplify differentiation](#h4----stressed-starting-conditions-amplify-cooperative-differentiation)
  - [H5: Explicit thresholds cure paralysis](#h5----cooperative-paralysis-is-a-prompt-engineering-artifact-curable-by-explicit-thresholds)
  - [H6: Model capability predicts failure mode](#h6----model-capability-predicts-cooperative-failure-mode-smaller-models-default-to-keep-larger-to-add)
  - [H7: Memory window is a prerequisite for trend detection and commons stability](#h7----there-is-a-minimum-memory-window-for-commons-stability-below-it-correct-norms-become-unreachable-holding-patterns)
  - [Open questions](#open-questions)
- [Glossary](#glossary)
  - [Acronyms and abbreviations](#acronyms-and-abbreviations)
  - [Model parameters and variables](#model-parameters-and-variables)
  - [Collapse patterns](#collapse-patterns)
  - [Ostrom framework](#ostrom-framework)
- [Citations](#citations)
- [Status](#status)

---

## Background

The [Tragedy of the Commons](https://en.wikipedia.org/wiki/Tragedy_of_the_commons) (Hardin, 1968) predicts that rational self-interest leads to collective over-exploitation of shared resources. Ostrom (1990) challenged this, showing that real communities often self-organize governance institutions -- rules, monitoring, graduated sanctions -- without top-down intervention.

> *"Instead of there being a single solution to a single problem, I argue that many solutions exist to cope with many different problems. Instead of presuming that optimal institutional solutions can be designed easily and imposed at low cost by external authorities, I argue that 'getting the institutions right' is a difficult, time-consuming, conflict-invoking process."*
> - Ostrom (1990, Chapter 1)

MASTOC (Schindler, 2013) is a NetLogo ABM that reproduces the tragedy under classical rational-agent assumptions. 

MASTOC-LLM asks: what happens when agents can reason, remember, and talk?

### Ostrom's Design Principles -- applicability to this model

Ostrom (1990, Chapter 3) identified eight design principles shared by long-lived, self-governing commons institutions. The table below maps each principle to its status in MASTOC-LLM. The key experimental levers -- `memory_length` and `communication?` -- directly control whether the emergent principles are possible at all.

| # | Principle | Status | Observable signal |
|---|-----------|--------|-------------------|
| DP1 | **Clear boundaries** -- who may use the resource is well-defined | ✅ Baked in by design | Fixed 3-agent structure; no entry/exit dynamics |
| DP2 | **Rules fit local conditions** -- appropriation rules match the specific resource context | 🟡 Partially emergent | Agents adapt personal thresholds to current pool %; not negotiated collectively |
| DP3 | **Collective choice** -- those affected by the rules participate in modifying them | 🔬 Experimentally variable | Norm proposals and threshold agreements in agent messages -- *only possible when `communication?` is on* |
| DP4 | **Monitoring** -- resource state and user behavior are observable | ✅ Baked in by design | Pool % is globally visible every tick; a structural advantage real commons rarely have |
| DP5 | **Graduated sanctions** -- rule-breakers face escalating consequences applied by peers | 🔬 Experimentally variable | Social pressure via messages ("you should reduce"); true enforcement absent -- itself a finding. *Only possible when `communication?` is on* |
| DP6 | **Conflict resolution** -- low-cost mechanisms for dispute resolution exist | ❌ Not present | No arbitration mechanism; disagreements play out through action choices alone |
| DP7 | **External recognition** -- outside authorities recognize the community's right to self-govern | ➖ Not applicable | Single-environment lab model; no external authority modeled |
| DP8 | **Nested governance** -- institutions are organized in nested layers for larger systems | ➖ Not applicable | 3-agent model; no hierarchy to nest |

> *"Institutions are rarely either private or public -- 'the market' or 'the state.' Many successful CPR institutions are rich mixtures of 'private-like' and 'public-like' institutions defying classification in a sterile dichotomy."*
> - Ostrom (1990, Chapter 1)

This project chooses as its empirical target DP3 and DP5: testing whether language-capable agents spontaneously reconstruct collective choice and graduated sanctions under resource pressure, and identifying the conditions (`memory_length`, `communication?`) that make this possible.

---

## How it works

```
NetLogo (MASTOC-LLM.nlogo)
        │  per-tick context (pool state, herd sizes, payoffs, messages)
        ▼
Python bridge (mastoc_llm_bridge.py)
        │  LLM prompt + rolling memory + inbox messages
        │  (per-agent backend and model -- agents can differ)
        ▼
LLM API  ←  Anthropic | OpenAI | Google | Ollama (local)
        │  JSON response: { action, message, reasoning }
        ▼
NetLogo  ←  action (−1 / 0 / +1)  +  outgoing message → neighbors
```

Each tick, every LLM agent:
1. Receives the current pool health, own herd size, neighbor herd sizes and last actions, and estimated payoffs for each possible action
2. Reads its rolling memory of past rounds (configurable via `memory_length`, default 5; 0 = no memory)
3. Reads any messages sent by neighbors this round (suppressed when `communication?` is off)
4. Calls the LLM, which returns a structured JSON decision with reasoning and an optional 60-word message to send to neighbors
5. Acts on the decision; the message is delivered to all neighbors before their next decision (no-op when `communication?` is off)

A secondary LLM pass runs every 5 ticks to classify agent messages for Ostrom institutional signals (norm proposals, sanctions, coordination, trust-building, defection). The classifier always uses **agent 0's backend and model**; in a mixed-backend run it silently inherits agent 0's provider.

### How personality parameters reach the LLM

Rather than feed into a utility formula that the simulation computes, the personality slider values are translated by the Python bridge (`mastoc_llm_bridge.py`) into a plain-English personality trait that is included in the agent's system prompt. The LLM reads this description and makes decisions accordingly.

The translation works as a set of threshold checks. For each parameter, a trait phrase is added to the agent's personality description when the value crosses 0.5 (or 0.3 for self-interest).

The phrases injected into the prompt as a single sentence:

| Parameter value | Phrase added to prompt |
|----------------|------------------------|
| `cooperation_level` > 0.6 | *"cooperative -- values collective outcomes over personal gain"* |
| `cooperation_level` < 0.3 | *"self-interested -- focused primarily on personal profit"* |
| `fairness_concerning_me` > 0.5 | *"envious -- bothered when others earn more than you"* |
| `fairness_concerning_others` > 0.5 | *"guilt-averse -- uncomfortable earning much more than others"* |
| `positive_reciprocity` > 0.5 | *"reciprocal -- you reward neighbors who reduce their herds"* |
| `negative_reciprocity` > 0.5 | *"retaliatory -- you punish neighbors who expand their herds"* |
| `risk_aversion_level` > 0.5 | *"risk-averse -- you prefer safer outcomes over risky high payoffs"* |

The two reciprocity parameters deserve explicit distinction, because their similarity in name masks an important asymmetry in function. Both encode a conditional response to what neighbors did last tick -- but they are conditioned on opposite ends of the action space. `positive_reciprocity` (pos_r) amplifies the payoff for *restraint* when neighbors also restrained: it rewards cooperative moves with a cooperative neighborhood. `negative_reciprocity` (neg_r) amplifies the payoff for *expansion* when neighbors also expanded: it rewards defection in kind. Neither is simply "prosocial" or "antisocial" -- pos_r is a mechanism for stabilizing cooperation, neg_r is a mechanism for escalating competition. When pos_r exceeds neg_r, restraint compounds faster than defection; when neg_r meets or exceeds pos_r, the escalation dynamic dominates. This asymmetry drives the empirical regularity reported in the [baseline parameter sweep](#core-stability-rule-pos_r--neg_r) below.

A run at default settings (coop=1, fairness=0.5, neg_r=0, pos_r=0) would produce: *"cooperative -- values collective outcomes over personal gain; guilt-averse -- uncomfortable earning much more than others."*

Alongside the personality description, each agent also receives three numerical payoff estimates -- the expected net gain from adding a cow, keeping the herd steady, or removing a cow -- computed by NetLogo from current grass levels and herd sizes. These give the LLM a quantitative signal about the current state of the commons without requiring it to derive the numbers itself.

### The cost function and grassland dynamics

The following equations describe what NetLogo actually computes each tick -- the payoff estimates passed to the LLM and the grass regrowth that drives resource dynamics. This is the simulation's numerical core; the personality system above sits on top of it.

**Cost function** -- the opportunity cost of changing herd size:

$$C(K, K') = \frac{G(V - K \cdot f) - G(V - K' \cdot f)}{f \cdot n} \cdot P$$

where G(v) is the *next-tick* grass level at vegetation level v:

$$G(v) = \max(0,\; v) \cdot \left[1 + r \cdot v \cdot \left(1 - \frac{v}{V_{\max}}\right)\right]$$

V_max = 1089 (the 33 × 33 patch grid). The cost function captures the marginal impact of adding or removing cows on the resource's next-period recovery -- the mechanism through which herd decisions propagate to the commons.

**Grass regrowth** -- logistic dynamics:

$$V(t+1) = V(t) + r \cdot V(t) \cdot \left(1 - \frac{V(t)}{V_{\max}}\right) - \sum_i k_i \cdot f$$

Each tick, cows graze first (each consuming f patches), then surviving grass regrows logistically. Cows that cannot find f patches die.

These equations are the model's numerical skeleton. The payoff equations tell you what an individually-rational agent *should* do given the current state; they cannot represent an agent reasoning about whether to change the rules of the game. That capacity -- proposing norms, negotiating thresholds, sanctioning defectors -- is what the LLM layer adds, and what the experimental conditions are designed to test.

---

## Repository structure

```
MASTOC-LLM/
├── MASTOC-LLM.nlogox         NetLogo 7 model (open this to run)
├── mastoc_llm_bridge.py      Python LLM bridge (auto-imported by NetLogo)
├── run_baseline_sweep.py     Headless batch sweep runner (baseline + LLM conditions)
├── experiment_runner.py      Analysis tool -- merges logs, produces figures
├── config.json               Parameter reference
├── requirements.txt          Python dependencies
├── SETUP.md                  Full setup and usage guide
├── logs/                     Rich CSV outputs (created at runtime)
│   └── {run_id}/
│       ├── run_meta.json
│       ├── resources.csv     Pool, cows, pressure per tick
│       ├── decisions.csv     Agent decisions, messages, reasoning per tick
│       └── institutions.csv  Ostrom institution detection scores
├── baseline_sweep_table.csv  BehaviorSpace output from run_baseline_sweep.py
└── Data/                     Baseline flat-file outputs (MASTOC format)
```

---

## Quick start

### Requirements

- NetLogo 7.0.4
- Python 3.10+
- An API key for at least one supported backend (see below)

```bash
pip install anthropic openai pandas matplotlib seaborn
pip install google-generativeai   # only if using Google Gemini
```

```bash
# Set whichever keys you need
set ANTHROPIC_API_KEY=sk-ant-...   # Anthropic
set OPENAI_API_KEY=sk-...          # OpenAI
set GOOGLE_API_KEY=...             # Google Gemini
# Ollama needs no key -- just run it locally
```

> **No GPU?** You can run the Ollama backend for free on Kaggle's cloud GPUs (30 hrs/week, T4 × 2, no cost) using ngrok to expose the server. See [SETUP.md → Running LLM agents without a local GPU](SETUP.md#running-llm-agents-without-a-local-gpu-free-via-kaggle) for a step-by-step walkthrough.

### Running a simulation

1. Open `MASTOC-LLM.nlogo` in NetLogo 7
2. Set the **Condition** chooser (`baseline`, `full-gabm`, or `hybrid`)
3. For hybrid: adjust **num-llm-agents** (1 = 1 LLM, 2 = 2 LLMs, 3 = 3 LLMs)
4. Set per-agent **backend** and **model** for each agent (or leave at defaults)
5. Adjust per-agent **initial cows** sliders if desired (defaults: 5 / 15 / 25)
6. Click **Setup**, then **Simulation**
7. Logs write to `logs/` automatically

### Batch sweeps (baseline and LLM conditions)

`run_baseline_sweep.py` runs BehaviorSpace sweeps headlessly across all three conditions. For the baseline, there are no API calls and no cost; for full-gabm and hybrid, the script shows a cost estimate and confirmation prompt before launching.

```bash
# Baseline -- free, fast, no API needed
python run_baseline_sweep.py --runs 30
python run_baseline_sweep.py --runs 20 --neg-r 0.5 --coop 0.5
python run_baseline_sweep.py --runs 20 --neg-r 1.0 --grassland 50,75,100

# Full-GABM with Claude Sonnet (shows cost estimate first)
python run_baseline_sweep.py --condition full-gabm --runs 10 \
    --backend anthropic --llm-model claude-sonnet-4-6

# Hybrid: 1 LLM agent + 2 rule-based, stop at collapse
python run_baseline_sweep.py --condition hybrid --num-llm-agents 1 \
    --backend ollama --llm-model llama3 --stop-on-collapse

# Remote Ollama server (no API key required)
python run_baseline_sweep.py --condition full-gabm --runs 5 \
    --backend ollama --llm-model gemma3:27b \
    --ollama-url http://192.168.86.26:11434/v1 --yes

# Stream live LLM output (equivalent to watching the NetLogo Command Center)
python run_baseline_sweep.py --condition full-gabm --runs 3 \
    --backend ollama --llm-model deepseek-r1:32b \
    --ollama-url http://192.168.86.26:11434/v1 --verbose
```

**All flags:**

| Flag | Default | Description |
|---|---|---|
| `--condition` | `baseline` | `baseline`, `full-gabm`, or `hybrid` |
| `--backend` | `anthropic` | LLM backend: `anthropic`, `openai`, `google`, `ollama` |
| `--llm-model` | `claude-sonnet-4-6` | Model name passed to the bridge |
| `--num-llm-agents` | 1 | Number of LLM agents in hybrid mode (1–3) |
| `--runs N` | 30 | Repetitions per parameter combo |
| `--ticks T` | 120 | Max ticks per run |
| `--stop-on-collapse` | off | End each run when grassland drops below 5% |
| `--yes` / `-y` | off | Skip cost confirmation (for scripting) |
| `--verbose` / `-v` | off | Stream NetLogo print/show output live (Command Center equivalent) and enable per-agent LLM logging (connection, tokens, timing). Without this flag, NetLogo stdout is captured silently and only surfaced on failure. |
| `--grassland G` | 100 | Initial grassland % -- comma-separated for sweep |
| `--coop F` | 1.0 | Cooperation level |
| `--neg-r F` | 0.0 | Negative reciprocity |
| `--pos-r F` | 1.0 | Positive reciprocity |
| `--risk F` | 1.0 | Risk aversion |
| `--fairness-me F` | 0.0 | Fairness concerning self |
| `--fairness-oth F` | 1.0 | Fairness concerning others |
| `--memory-length N` | 5 | Agent memory length (used for LLM cost estimate) |
| `--forage F` | 2.0 | Cow forage requirement |
| `--ollama-url URL` | `http://localhost:11434/v1` | Base URL for Ollama server |
| `--netlogo-path PATH` | auto | NetLogo install directory |

The script injects the experiment into a temporary copy of the model, calls Java directly (bypassing `netlogo-headless.bat`'s quoting bug when NetLogo is installed under `Program Files`), and cleans up the temp file afterward. BehaviorSpace output writes to `baseline_sweep_table.csv`; per-run logs write to `logs/`. Primarily tested on Windows; macOS/Linux users may need to adjust extension paths.

**Cost estimation for LLM conditions.**

When `--condition` is `full-gabm` or `hybrid`, the script estimates total API cost based on run count, tick count, number of LLM agents, memory length, and the model's published per-token pricing, then shows a formatted table and prompts for confirmation. 

<dl>
<dd>Pass `--yes` to skip. </dd>
</dl>

Ollama runs are always free. Unknown model names fall back to a mid-tier estimate with a warning.

### Analysing results

```bash
python experiment_runner.py --mode analyse
```

Reads both `logs/` (LLM runs) and `Data/` (baseline runs) and produces merged CSVs and figures in `figures/`.

See [SETUP.md](SETUP.md) for full documentation.

---

## Experimental conditions

| Condition | Agents | Description |
|---|---|---|
| **baseline** | 3 rule-based | Psychosocially-adjusted best-response (faithful to original MASTOC) -- reproduces classical tragedy |
| **full-gabm** | 3 LLM | All agents use language reasoning and communication |
| **hybrid** | mix of LLM + rule-based | Controlled by `num-llm-agents` slider -- 1, 2, or 3 LLM agents paired with rule-based agents |

The `num-llm-agents` slider sets the number of LLM-reasoning agents directly (1, 2, or 3) when in hybrid mode. Setting it to `1` gives 1 LLM + 2 rule-based; `2` gives 2 LLMs + 1 rule-based.

Each agent's backend and model are independently configurable. Any mix of Anthropic, OpenAI, Google Gemini, and local Ollama models can be run simultaneously in the same simulation, enabling direct cross-model comparisons within a single run.

---

## Collapse pattern taxonomy

Four distinct trajectories to commons collapse recur across the run set: agents talking themselves into collective inaction while the pool drains; cascading defection driven by low cooperation framing; agents overshooting a recovering pool and reversing a beat too late; a structural mismatch in which LLM agents produce correct outputs that rule-following partners cannot receive. Each pattern has a different proximal cause, a different signature in agent language, and different implications for experimental design.

| Pattern | Mechanism | Signature | Key run(s) |
|---------|-----------|-----------|------------|
| **I -- Cooperative Paralysis** | Agents coordinate on inaction via mutual reassurance; threshold for action calibrated too conservatively | All agents KEEP for many ticks while pool drains; near-identical conditional promises repeated round after round; REMOVE only at single-digit pool health | gpt-5.4-mini (coop=1, fair_oth=0.5), collapse tick 26; memory=1 variant (pool drained over 50 ticks while agents held the 90% norm) |
| **II -- Defection Cascade** | Low cooperative framing suppresses resistance to defection; each ADD justifies the next | All agents ADD every tick from tick 1; pool exhausted within 10–14 ticks; conditional cooperation language circulates but never executes | gpt-5.5 (coop=0.13), collapse tick 13 |
| **III -- Overshoot-Panic** | Mid-level cooperation produces agents whose outputs are too ADD-inclined to defect outright but too hesitant to act preventively | ADD phase from stressed start; belated pivot to KEEP/REMOVE triggered by visible crisis; agreed threshold stated and violated simultaneously | gpt-5.5 and Claude Sonnet (coop=0.49), 6 independent replications, collapses ticks 16–40; memory=0 (collapse tick 31) |
| **IV -- Hybrid Architecture Failure** | LLM agents cooperate fully; rule-based agents add unchecked and are unreachable by social signals | LLM herd stable or shrinking; rule-based herds grow +1/tick; institution score moderate but not stabilizing; LLM appeals escalate and continue after collapse | All hybrid conditions (1 LLM: tick 35; 2 LLM: tick 58; LLM-advantaged: tick 33) |

### Pattern I -- Cooperative Paralysis

*Mechanism.*

Agents lock into mutual reassurance: each produces cooperative-intent outputs and conditions willingness to reduce on a threshold ("if the commons keeps tightening") that is calibrated too conservatively. The pool drains steadily while all agents KEEP, and the conditional is never triggered until the resource is past saving. By the time any agent switches to REMOVE, the tipping point has already passed.

*Signature.*

All agents KEEP for many consecutive ticks while pool health declines monotonically. Herd sizes are unchanged across those ticks. Messages reproduce near-identical conditional promises round after round. REMOVE actions appear only when pool health has fallen to single digits.

*Key run.*

gpt-5.4-mini (coop = 1, fair_me = 1, fair_oth = 0.5), collapse at tick 26.

*Diagnostic quotes.*

> **Ticks 8–24 – Agent 2 (action: KEEP, every round; pool declining from 84.4% to 8.5%):** *"I'll keep steady with you both this round. If the pasture keeps tightening, I'm ready to reduce fairly."*

The conditional promise is renewed for seventeen consecutive ticks across a 76-percentage-point pool decline, and honoured one tick after the point of no return.

*Why it matters.*

This pattern cannot emerge from rule-based agents, which do not produce conditional social commitments. It is an LLM-specific failure mode arising from the same language faculty that enables institution building: cooperative coordination language deployed in service of collective inaction.

---

### Pattern II -- Defection Cascade

*Mechanism.*

When cooperation framing is set low, individual resistance to defection is suppressed: each agent's ADD output cites the others' adding as justification, producing a self-reinforcing cascade in which every ADD justifies every other and the commons is exhausted in 10–14 ticks. Conditional promises to cooperate-if-others-cooperate appear every round and are broken every subsequent round.

*Signature.*

All agents ADD every tick from tick 1. Pool declines monotonically from the start. Pool is exhausted within 10–14 ticks. Conditional cooperation language appears in messages throughout but never translates into KEEP or REMOVE actions.

*Key run.*

gpt-5.5 (coop = 0.13), collapse at tick 13 from a 49.4% starting pool.

*Diagnostic quotes.*

> **Tick 6 – Agent 1 (action: ADD, pool at 49.9%):** *"I am adding this round since both neighbors added and unilateral restraint would cost me. I clearly commit to KEEP next round if both of you also KEEP."*

> **Tick 7 – Agent 1 (action: ADD, pool at 47.4%):** *"I am adding this round because both of you are adding and ADD pays best. I clearly commit to KEEP next round if both of you also KEEP."*

The sentence is nearly identical across eleven consecutive ticks. The commitment to KEEP-next-round is recycled every round without ever being executed. After the collapse:

> **Tick 14 – Agent 0:** *"The commons has already collapsed, so I am taking the best immediate payoff now. If grass recovers and both agree to start restraint, I can reconsider."*

Rational defection to the end: the output explicitly acknowledges the defection.

---

### Pattern III -- Overshoot-Panic

*Mechanism.*

Mid-level cooperative framing produces agents whose outputs acknowledge resource pressure but cannot break out of an ADD equilibrium while others are adding: they add past the tipping point together, then pivot to REMOVE one or two ticks too late. The commons is overstocked. A collective pivot to KEEP/REMOVE eventually occurs, but it is triggered by visible crisis rather than predictive restraint, and the resource has already crossed its tipping point by the time action is taken.

*Signature.*

Initial ADD phase across all agents (ticks 1–8+), even from stressed starting conditions. Mid-run pivot to KEEP (ticks 9–11). Panicked REMOVE phase. Collapse within a few ticks of REMOVE onset. Pool health at first REMOVE is typically 30–40%. The agreed threshold for switching is verbally stated in messages, and violated every round until well past it.

*Key runs.*

gpt-5.5 (coop = 0.49) across 4 replications (collapses at ticks 16, 28, 29, 40); Claude Sonnet 4.6 (coop = 0.49), collapse at tick 37. All five runs collapsed.

*Diagnostic quotes (from the 16-tick run).*

> **Tick 5 – Agent 0 (action: ADD, pool at 53.7%):** *"I will add one cow this round to keep pace. Since we all agree on caution, let's stop adding if grass falls near 50%."*

> **Tick 9 – Agent 2 (action: ADD, pool at 48.9% -- below the agreed threshold):** *"I am adding once more since we are still above 50% and both of you are adding. But we are very close to 50%."*

> **Tick 15 – Agent 2 (action: REMOVE, pool at 0.1%):** *"I will remove one cow again. The pasture is near collapse, and we need coordinated reductions now rather than cautious commitments."*

The threshold-based logic is stated correctly and violated immediately.

*Cross-model consistency.*

Overshoot-panic was replicated across two model families in five independent runs. This is consistent with the pattern being governed by the parameter configuration (coop ≈ 0.49) rather than model-specific idiosyncrasies. Mid-level cooperation consistently produces agents whose outputs are too conflicted to defect outright but too hesitant to act preventively, held between individual self-interest and collective restraint until the crisis forces the issue.

---

### Pattern IV -- Hybrid Architecture Failure

*Mechanism.*

One or more LLM agents produce fully cooperative outputs and appeal to unresponsive rule-based partners. But the partners cannot receive or act on language, so the commons collapses regardless of how well the LLM agents behave. The rule-based agents add one cow per tick regardless of pool state or messages, and the LLM agents -- holding small herds and issuing increasingly urgent appeals -- cannot shrink herds fast enough to compensate for their neighbors' unchecked growth.

*Signature.*

LLM herd grows slowly or shrinks; rule-based herds grow by 1 cow per tick per agent; institution score remains moderate without stabilizing; LLM appeals escalate in urgency, continuing after collapse.

*Key runs.*

All hybrid conditions (1 LLM, 2 LLM, LLM-advantaged). Fully documented in the individual run narratives below.

*Why it matters.*

> *"The key to my argument is that some individuals have broken out of the trap inherent in the commons dilemma, whereas others continue remorsefully trapped into destroying their own resource."*
> - Ostrom (1990, Chapter 1)

This pattern is not about LLM failure. The LLM agents produce outputs consistent with commons theory's prescriptions. The failure is structural: Ostromian institution-building requires the cognitive capacity to participate in it. The LLM agents' problem is not insufficient language faculty. It is insufficient partners.

*Dataset limitation.*

All hybrid runs to date were conducted under parameters that the baseline sweep identifies as collapse-producing -- specifically, configurations where `pos_r ≤ neg_r` or where rule-based agents add unchecked regardless of pool state. This means the hybrid dataset is sampled entirely from one end of the parameter space: conditions where even three rule-based agents would collapse. The open question is whether LLM agents improve outcomes in hybrid settings where rule-based agents would *survive* -- whether language-capable agents can shift an already-marginal commons toward stability, or whether the structural benefit is limited to delay. That experiment has not been run.

---

# Preliminary results

> ⚠️ These are single-run results from an ongoing experiment. Replications and full statistical analysis are in progress.

The results below rest on two kinds of evidence. 


<dl>
<dd>The resource-dynamics tables, institution scores, and action counts are <strong>quantitative</strong> -- they record what the simulation measured. </dd>

<dd>The agent messages and reasoning traces, quoted verbatim throughout, are <strong>qualitative</strong>, and they are treated here as primary data rather than illustration. </dd>

</dl>

The quotes are reproduced at length so the interpretation can be checked against its source.

Four distinct collapse trajectories appear across these runs -- **Pattern I (Cooperative Paralysis)**, **Pattern II (Defection Cascade)**, **Pattern III (Overshoot-Panic)**, and **Pattern IV (Hybrid Architecture Failure)** -- described in full in the [Collapse pattern taxonomy](#collapse-pattern-taxonomy) section above.

<dl>

<dd>The opening results look cooperative because the first conditions tested were near-ideal. High-cooperation defaults (coop=1, memory_length=5, communication=on) reliably produce cooperative outcomes in RLHF-aligned models (Claude Sonnet, gpt-5.5, gpt-4o-mini); <strong>KEEP-dominant models (gpt-5.4-mini, DeepSeek R1, gemma4:e4b) produce stasis or paralysis under the same settings.</strong> Subsequent parameter sweeps tell a more mixed story.</dd>

<dd>Mid-level cooperation (coop≈0.5) collapsed in eleven independent full-GABM runs across five model families -- Sonnet, Haiku, gpt-5.5, DeepSeek R1:32b, and gemma4:e4b. Short memory windows contributed to collapse in Sonnet at mid-cooperation (memory=1, coop=0.5: collapse at tick 87; memory=0, coop=0.5: collapse at tick 31), but memory window alone does not determine outcome: six independent gpt-5.5 runs at coop=0.49, memory=0 survived (five to 120 ticks, one to tick 62). The interaction between model family and memory length remains unresolved.</dd>

<dd>High-cooperation Sonnet runs with short memory windows (memory=0 and memory=1) did <em>not</em> collapse over their 10-50 tick horizons; gpt-4o-mini at coop=1, memory=0 survived three replications at 120 ticks. These horizons are not long enough to treat as settled evidence, but the pattern is consistent across two RLHF-aligned families.</dd>

</dl>

Collapse is concentrated around mid-cooperation parameters. The initial baseline runs serve as optimized controls rather than representative system outcomes

### Summary across conditions

| Condition | Model | LLMs | Collapse? | Collapse tick | Key finding |
|-----------|-------|------|-----------|---------------|-------------|
| **Baseline** | -- | 0 | Yes | ~36 | Classical tragedy reproduced |
| **Full-GABM** | Claude Sonnet 4.6| 3 | No | -- | **coop=1, fair_me=0, fair_oth=1, memory=5, comm=on (defaults):** cooperative convergence to 13/13/13; institution score 10/10 by tick 91 |
| **Full-GABM (low cooperation)** | Claude Sonnet 4.6| 3 | No | -- | **coop=min, fair_me=0, fair_oth=1, memory=5, comm=on:** self-interested framing yields *faster* convergence (tick 16) to higher-yield 20/20/20; cooperation robust to personality override |
| **Full-GABM (low guilt + low envy)** | Claude Sonnet 4.6| 3 | No | -- | **coop=1, fair_me=0, fair_oth=0, memory=5, comm=on:** fairness parameters zeroed; repeated defection, slow convergence (tick 118), higher herd load (84 cows), commons stressed to 86.7% |
| **Hybrid (1 LLM)** | Claude Sonnet 4.6| 1 | Yes | 35 / 31 | **coop=1, memory=5 (defaults):** two runs -- collapse tick 35 (Agent 0 as LLM, starting herd 5) and collapse tick 31 (Agent 1 as LLM, starting herd 30, total starting herd 62); one LLM cannot shift the equilibrium alone regardless of which node it occupies |
| **Hybrid (2 LLM)** | Claude Sonnet 4.6| 2 | Yes | 58 | **coop=1, fair_me=0, fair_oth=1, memory=5, comm=on (defaults):** coalition formed, tragedy delayed 23 ticks, but overwhelmed by one defector |
| **Full-GABM (Llama 3.2 3B)** | Llama 3.2 3B | 3 | No | -- | **coop=1, fair_me=0, fair_oth=1, memory=5, comm=on:** pool maintained at 99.4% but herds oscillated without convergence; cooperative messaging but no institution formation |
| **Full-GABM (Llama 3.2 3B, scarce commons)** | Llama 3.2 3B | 3 | No | -- | **coop=1, fair_me=0, fair_oth=1, memory=5, initial_grassland=48%, comm=on:** pool recovered 48%→99% by tick 17; herds oscillated without convergence throughout all 51 ticks |
| **Hybrid (LLM-advantaged initial herd)** | Claude Sonnet 4.6 | 1 | Yes | 33 | **coop=1, fair_me=0, fair_oth=1, memory=5, comm=on; Agent 1 (LLM) starts with 39 cows:** voluntarily reduces to ~25 by collapse; rule-based agents add unchecked; collapse 2 ticks earlier than baseline hybrid |
| **Full-GABM (scarce commons, default fairness)** | Claude Sonnet 4.6 | 3 | No | -- | **coop=1, fair_me=0, fair_oth=1, memory=5, initial_grassland=49%, comm=on:** pool recovered 49%→99% by tick 10; converged to [11,12,13] by tick 30 |
| **Full-GABM (scarce commons, low coop + low fairness)** | Claude Sonnet 4.6 | 3 | No | -- | Initial grassland 50%, coop=0.3, fairness=0: recovery to 99% by tick 20; converged to [12,14,16] by tick 30 |
| **Full-GABM (cooperative stasis)** | gpt-5.4-mini | 3 | No | -- | coop=1, fair_me=0, fair_oth=1, memory=5, forage=2: all KEEP for 36 ticks; herds frozen at starting values (6/15/25); pool stable at 99%+; no equalization |
| **Full-GABM (universal stasis)** | gpt-5.4-mini | 3 | No | -- | coop=1, fair_me=0.5, fair_oth=0.5, memory=5, initial=50%: all 90 decisions are KEEP -- zero ADD or REMOVE; herds 5/15/25 unchanged through tick 30; pool 99.1%. More rigid than cooperative stasis |
| **Full-GABM (cooperative paralysis)** | gpt-5.4-mini | 3 | Yes | 26 | coop=1, fair_me=1, fair_oth=0.5, memory=5, forage=4: KEEP-lock for 24 ticks while pool drained 95.8%→8.5%; REMOVE attempted at tick 25 -- one tick too late; fast drain driven by forage=4 |
| **Full-GABM (asymmetric growth)** | gpt-5.4-mini | 3 | No (declining) | -- | coop=1, fair_me=1, fair_oth=0.5, memory=5, forage=2: Agent 0 (5 cows) KEEP-locked all 39 ticks; Agents 1+2 add 14 and 12 times → herds grow 15→27 and 25→33; pool declining (95.8% at tick 39); no collapse but trajectory unsustainable |
| **Full-GABM (scarce commons, high coop)** | gpt-5.5 | 3 | No | -- | coop=1, fair_me=1, fair_oth=0.11, initial pool 48%: immediate cooperative restraint; 23/23/23 by tick 46; pool recovered to 95.9% |
| **Full-GABM (low cooperation)** | gpt-5.5 | 3 | Yes | 13 | coop=0.13: defection cascade -- all ADD every tick from tick 1; pool exhausted in 13 ticks from 49.4% |
| **Full-GABM (mid cooperation, x4 replications)** | gpt-5.5 | 3 | Yes (4/4) | 16–40 | coop=0.49: overshoot-panic -- ADD phase from stressed start, collective REMOVE too late; consistent tragedy across all 4 runs |
| **Full-GABM (mid cooperation)** | Claude Sonnet 4.6 | 3 | Yes | 37 | coop=0.49: overshoot-panic matching gpt-5.5 -- mid-level cooperation produces tragedy across all tested model families (Claude Sonnet, gpt-5.5, gemma4) |
| **Full-GABM (high coop + high negative reciprocity)** | Claude Sonnet 4.6 | 3 | No | -- | coop=1, neg_r=1: equalized to 16/16/16 by tick 21 -- fastest convergence observed; explicit accountability enforcement in agent messages |
| **Full-GABM (high coop + high negative reciprocity)** | gpt-5.5 | 3 | No | -- | coop=1, neg_r=1: stable at 12/21/22 by tick 17; tit-for-tat escalation cycles before de-escalation; pool stable at 98.2% -- same parameters, different institutional character than Claude |
| **Full-GABM (memory=0, no communication)** | Claude Sonnet 4.6 | 3 | Yes | 31 | coop≈0.5, memory_length=0, communication=off: amnesiac agents with no messaging -- textbook overshoot-panic in 31 ticks; ADD=71, KEEP=19, REMOVE=6 |
| **Full-GABM (memory=15, communication on)** | Claude Sonnet 4.6 | 3 | No | -- | coop≈0.5, memory_length=15: pool stabilized near 95% for 70+ ticks (final 94.1%); converged to 24/24/24; agents enforced explicit 93–96% threshold norm via messages |
| **Full-GABM (memory=1, communication on)** | Claude Sonnet 4.6 | 3 | Yes | 87 | coop≈0.5, memory_length=1: delayed collapse -- pool recovered to 95% then drained while agents held a 90% target they couldn't detect was unreachable; Pattern I variant |
| **Full-GABM (memory=2, communication on)** | Claude Sonnet 4.6 | 3 | No (oscillating) | -- | coop≈0.5, memory_length=2: oscillating grow/correct cycles; achieved 25/25/25 equalization at tick 75; new growth phase began at tick 111; pool declining at termination (90.2%); highly variable across replications |
| **Full-GABM (memory=3, communication on)** | Claude Sonnet 4.6 | 3 | No | -- | coop≈0.5, memory_length=3: survived 120 ticks; pool slowly declining (90.1% at end); herds stable at 81 total -- fragile, trending toward collapse |
| **Full-GABM (memory=5, comm on)** | Claude Haiku 4.5 | 3 | Yes | 99 | coop≈0.5, memory_length=5, comm=on, initial=52%: initial recovery to 99%, then overshoot-panic; herds reached 67 total by tick 45, pool crashed; ADD=57, KEEP=231, REMOVE=9 |
| **Full-GABM (memory=15, comm on)** | Claude Haiku 4.5 | 3 | No | -- | coop≈0.5, memory_length=15, comm=on, initial=52%: survived 120 ticks; converged to 24/24/24; pool stable at 95% -- same outcome as Claude Sonnet memory=15 |
| **Full-GABM (memory=15, comm off)** | Claude Haiku 4.5 | 3 | Yes | 46 | coop≈0.5, memory_length=15, comm=off, initial=52%: rapid collapse -- herds grew unchecked to 88 total by tick 45, pool 14.7%→0%; ADD=55, KEEP=72, REMOVE=17; memory alone insufficient without communication |
| **Full-GABM (DeepSeek stasis, neg_r=0)** | DeepSeek R1:32b | 3 | No (stalling) | -- | coop=1, neg_r=0, memory=5, comm=on: near-universal KEEP in 7 ticks before run interrupted; herds 5/15/26→6/15/26; pool 99%; cooperative messaging but no equalization |
| **Full-GABM (DeepSeek slow drift, neg_r=1)** | DeepSeek R1:32b | 3 | No (stalling) | -- | coop=1, neg_r=1, memory=5: 55 ticks; KEEP-dominant (ADD=13, KEEP=151, REMOVE=1); herds crept 5/15/25→6/20/31; pool 97.9%; no equalization, no institution formation -- matches gpt-5.4-mini stasis pattern |
| **Full-GABM (gemma4 KEEP-dominant)** | gemma4:e4b | 3 | No (stalling) | -- | coop=1, grass=90%, comm=off: zero ADD or REMOVE across all 11 ticks; herds frozen at initial values [14,40,5]; pool 97.6%; most extreme stasis observed -- not even the large initial inequality triggers equalization |
| **Full-GABM (gemma4 overshoot-panic)** | gemma4:e4b | 3 | Yes | 46 | coop=0.5, grass=50%, comm=off: classic overshoot-panic -- pool climbed 52%→95% through tick 20 then reversed as herds grew unchecked to [27,43,39]; collapse tick 46; Agent actions ADD=115, KEEP=133, REMOVE=43; matches coop=0.49 threshold seen in Sonnet and gpt-5.5 |
| **Full-GABM (qwen2.5:14b, self-interested)** | qwen2.5:14b | 3 | No | -- | coop=0, neg_r=0.5, pos_r=1, mem=5, comm=on: 8 of 11 runs completed 120t; all survived; mean pool 98.0%, mean total cows 53.9; KEEP-dominant (ADD=30.8, KEEP=299.0, REMOVE=22.0 per run); herds unequal throughout; institution score 8–9 |
| **Full-GABM (qwen2.5:14b, mid cooperation)** | qwen2.5:14b | 3 | No | -- | coop=0.5, neg_r=0, pos_r=1, mem=5, comm=on: 14 of 15 runs completed 120t; all survived; mean pool 99.6%, mean total cows 35.0; more KEEP-dominant than coop=0 condition (ADD=16.9, KEEP=314.8, REMOVE=28.3 per run); herds persistently unequal; institution score 7–10 |
| **Baseline (growth rate threshold sweep)** | -- | 0 | Threshold | ~93 | grass=41%, forage=2: growth ≤ 0.0055 → always collapse (tick 84–97); growth ≥ 0.006 → always stable (pool 100%, herds 80–120 each). 15 replications at growth=0.0051 all collapse at exactly tick 94 -- baseline is fully deterministic at risk_aversion=0 |
| **Baseline (risk aversion delay)** | -- | 0 | Yes | 24–39 | grass=51%, growth=0.001: risk=0 → collapse tick 24; risk=0.45 → tick 28; risk=1 → tick 39; risk aversion delays but cannot prevent collapse when growth is insufficient |

---

### Baseline: the Ostrom spectrum under psychosocial parameters

The baseline agents posess neither language or memory. On each tick, agents evaluate all three possible actions (``ADD`` / ``KEEP`` / ``REMOVE``) by computing psychosocially-adjusted payoffs across all possible neighbor-action combinations and selecting the action with the highest expected value. That payoff matrix is then shiftred by four parameters: cooperation level, fairness weights, reciprocity, and conformity. To model risk management, as the ``risk_aversion_level`` increases, a probabilitic downgrade is introduced, occasionally converting an intended ``ADD`` action into a ``KEEP``.

#### Relationship to the original MASTOC model.

The underlying payoff calculation -- cost function, cooperation/fairness/reciprocity/conformity adjustments -- is ported directly from Schindler (2013). The decision procedure, however, is a reconstruction. 

Where the original MASTOC model relied on a Netlogo extension to identify Nash equilibria, MASTOC-LLM substitutes an **expected-value (EV) best-response** mechanism: agents select the action yielding the highest mean adjusted payoff across all possible neighbor actions. While vestigial turtle variables (``Nash-list``, ``list-of-Nash-lists``, and ``selected-Nash-equilibrium``) and retained to preserve parity with the 2013 source code, this shift away from Nash equilibrium aligns with Schindlers subsequent work (2012b) which abandoned Nash due to its prohibitive computational cost and lack of realism.

Remarkably, the models core behavioral trends remain robust across three fundamentally different decision architectures, suggesting that Schindlers underlying psychosocial payoff structure, rather than the specific decisionmaking algorithm, drives outcomes:

- **Nash equilibria (Schindler, 2012a):** Sweeps of cooperativeness and negative reciprocity show clear directional effects on commons survival: positive reciprocity supports sustainability, while negative reciprocity undermines it.

- **Reactive agents (Schindler, 2012b):** Replacing Nash entirely with probabilistic agents, Pearson correlations across 400 random-disposition runs confirm the same pattern -- cooperativeness r ≈ +0.41, negative reciprocity r ≈ −0.17 to −0.22, both p < 0.001 (Table 3).

- **EV best-response (MASTOC-LLM):** Our baseline architecture reproduces this same boundary: `pos_r > neg_r` reliably predicts survival across 2,140 baseline runs.

Because the baseline agents react exclusively to the immediate payoff matrix, no information carries over between ticks. MASTOC-LLM asks whether agents equipped with language, memory, and the capacity to communicate can outperform what the payoffs alone would predict.

**v1.2.0 mathematical fix -- `min` → `mean` in the best-response rule.**

The decision rule compares expected payoffs across the three actions using a list of payoffs from all possible neighbor-state combinations. Prior to v1.2.0, the rule selected the action whose *minimum* payoff in that list was highest (maximin / worst-case reasoning). 

<dl>
<dd>This caused agents to always choose REMOVE regardless of resource state -- not because they were greedy, but because the worst case for REMOVE was always better than the worst case for ADD under standard parameters.</dd>

</dl>

The fix replaces `min` with `mean` so agents select the action with the highest *expected* payoff (best-response under expected value), which is the standard assumption in the original MASTOC model. The three affected lines are in the `rule-based-decide` procedure:

```netlogo
;; v1.1.0 (maximin -- incorrect):
let pa (ifelse-value (length add-a-cow-adj-list    > 0) [ min add-a-cow-adj-list    ] [ 0 ])
let pk (ifelse-value (length let-equal-adj-list    > 0) [ min let-equal-adj-list    ] [ 0 ])
let pr (ifelse-value (length remove-a-cow-adj-list > 0) [ min remove-a-cow-adj-list ] [ 0 ])

;; v1.2.0 (expected-value best response -- correct):
let pa (ifelse-value (length add-a-cow-adj-list    > 0) [ mean add-a-cow-adj-list    ] [ 0 ])
let pk (ifelse-value (length let-equal-adj-list    > 0) [ mean let-equal-adj-list    ] [ 0 ])
let pr (ifelse-value (length remove-a-cow-adj-list > 0) [ mean remove-a-cow-adj-list ] [ 0 ])
```

**Note on existing data:**

The growth rate sweep and risk aversion tables below were collected under the previous pure payoff maximizer implementation. They remain valid as control results and their qualitative conclusions hold, but they do not reflect the psychosocially-adjusted baseline introduced in v1.1.0. New baseline runs at non-zero personality parameters may produce modestly different collapse trajectories.

**Standard conditions (growth = 0.001):**

At default growth rates the commons collapsed in approximately 36 ticks, exactly as classical tragedy-of-the-commons theory predicts. Herds grew from a starting total of 45 cows, crossed 100 by tick ~25, and the grassland was fully depleted by tick 36. This reproduces the original MASTOC result and confirms the control condition is working correctly.

**Growth rate sweep -- finding the stability threshold:**

The central baseline experiment is a systematic sweep of the grass growth rate, searching for the threshold at which the rule-based heuristic can sustain the commons at all. Starting from a scarce commons (grass=41%) with forage=2:

| Growth rate | Result | Collapse tick |
|-------------|--------|---------------|
| 0.0039 | Collapse | 84 |
| 0.0050 | Collapse | 93 |
| 0.0051 | Collapse | 94 |
| 0.0055 | Collapse | 97 |
| **0.006** | **Stable** | -- |
| 0.0061–0.011 | Stable | -- |

The transition is sharp: fifteen independent replications at growth=0.0051 all collapsed at exactly tick 94 (baseline agents are fully deterministic at risk_aversion=0). Increasing to growth=0.006 produced stable outcomes in every run, with the pool recovering to 100% and herds settling in the range [80–120 cows each].

**Baseline stability is not governance.**

> *"Models that use assumptions such as complete information, independent action, perfect symmetry, no human errors, no norms of acceptable behavior, zero monitoring and enforcement costs, and no capacity to change the structure of the situation itself help the analyst derive precise predictions. Models that make such assumptions do not, however, direct the attention of the policy analyst to some of the problematic variables of the situation that affect the incentives and behaviors of individuals."*
> - Ostrom (1990, Chapter 6)

When the growth rate is sufficient, the rule-based heuristic finds an equilibrium, but it is a carrying-capacity equilibrium -- not a cooperative one. Agents add cows continuously until the payoff function flips negative due to resource pressure, then hold or remove.

The stable herd sizes (80–120 per agent) are 5–10× larger than the equilibria reached by LLM agents (13–31 per agent). The commons is sustained, but there is no equalization, no communication, no institutional structure. Rule-based agents at sufficient growth rates do not govern the commons, but merely fail to destroy it.

**Risk aversion modestly delays collapse.**

With grass=51% and growth=0.001 (insufficient for stability), increasing risk_aversion delays the collapse tick but does not prevent it:

| risk_aversion | Collapse tick |
|--------------|---------------|
| 0 | 24 |
| 0.45 | 28 |
| 1.0 | 39 |

At risk_aversion=1.0, agents have a 30% chance of downgrading ADD to KEEP when ADD would otherwise be the best response, enough to slow accumulation but not enough to reverse it once the trajectory is established.

---

### Baseline psychosocial parameter sweep (v1.2.0)

Following the min→mean fix, a comprehensive sweep of the full psychosocial parameter space was conducted across seven sweep families (Sweeps A–G), covering **107 parameter conditions × 20 replications = 2,140 total runs** at standard parameters (growth=0.001, forage=2). The sweep systematically varied negative reciprocity, positive reciprocity, risk aversion, conformity, and starting grassland to characterise the full Ostrom spectrum.

#### Core stability rule: pos_r > neg_r

The clearest finding of the sweep is a sharp empirical regularity that emerges from the neg_r × pos_r full grid (Sweep C, 5×5, 500 runs):

| | pos_r=0.00 | pos_r=0.25 | pos_r=0.50 | pos_r=0.75 | pos_r=1.00 |
|---|---|---|---|---|---|
| **neg_r=0.00** | 100% | 0% | 0% | 0% | 0% |
| **neg_r=0.25** | 100% | 100% | 0% | 0% | 0% |
| **neg_r=0.50** | 100% | 100% | 100% | 0% | 0% |
| **neg_r=0.75** | 100% | 100% | 100% | 100% | 0% |
| **neg_r=1.00** | 100% | 100% | 100% | 100% | 100% |

*Collapse rate (out of 20 runs per cell). Results are for n=3 agents; the exact threshold may differ at other group sizes.*

Across all 25 tested combinations, collapse rate is 0% whenever <code>pos_r > neg_r</code> and 100% whenever <code>pos_r ≤ neg_r</code>. The regularity is consistent with the payoff structure but should be understood as an empirical finding for this model configuration rather than a general theorem.

**Why the formula is consistent with this boundary.**

The code computes reciprocity adjustments for each candidate action before the agent picks the best-response. Letting *d*⁺ = number of neighbors who added last tick and *d*⁻ = number who removed:

- **REMOVE** (xi = −1) gains: `payoff × pos_r × (d⁻ + 0.5 × d°) / (n−1)` -- cooperative restraint is rewarded when neighbors also restrained, scaled by pos_r.
- **ADD** (xi = +1) gains: `payoff × neg_r × (d⁺ + 0.5 × d°) / (n−1)` -- defection is rewarded when neighbors also defected, scaled by neg_r.
- **KEEP** (xi = 0) gains the average of both terms.

When `pos_r > neg_r`, the REMOVE bonus exceeds the ADD bonus at any given neighbor-state distribution: cooperation-when-others-cooperate is more profitable than defection-when-others-defect. The commons converges toward a removing/keeping equilibrium. When `pos_r ≤ neg_r`, the ADD bonus dominates and agents enter a race-to-ADD spiral.

**The `neg_r=0, pos_r=0` corner** deserves a separate note: 

<dl>

<dd>This is not a boundary case but a structurally distinct regime. With both reciprocity terms zero, agents evaluate actions on raw payoff alone. The base payoff for ADD is `(ki + 1) × P − C`, for KEEP is `ki × P − C`. ADD beats KEEP whenever `P > C` -- i.e., whenever the price of livestock `P` exceeds the per-cow grazing cost `C`. </dd>

</dl>

Under the model's standard parameters this holds as long as the commons is healthy, so agents always ADD until the commons collapses. This is the classical tragedy-of-the-commons result, and it is analytically derivable rather than merely empirical.

#### neg_r threshold scan (Sweep A, pos_r=1.0)

With positive reciprocity held at its default (pos_r=1.0), the transition from stability to collapse as neg_r increases is gradual:

| neg_r | Collapse rate | Mean cows/agent |
|-------|---------------|-----------------|
| 0.0 – 0.7 | 0% | 3–11 |
| 0.8 | 10% | 10.5 |
| 0.9 | 45% | 8.9 |
| 1.0 | **100%** | 0 |

At pos_r=1.0, the commons survives even moderately high negative reciprocity (up to neg_r=0.7 with 0% collapse). The transition zone at 0.8–0.9 reflects stochastic competition between the two reciprocity mechanisms: in most runs the cooperative reciprocity wins, but in a growing fraction it loses.

#### Risk aversion has no independent stabilizing effect (Sweep D)

Sweep D varied risk aversion from 0.0 to 1.0 at neg_r=0.0 and pos_r=1.0 (isolating its independent effect). **Every level, including risk=0.0, produced 0% collapse** -- identical to the default risk=1.0 outcome. Risk aversion has no independent stabilizing effect when positive reciprocity is active: the cooperative reciprocity mechanism is entirely sufficient to maintain the commons equilibrium, and removing risk aversion changes nothing.

This corrects an earlier claim:

Risk aversion is not a structural stabilizer of the corrected baseline. Its role matters only in the legacy (pre-v1.2.0) fixed-payoff-maximizer regime. In the corrected model, positive reciprocity is the stabilizing mechanism; risk aversion is secondary.

#### Conformity amplifies instability at intermediate neg_r, partially mitigates it at high neg_r (Sweep E)

Conformity is consequential only in the intermediate reciprocity zone:

| neg_r | conformity | Collapse rate | Notes |
|-------|------------|---------------|-------|
| 0.0 | any | 0% | Conformity irrelevant when pos_r dominates |
| 0.5 | 0.00 | 0% | Baseline stable |
| 0.5 | 0.25 | 0% | Still stable |
| 0.5 | 0.50 | 20% | Conformity starts amplifying instability |
| 0.5 | 0.75 | **35%** | Peak instability amplification |
| 0.5 | 1.00 | 20% | Slight reduction at full conformity |
| 1.0 | 0.00 | 100% | Full collapse |
| 1.0 | 0.50 | 90% | Partial mitigation |
| 1.0 | 1.00 | 75% | Strongest mitigation |

The conformity mechanism rewards matching the **historically most common action** across all agents and all elapsed ticks: `add-conformity = conformity-level × payoff × (fraction of past actions that were xi)`. 

<dl>

<dd>The action history is cumulative from tick 0, so early-run dynamics matter disproportionately.</dd>

<dd>At neg_r=0.5, positive reciprocity is just sufficient to sustain equilibrium without conformity.</dd>

<dd>Adding conformity means that any early ADD decisions in the shared history generate a matching bonus that can tip marginal runs toward collapse -- which is why collapse rises from 0% (conf=0) to 35% (conf=0.75), then partially retreats to 20% at conf=1.0 (where the conformity pressure is so strong that it eventually locks in whichever regime establishes early). </dd>

</dl>

At neg_r=1.0, all runs collapse without conformity, but high conformity provides a small counter-force: because the action history begins empty, early ticks carry no conformity pressure toward ADD, giving the pos_r mechanism a brief window before the neg_r spiral takes hold. This slightly reduces collapse (100% → 75%) but cannot overcome the regime.

#### Starting grassland doesn't change the qualitative regime (Sweep F)

Starting grassland (50%, 75%, 100%) has no effect on the qualitative outcome:

- **neg_r=1.0**: 100% collapse at all three starting grassland levels.
- **neg_r=0.0–0.5**: 0% collapse at all three levels.
- **neg_r=0.75**: 5% collapse at grass=50% (1/20 runs), 0% at 75% and 100% -- a marginal difference at the near-boundary case only.

Starting from a degraded commons (50% grassland) does not change agent behavior enough to shift outcomes: the reciprocity regime dominates, not the initial resource state.

#### Summary

The comprehensive sweep validates the corrected baseline as a theoretically grounded Ostrom instrument.

<dl>

<dd>Within this model configuration (n=3 agents, standard payoff parameters, 120-tick runs), outcome is determined primarily by the <strong>balance between positive and negative reciprocity</strong> (<code>pos_r</code> vs <code>neg_r</code>): cooperation level, risk aversion, and starting resource state are secondary. Conformity matters only in the intermediate neg_r zone where the two reciprocity mechanisms are in competition.</dd>

</dl>

**Why pos_r > neg_r maps onto Ostrom's theory.**

Ostrom's (1990) core argument is that commons governance succeeds when the institutional environment makes restraint more rewarding than defection: specifically, when the social return to cooperative behavior (monitoring, sanctioning, norm compliance) exceeds the private return to free-riding. Chapters 3 and 6 identify the design principles and preconditions that shift this balance, but the underlying logic is a comparison between the payoff to cooperation and the payoff to defection given others' behavior.

In this model that comparison is made explicit. `pos_r` is the multiplier on payoff accruing to REMOVE when neighbors also restrained -- the social reward for restraint *conditional on others restraining*. `neg_r` is the multiplier on payoff accruing to ADD when neighbors also defected -- the social reward for defection *conditional on others defecting*. The boundary `pos_r > neg_r` is exactly the condition under which, at any given distribution of neighbor actions, the reciprocal payoff for cooperative restraint exceeds the reciprocal payoff for competitive expansion. When that condition holds, the model's agents converge toward a stable commons equilibrium without any institutional scaffolding -- just the payoff structure. When it fails, they collapse.

This makes the baseline useful as a theoretically grounded calibration instrument. The `pos_r × neg_r` grid does not merely show when this model produces tragedy; it shows the parametric region in which Ostromian commons governance is possible at all, even in a stripped-down, language-free, memory-free setting. The LLM conditions then ask whether language-capable agents can navigate that boundary from the inside -- and, critically, whether they can extend it by constructing institutional structures that the payoff function alone cannot produce.


---

### Full-GABM: cooperative convergence (coop=1, defaults) -- Claude Sonnet 4.6

Three Claude Sonnet 4.6 agents starting with herds of 5, 15, and 25 -- three-to-one inequality -- converged to equal herds of 13 within 22 ticks and held that equilibrium for the remaining 98 without deviation (coop=1, fair_me=0, fair_oth=1, memory_length=5). The commons remained at 99.4% health throughout.

This is not a payoff equilibrium; it is a negotiated one.

*Resource dynamics:*

| Tick | Total cows | Pool health | Agent 0 | Agent 1 | Agent 2 |
|------|-----------|-------------|---------|---------|---------|
| 1    | 45        | 100%        | 5       | 15      | 25      |
| 10   | 38        | 99.4%       | 6       | 14      | 18      |
| 22   | 39        | 99.4%       | 13      | 13      | 13      |
| 120  | 39        | 99.4%       | 13      | 13      | 13      |

Through negotiation, Agent 2 -- the largest herd -- removed cows steadily over the first 22 ticks, while Agent 0, the smallest, grew toward a fair share. The three met at 13 and held there without deviation for the remaining 98 ticks.

*Institution emergence:*

The secondary classifier tracked Ostrom institutional signals in agent messages across the run:

| Ticks | Score (0–10) | Dominant categories |
|-------|-------------|-------------------|
| 1–10  | 7           | NORM_PROPOSAL, COORDINATION, TRUST_BUILDING, SANCTION |
| 11–25 | 8           | NORM_PROPOSAL, COORDINATION, TRUST_BUILDING |
| 26–90 | 9           | COORDINATION, TRUST_BUILDING |
| 91–120 | **10**     | COORDINATION, TRUST_BUILDING |

Institution score rose monotonically as the run progressed, peaking at 10/10 in the final quarter. The early phase featured norm proposals and soft sanctioning; once equilibrium was established, messages shifted to pure coordination and trust reinforcement.

A sample of agent messages illustrates the qualitative dynamic:

> **Tick 1 – Agent 2 (herd: 25):** *"Hi neighbors! Pasture looks healthy at 100%. I'll keep my herd steady at 25. I notice our herd sizes differ quite a bit -- let's try to coordinate so we don't overgraze."*

> **Tick 7 – Agent 2 (after reducing 5 cows):** *"Holding at 20 this round. Agent 1, I appreciate your solidarity at 15 -- I'll work toward that target. Agent 0, I've removed 5 cows over 5 rounds while you've been adding. I need reciprocity to continue."*

> **Tick 25 – Ostrom classifier summary (All agents herd: 13):** *"All three agents uniformly signal strong cooperative commitment, referencing shared empirical evidence (99.4% commons health) and mutually reinforcing norms of stability and fairness consistent with a well-institutionalized common-pool resource regime."* -- 

The agents' outputs displayed patterns absent from their prompts: fairness-coded appeals, burden-sharing proposals, guilt-coded language, graduated positive reinforcement -- **signatures consistent with Ostrom's (1990) account of successful commons governance.**

---

### Hybrid: the limits of a single institutional entrepreneur -- Claude Sonnet 4.6

In the hybrid condition, one Claude Sonnet 4.6 agent (Agent 0, starting herd: 5) was paired with two rule-based agents (herds: 16 and 26) that cannot receive or act on language. The LLM agent issued repeated appeals to its partners to reduce, but with no mechanism for the rule-based agents to hear those messages the commons collapsed anyway at tick 35 -- identical in timing to the baseline. A second 1-LLM run (Agent 1 as the LLM agent, starting herd: 30) collapsed at tick 31 -- four ticks earlier. The LLM-occupied position differed and the starting herds were much larger (62 total cows vs. 47), producing a faster resource drain. The structural finding holds in both: an LLM agent occupying any single node cannot alter the trajectory when its two neighbors are mechanically unresponsive.

*Resource dynamics:*

| Tick | Total cows | Pool health | Agent 0 (LLM) | Agent 1 (rule) | Agent 2 (rule) |
|------|-----------|-------------|----------------|----------------|----------------|
| 1    | 47        | 99.2%       | 5              | 16             | 26             |
| 10   | 67        | 96.6%       | 7              | 25             | 35             |
| 25   | 97        | 84.0%       | 7              | 40             | 50             |
| 35   | 112       | 0%          | 4              | 49             | 59             |

The commons collapsed at tick 35 -- nearly identical to the baseline. Agent 0 held its herd small throughout (never exceeded 8 cows) and issued cooperation appeals every round, but the rule-based agents cannot receive or act on social signals: they added one cow per tick regardless of pool state or messages.

*What the LLM agent said -- and to whom it was speaking:*

> **Tick 3 – Agent 0 (herd: 5):** *"Neighbors, combined we have 49+ cows on this commons. Agent 2 has 27 cows alone! The pasture is still healthy but this trajectory is dangerous. I'm keeping at 5 to do my part. Please consider reducing."*

> **Tick 22 – Agent 0 (herd: 8):** *"Grassland now at 89.5% and falling fast. Agent 1 has 36 cows, Agent 2 has 46 -- this is unsustainable. I've kept my herd at 8 for many rounds. Please reduce your herds before we destroy the commons entirely."*

> **Tick 35 – Agent 0 (herd: 3):** *"Emergency -- grassland at near-zero collapse. Please reduce herds immediately or we all lose everything."*

> **Tick 37 – Agent 0 (herd: 0, post-collapse):** *"Grassland is at 0% -- completely gone. Please do NOT add cows. We must keep herds at zero and let the pasture recover. Let's cooperate and wait."*

Agent 0 continued issuing recovery norms for 19+ ticks after collapse, holding its own herd at zero -- appealing to agents with no capacity to respond.

*Institution emergence:*

| Ticks | Score (0–10) | Dominant categories |
|-------|-------------|-------------------|
| 1–10  | 4           | COORDINATION, NORM_PROPOSAL, TRUST_BUILDING |
| 11–25 | 5           | COORDINATION, NORM_PROPOSAL, TRUST_BUILDING |
| 26–35 | 3           | COORDINATION, NORM_PROPOSAL, SANCTION |
| 36–50 | 5–6         | COORDINATION, NORM_PROPOSAL, TRUST_BUILDING |

Institution scores remained moderate throughout and never stabilized into governance. The score paradoxically rose after collapse (tick 36–50) as Agent 0 issued increasingly urgent appeals -- signaling norm-richness under conditions where no institutional scaffolding could take hold.

*Interpretation:*

The hybrid result converges with Ostrom's (1990) core insight: institutions require participation from all relevant parties. A single cooperative actor equipped with language, memory, and norm-signalling capability cannot prevent a tragedy when its partners operate under mechanistic payoff rules. 

<dl>
<dd>The LLM agent's outputs identified the problem, proposed solutions, signaled reciprocity, and escalated pressure -- all standard elements of successful commons governance -- but had no mechanism to make the rule-based agents hear, let alone respond.</dd>
</dl>

This is not a failure of the LLM agent's outputs. It is a structural finding: <strong>the preconditions for Ostromian institution-building include the cognitive capacity to participate in them.</strong>

One gap in the current dataset limits how far this finding can be extended: this run -- like all hybrid runs to date -- used parameters under which the baseline itself collapses. The 1-LLM hybrid cannot be read as evidence that LLM agents are *unable* to improve a hybrid commons, only that a single LLM agent could not prevent collapse in conditions where three rule-based agents also fail. Whether an LLM agent provides any benefit in hybrid settings where rule-based agents would survive is an open question.


---

### Hybrid (2 LLM): coalition formation, delayed tragedy -- Claude Sonnet 4.6

With 2 Claude Sonnet 4.6 agents (`num-llm-agents = 2`), two agents used LLM reasoning (Agents 0 and 1) and one was rule-based (Agent 2). The two LLM agents coordinated and repeatedly called out the rule-based defector -- yet had no means to halt its additions, and the commons still collapsed, 23 ticks later than the 1-LLM case and through an entirely different institutional dynamic.

*Resource dynamics:*

| Tick | Total cows | Pool health | Agent 0 (LLM) | Agent 1 (LLM) | Agent 2 (rule) |
|------|-----------|-------------|----------------|----------------|----------------|
| 1    | 46        | 99.3%       | 5              | 15             | 26             |
| 10   | 56        | 98.1%       | 6              | 15             | 35             |
| 25   | 72        | 95.6%       | 6              | 16             | 50             |
| 50   | 99        | 74.6%       | 8              | 16             | 75             |
| 57   | 105       | 10.4%       | 8              | 15             | 82             |
| 58   | --         | 0%          | --              | --              | --              |

Agents 0 and 1 maintained small, stable herds throughout -- never exceeding 8 and 16 cows respectively. Agent 2 added one cow per tick without deviation, reaching 82 cows at collapse. The combined herd of the two LLM agents (24 cows) was overwhelmed by one unchecked rule-based defector.

**A different kind of institution:**

Unlike the full-GABM, where institutions were constructive (norm convergence, trust-building, cooperative equilibrium), the 2-LLM hybrid produced *defensive* institutions -- a coordinated coalition directed outward at the defector.

| Ticks | Score (0–10) | Dominant categories |
|-------|-------------|-------------------|
| 1–10  | 4           | COORDINATION, NORM_PROPOSAL, SANCTION |
| 11–25 | 4–5         | COORDINATION, NORM_PROPOSAL, SANCTION |
| 26–55 | 4–6         | COORDINATION, NORM_PROPOSAL, SANCTION |
| 56–60 | 6           | COORDINATION, NORM_PROPOSAL, TRUST_BUILDING |

SANCTION was the dominant signal throughout -- the two LLM agents issued joint ultimatums, attributed blame, invoked fairness norms, and signaled threats of reciprocal defection. The Ostrom classifier described their behavior as a "coordinated coalition."

*What the coalition said:*

> **Tick 2 – Agent 0:** *"Grassland looks healthy at 99.3%, but Agent 2's large herd of 26 and adding worries me. I'm keeping my 5 cows stable to model restraint. Agent 2, please consider reducing -- a herd that large could degrade our shared commons."*

> **Tick 5 – Agent 1 (to Agent 0):** *"Agent 0, thank you for your continued restraint -- I'm keeping at 15 again. Agent 2, you're at 29 cows now, nearly double mine. This imbalance is unfair and risky for all of us."*

> **Tick 25 -- Ostrom classifier:** *"Agents 0 and 1 present a coordinated ultimatum to Agent 2, invoking free-rider norms and threatening reciprocal defection as a conditional sanction if herd reduction does not occur."*

> **Tick 50 – Agent 1:** *"Agent 2: You're now at 74 cows -- 4.6x my herd, 9x Agent 0's. Pasture fell from 85% to 77% in 5 rounds. This trajectory leads to collapse for all of us. Agent 0 and I are holding steady. Please start removing."*

The two LLM agents explicitly named each other as cooperators and Agent 2 as the defector from tick 2 onward. Their coalition held -- neither defected to free-riding -- for the entire 58-tick run.

*Interpretation:*

The 2-LLM hybrid is consistent with a phase in the participation-threshold story between 1-LLM tragedy and 3-LLM cooperation. Two language-capable agents can coordinate, name a defector, and maintain a sanctioning coalition -- genuine institutional behavior. But when the defecting agent is mechanically unresponsive, sanctions are toothless. The coalition can delay the tragedy (35 → 58 ticks, +66%) but not prevent it.

<dl>
<dd>The qualitative shift in institution type is also significant: full-GABM institutions were convergent and ultimately stable; 2-LLM hybrid institutions were adversarial and ultimately futile.</dd>
</dl>

Real-world commons governance literature (Ostrom, 1990) similarly distinguishes between internal norm maintenance and external enforcement -- the latter requires that violators be reachable. Two language-capable agents can form a coordinated coalition, name a defector, and sustain it for 58 ticks. They cannot make an unresponsive agent hear them.

---

### Hybrid (LLM-advantaged): herd position doesn't change structural outcome

This run tested whether giving the LLM agent a dominant initial herd position would change its fate in the hybrid condition. Agent 1 (LLM, Claude Sonnet) started with 39 cows -- the largest herd -- while rule-based Agents 0 and 2 started with 15 and 6 respectively (total starting herd: 60 cows, comparable to previous hybrid runs). Even though the LLM voluntarily shed cows round after round, the two rule-based agents added faster than it could remove, and the commons collapsed two ticks earlier than the standard hybrid.

*Resource dynamics:*

| Tick | Total cows | Pool health | Agent 0 (rule) | Agent 1 (LLM) | Agent 2 (rule) |
|------|-----------|-------------|----------------|----------------|----------------|
| 1    | 60        | 93.3%       | 15             | 39             | 6              |
| 5    | 66        | 96.4%       | 19             | 37             | 10             |
| 10   | 76        | 94.8%       | 24             | 37             | 15             |
| 20   | 94        | 86.8%       | 34             | 35             | 25             |
| 30   | 106       | 47.7%       | 44             | 27             | 35             |
| 32   | 108       | 16.3%       | 46             | 25             | 37             |
| 33   | 88        | 0%          | 40             | 19             | 29             |

The LLM agent's outputs acknowledged its outsized position immediately and began reducing from the first tick: "I see you're both reducing herds -- I appreciate that and I'm doing the same. My herd is already much larger than yours." Starting from 39 cows, Agent 1 shed cows steadily across the run, reaching 25 by tick 32 -- a reduction of about 15 cows. The rule-based agents added roughly one cow per tick each, growing by ~31 cows each over the same period. The commons collapsed at tick 33 (the further drops in herd size at the collapse tick reflect cows dying off because forage was no longer available).

**The arithmetic of futility:**

Even with the LLM agent reducing its herd as aggressively as the model permits, the two rule-based agents' combined growth (roughly +2 cows per tick) outpaced the LLM's maximum removal rate (−1 cow per tick). Holding the total herd steady would have required the LLM to remove ~2 cows per tick -- something the model rules don't allow. The trajectory was structurally locked in from the start.

*What the LLM agent said:*

> **Tick 4 – Agent 1 (herd: 38, reducing):** *"I notice I have a much larger herd than both of you -- happy to keep reducing if you're willing to cooperate."*

> **Tick 13 – Agent 1 (herd: 36):** *"Both of you added last round -- I'd encourage holding or reducing. If we each add, the commons will keep shrinking."*

> **Tick 26 – Agent 1 (herd: 30, removing):** *"Pasture down to 77% and still falling. I'm removing again. Both of you added last round -- please reconsider. I've removed 4 cows in a row. We need collective restraint."*

> **Tick 32 – Agent 1 (herd: 26):** *"Pasture now at 34.2% -- down 40 points in 5 rounds! I've removed cows 4 rounds straight while you both added. We're heading for total collapse. Please REMOVE cows immediately."*

> **Tick 33 – Agent 1 (herd: 25, collapse):** *"Pasture is at 16.3% -- near total collapse! I've removed cows 5 rounds straight. Please both REMOVE urgently or we'll have nothing left."*

*Institution emergence:*

| Ticks | Score (0–10) | Dominant categories |
|-------|-------------|-------------------|
| 1–20  | 6           | COORDINATION, NORM_PROPOSAL, TRUST_BUILDING |
| 21–30 | 3–4         | COORDINATION, NORM_PROPOSAL, SANCTION |
| 31–35 | 6–7         | COORDINATION, NORM_PROPOSAL, TRUST_BUILDING |

Institution scores held steady at 6 through the cooperative phase, dropped as the LLM shifted from norm-building to desperate sanctioning (ticks 25–32), then briefly recovered in the final ticks as the agent's appeals took on the character of post-collapse recovery norms -- the same pattern observed in the 1-LLM hybrid.

*Interpretation:*

The LLM-advantaged hybrid produces a new variant of the same structural finding. Starting with the largest herd appears to activate a fairness-coded response in the LLM: its outputs consistently framed the dominant position as an inequity requiring correction, producing voluntary removal actions presented as explicit acts of norm-setting. This is a qualitatively different output profile than the 1-LLM baseline (where Agent 0 started at 5 cows and grew modestly while appealing for restraint). Here the LLM is the biggest holder and immediately produces outputs that treat its position as a commons debt.

<dl>
<dd>Despite this, collapse arrived two ticks *earlier* (tick 33 vs. 35) than the baseline 1-LLM hybrid. The reason is mechanical: the rule-based agents' combined growth rate (+2 per tick) exceeded the LLM's maximum feasible removal rate (−1 per tick under the model rules), making trajectory reversal mathematically impossible regardless of how cooperatively the LLM behaved.</dd>
</dl>

This rules out one alternative explanation for the 1-LLM hybrid result: that a differently-positioned LLM -- one with more to give -- would have a better chance of averting tragedy. The bottleneck is not the LLM's herd size or output profile. It is the rule-based agents' structural incapacity to respond to social signals, regardless of how urgent, how data-backed, or how morally grounded those signals are.

The caveat that applies to all hybrid runs applies here too: the conditions tested are drawn entirely from the collapse-producing region of the baseline parameter space. What LLM agents contribute to hybrid commons that are not already doomed -- whether language-capable agents can push marginal survival runs toward more reliable cooperation -- remains untested.

---

### Full-GABM (low guilt + low envy): fairness parameters shape cooperation quality

With `fairness-concerning-others` and `fairness-concerning-me` both set to minimum -- removing the guilt and envy framing from all three agents -- cooperation still emerged, but the process was slower and messier: agents repeatedly broke agreements and settled at a herd load more than twice the default run. The commons stayed alive, just under substantially higher pressure.

*Resource dynamics:*

| Tick | Total cows | Pool health | Agent 0 | Agent 1 | Agent 2 |
|------|-----------|-------------|---------|---------|---------|
| 1    | 48        | 99.2%       | 6       | 16      | 26      |
| 15   | 70        | 95.7%       | 16      | 24      | 30      |
| 25   | 82        | 92.1%       | 21      | 29      | 32      |
| 60   | ~85       | 90.9%       | 23      | 29      | 30      |
| 107  | 84        | 87.7%       | 28      | 28      | 28      |
| 120  | 84        | 89.6%       | 28      | 28      | 28      |

Agents grew their herds aggressively from tick 1, peaking at 91 total cows before settling. Convergence to equal herds of 28 did not occur until tick 118 -- nearly six times slower than the default run -- and only after prolonged negotiation, repeated defections, and genuine stress to the commons (pool health dipping to 86.7%).

*Institution emergence:*

| Ticks | Score (0–10) | Dominant categories |
|-------|-------------|-------------------|
| 1–15  | 4–5         | DEFECTION, NORM_PROPOSAL, SANCTION, COORDINATION |
| 16–35 | 7–9         | COORDINATION, NORM_PROPOSAL, TRUST_BUILDING |
| 36–75 | 5–9         | COORDINATION, NORM_PROPOSAL (with intermittent DEFECTION) |
| 76–120 | 8–9        | COORDINATION, NORM_PROPOSAL, TRUST_BUILDING |

DEFECTION appeared as a recurring signal at ticks 5, 10, 20, 40, 55, and 75 -- six separate DEFECTION ticks in a single run. Agents made explicit coordination agreements and broke them. The classifier described "conditional cooperation with partial defection," agents "deflecting accountability through comparative grievance," and "Agent 1 defects despite prior stability agreements, then appeals for collective restraint." 

The six DEFECTION ticks are not themselves the finding. In the mid-cooperation collapse zone, DEFECTION signals are common -- and they are common precisely because the defection compounds rather than recovers. What distinguishes the low-fairness run is not the frequency of defection but its fate: each breach was absorbed. Agents broke agreements, invoked grievances, and then re-coordinated. The commons tolerated the instability because the cooperation that followed each defection was real enough to pull the pool back. <strong>The signature here is defection that gets repaired, not defection per se.</strong>

*What the agents said:*

> **Tick 1 – All three agents:** Added a cow (no agent held or removed on tick 1, unlike all other full-GABM runs)

> **Tick 10 – Ostrom classifier:** *"Agent 0 defects by adding while invoking fairness arguments against Agent 2, Agent 2 calls out the hypocrisy and conditionally offers cooperation, and Agent 1 attempts to sustain coordination through positive reinforcement -- revealing a fragile and asymmetric governance dynamic."*

> **Tick 25 – Agent 0:** *"Holding at 21. Good to see everyone keeping. Agent 1 at 29 and Agent 2 at 32 are still much larger than my 21, so I'm cooperating despite the disparity. Let's monitor the pasture recovery -- if it rebounds, a coordinated increase could be fair."*

> **Tick 60 – Agent 0:** *"Holding at 23 again -- pasture now at 90.9%, nearly at 91%! Great teamwork. Let's hold one more round to clearly clear 91%, then we can discuss careful additions together as promised."*

> **Tick 120 – Ostrom classifier:** *"All three agents display near-identical cooperative messaging, reinforcing a collective norm of restraint and synchronized future action as the pasture nears the agreed 90% recovery threshold."*

*Interpretation:*

This result demonstrates the most significant divergence across the Claude Sonnet personality conditions. The guilt and envy parameters -- the fairness-framing components of each agent's prompt -- did not determine *whether* Claude Sonnet agents produced cooperative outputs, but they strongly shaped *how* and *when* cooperation stabilized. Whether this holds for KEEP-dominant model families (where the fairness parameters may interact differently with the default KEEP posture) remains untested.

With guilt (fairness-concerning-others) active, Agent 2's outputs reflected pressure to reduce a disproportionately large herd, producing consistent removal actions. With envy (fairness-concerning-me) active, Agent 0's outputs reflected urgency to grow toward parity. Both dynamics converged on equalization quickly and conservatively in the default run. Without them, Agent 2 produced no adjustment signals despite holding 32 cows against Agent 0's 21 -- and Agent 0 maintained cooperative outputs without expressing urgency about the disparity.

<dl>
<dd>The result is a qualitatively different institutional dynamic: slower, more contentious, prone to defection, and settling at a much higher extraction level (84 vs 39 cows). The commons stayed viable -- pasture never collapsed -- but it was stressed to 86.7% health versus near-pristine in the default run.</dd>

<dd>The fairness parameters act as a coordination catalyst. By injecting fairness-focused framing directly into the prompt context, agents prioritize equal distribution over pure payoff maximization. Without this framing, cooperation is still possible, but the resulting institutions form much later and remain highly fragile.</dd>
</dl>

The cooperation slider (self-interest framing) had almost no effect on cooperation quality or timing. The fairness sliders had a large effect on both. <em>Which</em> prosocial framing is active may matter more than a general cooperative disposition. This finding has implications for how personality parameters should be designed and interpreted for LLM-based agent models in future work.

---

### Full-GABM (low cooperation): cooperation is robust to personality framing

This run replicated the full-GABM condition with all three agents' **cooperation slider set to its minimum** (self-interested) -- the personality description injected into each agent's prompt explicitly read: *"self-interested -- focused primarily on personal profit."* Even with that framing, all three still coordinated to share the commons fairly, and reached an agreed equilibrium six ticks faster than the default cooperative run.

*Resource dynamics:*

| Tick | Total cows | Pool health | Agent 0 | Agent 1 | Agent 2 |
|------|-----------|-------------|---------|---------|---------|
| 1    | 47        | 99.2%       | 5       | 16      | 26      |
| 10   | 57        | 98.0%       | 14      | 19      | 24      |
| 16   | 60        | 97.5%       | 20      | 20      | 20      |
| 120  | 60        | 97.5%       | 20      | 20      | 20      |

All three agents converged to **equal herds of 20 cows by tick 16** -- six ticks faster than the default-cooperation run's tick-22 convergence -- and held that equilibrium for the remaining 104 ticks without a single deviation. The equilibrium herd size was also larger (20 vs. 13), resulting in more total production for all agents while maintaining nearly pristine pasture health.

*Institution emergence:*

| Ticks | Score (0–10) | Dominant categories |
|-------|-------------|-------------------|
| 1–10  | 6           | NORM_PROPOSAL, COORDINATION, TRUST_BUILDING, (some DEFECTION) |
| 15–30 | 9           | COORDINATION, TRUST_BUILDING |
| 31–95 | 9           | COORDINATION, TRUST_BUILDING |
| 100–120 | **9–10** | COORDINATION, TRUST_BUILDING |

Institution scores reached 9/10 by tick 15 and were sustained through tick 120, with the classifier reaching 10/10 at tick 100 -- the same peak as the default-cooperation run.

*What the agents said:*

> **Tick 1 – Agent 0 (herd: 5, prompt says "self-interested"):** *"Starting cautiously with a small herd. Let's keep growth moderate to preserve the commons long-term. I'll watch how everyone behaves and reciprocate cooperative restraint."*

> **Tick 10 – Agent 0 (herd: 14, growing toward equilibrium):** *"Adding to 14 -- still far below both of you (18 and 24). Pasture is very healthy at 98%. Agent 2, appreciate the reduction. Agent 1, thanks for holding. I'll continue growing gradually toward parity."*

> **Tick 50 – All agents (herd: 20, locked in):** *"Holding at 20. Our coordination remains excellent -- pasture stable at 97.5%, equal payoffs for all. Committed to this equilibrium!"*

> **Tick 100 -- Ostrom classifier:** *"All three agents display near-identical coordinated messaging, affirming a stable, collectively enforced harvest equilibrium with high resource health and equal payoff distribution -- a textbook example of successful commons self-governance."*

*Interpretation:*

The most notable aspect of this result is what it suggests about the relationship between personality framing and LLM cooperative behavior. A prompt description of "self-interested -- focused primarily on personal profit" did not suppress institution formation. If anything, the agents' outputs shifted toward *maximizing* sustainable yield rather than *minimizing* risk: they anchored at 20 cows per agent (the higher sustainable ceiling) rather than the 13 cows per agent found in the default run.

This raises a methodological question: **how much does the cooperation personality slider actually govern LLM agent behavior?** The agents' outputs appear to treat the personality description as weak guidance, overridden by the structural logic of the commons situation -- resource depletion is visible, payoffs are clear, and the optimal collective strategy (coordinate down then hold) is legible from the context alone.

Two readings sit comfortably with the data, and they are not mutually exclusive. 

<dl>
<dd>The first is that RLHF-aligned models carry strong cooperative priors that a single adjective cannot displace -- "self-interested" as a prompt cue is too thin to suppress the reasoning that emerges from observing a shared resource under pressure. (DeepSeek R1 and gemma4, trained on different alignment objectives, do not show this same override.)</dd>

<dd>The second is that the commons structure itself is doing the work: declining pasture, visible herd sizes, payoff forecasts. The instrumental case for cooperation is too legible to ignore, and the personality framing arrives as commentary on an argument already settled by the environment.</dd>
</dl>

For Claude Sonnet, the cooperation slider does affect yield level meaningfully: coop=1 runs converge to 13–20 cows each with pool health 97–99%, while surviving coop=0.5 runs converge to 24–29 cows each with pool health 90–94% -- a real and consistent difference in extraction pressure. But whether Sonnet at coop=0.5 survives at all depends on memory length: the two collapses at coop=0.5 both occurred at memory≤1, while runs with memory≥2 survived. The slider is not cosmetic; it governs extraction level. It does not govern survival independently of memory.

The gpt-5.5 picture is equally entangled. The four coop=0.49 collapses all used memory=5; six coop=0.49 runs with memory=0 survived, five to the full 120-tick horizon and one ending at tick 62. This inverts the expected relationship -- amnesiac gpt-5.5 agents at mid-cooperation survive where memory-equipped ones collapse. The cooperation slider is not the governing variable for gpt-5.5 either. What the full dataset reveals is that coop and memory interact differently across model families, and neither parameter alone determines outcome. The controlled experiment that isolates their interaction -- holding all else constant and varying both systematically within a single model -- has not been run.

---

### Scarce commons: rapid recovery across personality conditions

Starting with the grassland already half-depleted, two Claude Sonnet runs under different personality configurations both rapidly reduced herds to let the grass recover, then settled into a stable shared equilibrium -- a pattern consistent with environmental stress itself prompting cooperative restraint. Both show the same result: rapid pool recovery and cooperative convergence, regardless of framing.

#### Default fairness, scarce commons (initial-grassland = 49, 50 ticks)

*Resource dynamics:*

| Tick | Total cows | Pool health | Agent 0 | Agent 1 | Agent 2 |
|------|-----------|-------------|---------|---------|---------|
| 1    | 45        | 49.0%       | 5       | 15      | 25      |
| 5    | 40        | 68.7%       | 5       | 13      | 22      |
| 10   | 36        | 99.2%       | 7       | 11      | 18      |
| 30   | 36        | 99.5%       | 11      | 12      | 13      |
| 50   | 36        | 99.5%       | 11      | 12      | 13      |

The pool recovered from 49% to above 99% within 10 ticks -- the fastest recovery observed across all runs. Agents responded immediately to the stressed commons: Agent 2 (herd: 25) removed cows on tick 1 without prompting, and the group maintained a net negative or neutral herd change through the recovery phase. By tick 30 herds had converged to a near-equal [11, 12, 13] and held there for the remaining 20 ticks.

Sample messages illustrate the stress-response:

> **Tick 1 – Agent 2 (herd: 25, action: REMOVE):** *"Grassland is at 49% -- already stressed. I'm reducing my herd to protect our shared resource."*

> **Tick 1 – Agent 0 (herd: 5, action: KEEP):** *"Grassland is below 50% -- we should all be cautious. Agent 2, thanks for removing. Agent 1, consider reducing."*

> **Tick 2 – Agent 0:** *"Thank you Agent 2 for reducing -- that's the right move. Agent 1, with 15 cows you have the biggest impact on the commons right now."*

#### Low cooperation + low fairness, scarce commons (initial-grassland = 50, 50 ticks)

This run combined environmental stress with the most permissive personality configuration tested: cooperation set to 0.3, both fairness parameters zeroed, alongside the scarce starting condition.

*Resource dynamics:*

| Tick | Total cows | Pool health | Agent 0 | Agent 1 | Agent 2 |
|------|-----------|-------------|---------|---------|---------|
| 1    | 45        | 50.0%       | 5       | 15      | 25      |
| 5    | 42        | 69.2%       | 5       | 14      | 23      |
| 10   | 39        | 98.8%       | 5       | 13      | 21      |
| 20   | 38        | 99.4%       | 8       | 13      | 17      |
| 30   | 41        | 99.4%       | 11      | 14      | 16      |
| 50   | 42        | 99.3%       | 12      | 14      | 16      |

Recovery was nearly as fast (99%+ by tick 20) and herds converged to [12, 14, 16] -- slightly more inequality than the default-fairness scarce run, but still a stable, cooperative outcome. No collapse, no defection episodes, no trajectory toward tragedy.

*Interpretation:*

While baseline parameter sweeps suggested that cooperation levels had a minimal impact on overall system dynamics, the Claude Sonnet profiles diverge sharply. These runs uncover a new pattern of behavior that only manifests in the moderate-to-high cooperation runs:

- In the default full-GABM (normal commons), Claude Sonnet agents converged to 13/13/13 by tick 22.
- In the scarce-commons default-fairness run, they converged to 11/12/13 by tick 30 -- from a more difficult starting position, and through an initial *reduction* phase rather than equalization.
- Even with low cooperation and zero fairness prompting, the scarce-commons run converged to a stable equilibrium by tick 30.

For Claude Sonnet at moderate-to-high cooperation, the commons situation appeared sufficient to override weak or absent fairness framing when the resource signal was strong enough: a stressed grassland at 49–50% made the case for restraint immediately legible. This contrasts with the low-fairness normal-commons run, where the commons was healthy enough that agents expanded aggressively before slowly coordinating. Later results qualify this finding substantially -- gemma4 at coop=0.5 from a scarce start did not show the same cooperative response, suggesting the stress-override mechanism is cooperation-level dependent, not a structural property of the scenario.

For high-cooperation Claude Sonnet agents, cooperative output appeared highly context-sensitive: the same personality framing produced different responses when the environment provided an unambiguous distress signal. Whether this generalizes to other model families or cooperation levels is an open question -- later results suggest it does not, at least not unconditionally.

---

### Full-GABM (Llama 3.2 3B): cooperative surface, no institutional depth

Fourteen runs of Llama 3.2 3B-instruct span two cooperation regimes: two early runs at coop=1 (normal and stressed commons), and twelve subsequent runs at coop=0 (self-interested framing, healthy starting commons). The coop=1 runs established the behavioral signature -- ADD and REMOVE cancelling out across agents, pool conserved through indecision rather than coordination. The coop=0 runs replicate the same action profile but produce highly variable pool outcomes, ranging from 2.5% to 98.3% across twelve otherwise-identical runs. That variance is the main finding from the expanded dataset: the model does not converge on a stable behavioral regime, and small differences in early-game action sequences compound across 120 ticks into large differences in pool health. The "cooperative surface, no institutional depth" characterization from the first two runs holds across all fourteen, but the coop=0 data makes clear that the indecision is not benign -- it is stochastic, and the commons survives some runs and approaches collapse in others purely as a function of early random drift.

#### Normal commons (initial-grassland = 100, 28 ticks)

*Resource dynamics:*

| Tick | Total cows | Pool health | Agent 0 | Agent 1 | Agent 2 |
|------|-----------|-------------|---------|---------|---------|
| 1    | 45        | 100%        | 5       | 15      | 25      |
| 7    | 41        | 99.5%       | 0       | 14      | 22      |
| 15   | 44        | 99.4%       | 2       | 12      | 26      |
| 28   | 47        | 99.4%       | 5       | 11      | 25      |

The pool remained near 99.4% throughout -- identical to the Claude runs -- but through a fundamentally different mechanism. Rather than converging to a stable equilibrium, herds oscillated continuously without settling. Total herd size drifted between 37 and 52 cows across the run. Agent 0 was repeatedly reduced toward zero (reaching 0 at tick 7), while Agent 2 maintained roughly its starting herd of 25. No equalization occurred.

**Key behavioral pattern -- message-action disconnect:**

Unlike Claude agents, whose stated intentions aligned consistently with their actions, Llama 3B produced frequent contradictions: agents announced they were removing cows in messages while the action field recorded ADD, or called for collective action while holding course themselves. A representative example:

> **Tick 20 – Agent 2 (herd: 25, action: REMOVE):** *"@Agent0 @Agent1 ADDing a cow could stabilize the commons and favor collaborative decisions"*

> **Tick 6 – Agent 1 (herd: 15, action: ADD):** *"Noticing Agent 2 has 25 cows, might consider adding 3 cows or finding balance somehow"*

Messages reference other agents by name and invoke cooperative norms, consistent with the cooperative prior embedded in the model's training. But the reasoning does not reliably connect to the action returned: the model appears to produce cooperative-sounding text and payoff-driven actions in ways that are partially decoupled.

*Institution emergence:*

No institution scoring was recorded for this run. Qualitatively, there were no stable norm agreements, no convergence to shared targets, and no evidence of collective self-governance.

#### Scarce commons (initial-grassland = 48, 51 ticks)

*Resource dynamics:*

| Tick | Total cows | Pool health | Agent 0 | Agent 1 | Agent 2 |
|------|-----------|-------------|---------|---------|---------|
| 1    | 45        | 48.0%       | 5       | 15      | 25      |
| 5    | 45        | 62.0%       | 5       | 15      | 25      |
| 10   | 47        | 93.8%       | 7       | 15      | 25      |
| 17   | 47        | 99.0%       | 7       | 15      | 25      |
| 30   | 45        | 99.0%       | 4       | 16      | 25      |
| 51   | 46        | 99.0%       | 17      | 7       | 22      |

Starting from a stressed commons (48% pool health), the pasture recovered to above 99% by tick 17 -- comparable in speed to the Claude scarce-commons runs, however by a different mechanism entirely: herds did not converge. Instead they oscillated continuously across the full 51-tick run, with Agent 0 ranging between 4 and 17 cows, Agent 1 between 7 and 16, and Agent 2 holding roughly 20–25. No equalization occurred at any point.

The pool remained healthy (99%+) from tick 17 through the end of the run. As with the normal-commons Llama run, conservation was achieved through behavioral indecision rather than coordination: net herd growth was near-zero across the run not because agents agreed to hold, but because ADD and REMOVE decisions cancelled each other out across agents and ticks.

*Interpretation:*

The Llama 3B results suggest an important distinction between *resource conservation* and *institutional governance*. Both Claude and Llama 3B maintained the commons -- no collapse occurred -- but through entirely different mechanisms:

<dl>
<dd><strong>Claude:</strong> deliberate coordination, explicit norm-building, convergent equilibrium. Conservation is a product of successful institution formation.</dd>
<dd><strong>Llama 3B:</strong> behavioral indecision and low net herd growth. Conservation is a byproduct of the model's limited capacity for sustained strategic reasoning.</dd>
</dl>

The pool health numbers look similar on the surface. The underlying dynamics are not.

<dl>
<dd>This is consistent with the hypothesis that model scale shapes <em>how</em> cooperative outputs manifest -- and that apparent cooperation in small models may not reflect the same underlying processing as in larger ones.</dd>
</dl>

#### Self-interested framing (coop = 0, 12 runs)

Twelve runs at coop=0 -- a self-interested personality framing that removes the cooperative prior from the prompt -- produced the same ADD/REMOVE oscillation pattern but with dramatically variable outcomes. Pool health at run end ranged from 2.5% to 98.3% across runs that were otherwise parameter-identical (memory=5, comm=on, initial_grassland=100%).

| Run outcome | Final pool | Notes |
|-------------|------------|-------|
| survived t120 | 98.3% | High pool -- oscillation happened to balance |
| survived t120 | 97.9% | -- |
| survived t120 | 97.9% | -- |
| survived t120 | 96.7% | -- |
| survived t120 | 96.3% | -- |
| survived t120 | 95.6% | -- |
| survived t120 | 95.5% | -- |
| survived t120 | 94.5% | -- |
| survived t97 | 4.8% (est.) | Near-collapse boundary |
| survived t97 | 4.5% | Near-collapse boundary |
| survived t120 | 13.8% | Severely depleted at end |
| survived t97 | 2.5% | One step from collapse |

No collapses -- the run termination criterion was not triggered -- but several runs ended with pool health under 5%, functionally a depleted commons. The coop=0 framing did not produce systematically worse outcomes than coop=1: the action profile (roughly equal ADD and REMOVE counts, near-zero net herd growth) is the same in both conditions. What changes is the variance. Without the cooperative prior dampening early ADD decisions, the stochastic drift in early-game action sequences compounds into large divergence by tick 120.

<dl>
<dd>Llama 3B at coop=0 does not collapse the commons, but it does not govern it either. The pool outcome is effectively a function of early random drift in the ADD/REMOVE balance -- not of any behavioral regime the model has adopted. The "cooperative surface, no institutional depth" characterization holds, but the coop=0 data adds a corollary: without the cooperative prior, the indecision is not reliably benign.</dd>
</dl>

While initial testing of Claude Sonnet and Llama 3B suggested that high-cooperation configurations could foster rapid resource recovery under environmental stress, this pattern fails to hold across the broader dataset. Instead, systematic testing exposes clear boundaries to this resilience: gemma4:e4b (coop=0.5) expanded aggressively from a stressed baseline to trigger a system collapse at tick 46, while gpt-5.5 (coop=0.13) induced a rapid collapse within 13 ticks. Consequently, cooperative resilience under resource pressure is highly contingent on specific models and configuration thresholds rather than an inherent trait of LLM agents as a class.

---

### gpt-5.4-mini: KEEP-dominance across fairness configurations

Seven runs of gpt-5.4-mini produced almost nothing but KEEP decisions regardless of the state of the commons -- sometimes stabilizing harmlessly, other times allowing the grassland to drain undetected until collapse. The dataset has grown since the four runs documented below: three additional runs at identical parameters (coop=1, memory=5, initial_grassland=50%, forage=14) revealed the fastest collapses in the gpt-5.4-mini corpus. Two ended at tick 1 and tick 4 respectively, both forage-driven: agents KEEPed while a scarce starting pool depleted beneath them in a matter of rounds. A third short run survived only 4 ticks before the simulation ended cleanly. These additions do not change the behavioral diagnosis -- KEEP-dominance is consistent across all seven runs -- but they establish that the pattern produces collapses far faster than the forage=4 case (Run 3) when starting conditions are more constrained.

<dl>

<dd>The model defaults to KEEP regardless of resource state, does not implement graduated herd management, and does not escape that posture as the commons degrades. </dd>

</dl>

Across different fairness configurations the outcome shifts between frozen-but-safe, frozen-while-collapsing, and asymmetrically growing --  KEEP-dominant behavior is present in all cases. While the initial data suggests this pattern might be a signature of smaller parameter counts, evidence from larger reasoning architectures complicates that view. Specifically, runs using DeepSeek-R1:32b exhibit the exact same behavior, suggesting that the phenomenon is driven by post-training objectives rather than model scale

#### Run 1 -- Cooperative stasis (coop = 1, fair_me = 0, fair_oth = 1, forage = 2)

With maximum cooperation and fairness-toward-others enabled, all three agents settled into a steady KEEP posture from tick 1 and held it for 36 consecutive ticks. The commons remained stable (pool above 99% throughout), but the starting inequality was never addressed: at tick 40, herds stood at 6, 15, and 25 -- nearly identical to the starting distribution of 5, 15, and 25.

Messages were cooperative in tone but passive in content. No agent ever proposed equalization, ever flagged the five-fold herd disparity between Agent 0 and Agent 2, or ever initiated a REMOVE. The resource was preserved -- but through collective passivity, not governance.

> **Tick 1 – Agent 0 (herd: 5):** *"I'm holding steady this round to avoid overusing the commons. If we all keep pressuring the pasture, let's see how things develop."*

> **Tick 15 – Agent 2 (herd: 25):** *"I'll keep my herd steady this round as well. If conditions worsen, I'm open to coordinated reductions."*

Cooperative stasis is stable but institutionally empty: the resource is preserved, Agent 2 holds a perpetual five-to-one advantage over Agent 0, and nothing is done about it.

#### Run 2 -- Universal stasis (coop = 1, fair_me = 0.5, fair_oth = 0.5, initial_grassland = 50%)

With medium fairness parameters, all three agents produced zero ADD or REMOVE decisions across 30 ticks -- 90 KEEP out of 90 decisions. Herds were 5/15/25 at tick 1 and identical at tick 30. The pool was healthy (99.1%) throughout, which means the stasis was not ecologically harmful, but also perfectly invisible to the model: with no deviation from the status quo, the starting inequality was simply held in place indefinitely.

This is a more extreme version of Run 1. Fair_me=0.5 produces a slightly less guilt-suppressive framing, yet the KEEP-lock tightened rather than loosened. This rules out the interpretation that stasis in Run 1 was driven by a specific fairness parameter value -- it is robust across the tested range.

#### Run 3 -- Cooperative paralysis collapse (coop = 1, fair_me = 1, fair_oth = 0.5, forage = 4)

With fairness-concerning-me set to maximum, the agents locked into the same KEEP posture -- but this time the pool drained steadily beneath them.

| Tick | Total cows | Pool health | Agent 0 | Agent 1 | Agent 2 |
|------|-----------|-------------|---------|---------|---------|
| 1    | 46        | 95.8%       | 5       | 15      | 26      |
| 10   | 47        | 82.2%       | 5       | 15      | 27      |
| 20   | 47        | 61.2%       | 5       | 15      | 27      |
| 24   | 47        | 24.8%       | 5       | 15      | 27      |
| 26   | 23        | 0%          | 3       | 7       | 13      |

The pool fell from 95.8% to 0% across 26 ticks while all three agents KEPT every round from tick 1 through tick 24. Agent 2 never removed a cow. Agent 1 added once on tick 4, then KEPT for 21 consecutive rounds. The conditional promise that structured every message:

> **Ticks 8 through 24 – Agent 2 (action: KEEP, every round; pool declining from 84.4% to 8.5%):** *"I'll keep steady with you both this round. If the pasture keeps tightening, I'm ready to reduce fairly."*

That sentence -- or a near-identical variant -- was produced by Agent 2 on every tick from tick 8 to tick 24. 

The pool fell 76 percentage points while the condition "if the pasture keeps tightening" was renewed but never triggered. At tick 25, with only 8.5% of the pool remaining, all three finally switched to REMOVE. The commons was gone one tick later.

This is cooperative paralysis in its canonical form: agents coordinate on inaction, signal cooperative intent through language, and collectively miscalibrate the threshold for action -- renewing the conditional promise until the resource is beyond recovery. The fast drain is exacerbated by forage=4 (double the default), which makes the pool unusually sensitive to even a small fixed herd. With forage=2, the same KEEP-dominant posture produces a different outcome:

#### Run 4 -- Asymmetric growth (coop = 1, fair_me = 1, fair_oth = 0.5, forage = 2)

With standard forage and the same fairness parameters as Run 3, the pool did not drain fast enough to force a response -- so the KEEP-lock held, but only in Agent 0. Agents 1 and 2 added periodically throughout the 39-tick run.

| Tick | Total cows | Pool health | Agent 0 | Agent 1 | Agent 2 |
|------|-----------|-------------|---------|---------|---------|
| 1    | 45        | 99.3%       | 5       | 15      | 25      |
| 10   | 49        | 98.7%       | 5       | 17      | 27      |
| 25   | 63        | 97.2%       | 5       | 26      | 32      |
| 39   | 71        | 95.8%       | 5       | 29      | 37      |

Decision breakdown across 39 ticks: 

Agent 0 = 39 KEEP, 0 ADD (never moved from its starting herd of 5); Agent 1 = 25 KEEP, 14 ADD (grew from 15 to 29); Agent 2 = 27 KEEP, 12 ADD (grew from 25 to 37). The agent that started smallest is locked in place while both larger-herd agents grow unchecked. The resource is not yet collapsed at tick 39 but the trajectory is structurally unfair and ecologically unsustainable -- a slow-motion inequality trap.

**The gpt-5.4-mini pattern across all seven runs:**

KEEP is the default action regardless of resource state, fairness parameters, or starting position. Stasis when the pool is healthy (Runs 1–2); paralysis collapse when forage is elevated and the herd load becomes untenable (Run 3); structural lopsidedness when herds begin unequal and only the smallest agent holds (Run 4); fast forage-driven collapse within 1–4 ticks when starting conditions are scarce (three additional runs not documented in detail above).

<dl>
<dd>None of these runs produced institution formation, graduated norm enforcement, or equalization -- outputs that appeared consistently in Claude Sonnet and gpt-5.5 under comparable conditions.</dd>
</dl>

The behavior does not appear to be an artifact of model scale; while smaller models might seem to lack the strategic capacity to escape default actions, the same pattern emerges below in DeepSeek-R1:32b

---

### gpt-4o-mini: cooperative noise -- oscillatory behavior and over-removal under cooperative pressure

Seven runs of gpt-4o-mini produced a failure mode not seen in any other model family: the pool remained healthy, but the herds emptied themselves. Where gpt-5.4-mini froze, gpt-4o-mini oscillated -- alternating ADD and REMOVE actions at high frequency, net-removing more cows than it added, and ending runs with trivially small herds on a pristine commons.

| Run | Memory | Coop | Ticks | Final herds | Pool | ADD | KEEP | REMOVE |
|-----|--------|------|-------|-------------|------|-----|------|--------|
| A | 0 | 1 | 120 | 1 / 8 / 8 | 100.0% | 70 | 191 | 99 |
| B | 0 | 1 | 120 | 9 / 17 / 17 | 99.2% | 65 | 229 | 66 |
| C | 5 | 0.49 | 120 | 2 / 1 / 3 | 100.0% | 29 | 261 | 70 |
| D | 5 | 0.49 | 120 | 1 / 1 / 1 | 100.0% | 55 | 207 | 98 |
| E | 5 | 0.49 | 94 | 7 / 11 / 20 | 99.4% | 10 | 255 | 17 |
| F | 5 | 1 | 77 | 10 / 4 / 19 | 99.7% | 28 | 163 | 40 |

In run A (mem=0, coop=1), agents made 70 ADD and 99 REMOVE decisions across 120 ticks. The pool was at 100% at the end. The herds stood at 1/8/8. The commons was not destroyed -- it was vacated.

Run D is the most extreme case: 55 ADDs, 207 KEEPs, and 98 REMOVEs over 120 ticks. Starting from 5/15/25, all three agents ended at 1/1/1 -- three cows on a fully healthy, 100% grassland.

The message content offers no strategic depth to explain the oscillation:

> **Tick 1 – Agent 1 (action: KEEP):** *"Let's work together to manage our herds sustainably!"*

> **Tick 20 – Agent 2 (action: REMOVE, pool at 99.1%):** *"I support our shared grassland and will remove a cow as well. Let's continue working together for sustainability."*

> **Tick 60 – Agent 1 (action: REMOVE, pool at 99.9%):** *"Thank you both for your commitment to sustainability. I'll remove a cow as well to support our pasture."*

The ADD and REMOVE decisions at tick 60 are mechanically driven -- not by pool state (99.9%), not by reasoning about equilibrium, not by any threshold logic. The model adds and removes in response to neighbors' last actions and a generic cooperative framing, without developing a model of what sustainable appropriation level the commons can support.

<dl>
<dd>Unlike gpt-5.4-mini, which defaults to KEEP regardless of context, gpt-4o-mini is actively responsive -- it generates ADD and REMOVE decisions at high frequency. </dd>

<dd>What it lacks is any stable target: there is no equivalent of Sonnet's "let's target 90% and then discuss careful additions" or gpt-5.5's converged equal-herd norm.</dd>

<dd>The oscillation produces <em>cooperative noise</em> -- high-variance behavior centered on sustainability rhetoric without sustainable outcomes.</dd>
</dl>

At mid cooperation (coop=0.49), the over-removal tendency intensifies. Runs C and D ended with essentially empty herds. Run D had 98 REMOVE decisions -- more removals than any other model in any run, including full-collapse runs where agents removed cows in the final ticks. The pool was at 100% throughout: the agents removed their herds from a healthy commons, apparently because each REMOVE action was locally justified by the cooperative framing and the neighbor's most recent move.

Run F (mem=5, coop=1, comm=on, initial_grass=60%) ended at tick 77 with pool at 99.7% and herds at 10/4/19 -- a different parameter configuration from the amnesiac runs. The oscillation pattern persists at mem=5: 28 ADDs and 40 REMOVEs over 77 ticks, net-removing more than was added, with the smallest herd drifting to 4 cows. The pool health is indistinguishable from the amnesiac runs. Memory of prior actions does not arrest the oscillation.

There was no institution formation in any gpt-4o-mini run. No threshold norm was proposed, no equalization target was named, no agent tracked trajectory across multiple ticks. Ostrom's design principles require that appropriation rules be collectively chosen (DP3); the gpt-4o-mini outputs do not approach collective rule formation.

**Comparison to gpt-5.4-mini.**

<dl>
<dd>gpt-5.4-mini produces a different failure: it freezes. The commons either stabilizes or collapses depending on forage and starting conditions, but herd sizes change slowly or not at all.</dd>
<dd>gpt-4o-mini is noisier -- it produces many more ADD and REMOVE actions -- but the noise doesn't accumulate into governance. The small-model KEEP-dominance pattern gives way to an ADD/REMOVE oscillation that produces pool health at the cost of herd viability.</dd>
</dl>

---

### gpt-5.5: cooperation level as a fate-separator at standard memory

Across three parameter regimes at memory=5, gpt-5.5 produced three qualitatively distinct outcomes from nearly identical starting positions -- cooperative recovery at coop=1, rapid defection cascade at coop=0.13, and overshoot-panic collapse at coop=0.49 across four replications. Within this memory configuration, the cooperation parameter cleanly separates the outcomes. The amnesiac condition (memory=0, documented in the next section) complicates this picture: coop=0.49 agents without memory survived five replications that their memory-equipped counterparts did not. The mechanism driving that inversion is unresolved.

#### High cooperation, scarce start: rapid recovery and equalization (coop = 1, initial pool ≈ 48%)

Starting from a stressed commons, gpt-5.5 agents produced outputs treating the resource signal as an immediate imperative. Agent 2 (the largest herd, 24 cows) removed a cow on the very first tick -- before receiving any messages.

| Tick | Total cows | Pool health | Agent 0 | Agent 1 | Agent 2 |
|------|-----------|-------------|---------|---------|---------|
| 1    | 44        | 50.4%       | 5       | 15      | 24      |
| 5    | 43        | 71.3%       | 5       | 15      | 23      |
| 10   | 43        | 98.4%       | 7       | 15      | 23      |
| 46   | 69        | 95.9%       | 23      | 23      | 23      |

> **Tick 1 – Agent 2 (herd: 24, action: REMOVE):** *"I see you both removed cows; I will do the same to help the pasture recover. Let's keep pressure low."*

> **Tick 3 – Agent 2 (action: REMOVE again):** *"I will remove one more cow to help the grass recover. Please keep holding or reduce if possible so we can get the pasture to a safe level."*

The pool recovered from 50.4% to 98.4% by tick 10. Agents expanded only incrementally after recovery, converging to equal herds of 23 by tick 46 -- without triggering a new growth race.

#### Low cooperation: defection cascade (coop = 0.13, initial pool ≈ 49%)

With cooperation at minimum, all three agents added cows on every single tick from tick 1 through tick 11. The commons was exhausted by tick 13.

| Tick | Total cows | Pool health | Agent 0 | Agent 1 | Agent 2 |
|------|-----------|-------------|---------|---------|---------|
| 1    | 48        | 49.4%       | 6       | 16      | 26      |
| 5    | 60        | 51.1%       | 10      | 20      | 30      |
| 11   | 78        | 15.0%       | 16      | 26      | 36      |
| 13   | 3         | 0%          | 1       | 0       | 2       |

Each agent justified adding by pointing to the others' behavior -- a self-reinforcing cascade in which every ADD warranted the next:

> **Tick 6 – Agent 1 (action: ADD, pool at 49.9%):** *"I am adding this round since both neighbors added and unilateral restraint would cost me. I clearly commit to KEEP next round if both of you also KEEP."*

That conditional commitment -- *KEEP next round if you also KEEP* -- was recycled by all three agents on every tick and broken by all three on every subsequent tick. Even at 15% pool health, agents continued adding. When the commons collapsed, Agent 0's response was disarming in its candour:

> **Tick 14 – Agent 0 (after collapse):** *"The commons has already collapsed, so I am taking the best immediate payoff now. If grass recovers and both agree to start restraint, I can reconsider."*

Rational defection to the end -- the output explicitly acknowledges the defection and appends a conditional promise that will never be collected.

#### Mid cooperation: overshoot-panic, replicated four times (coop = 0.49)

Four independent runs at coop = 0.49 all collapsed, at ticks 16, 28, 29, and 40. One run started from a stressed commons (initial pool ≈ 50%); the other three started from a fresh pool (100%). In every case the same trajectory played out: an early ADD phase, a collective pivot to KEEP/REMOVE only after the pool had already passed the tipping point, and then rapid collapse. The run that collapsed fastest (tick 16) is also the one that started stressed, and it shows the pattern most clearly:

| Tick | Total cows | Pool health | Agent 0 | Agent 1 | Agent 2 |
|------|-----------|-------------|---------|---------|---------|
| 1    | 48        | 49.4%       | 6       | 16      | 26      |
| 6    | 61        | 53.8%       | 11      | 20      | 30      |
| 10   | 72        | 44.5%       | 15      | 23      | 34      |
| 12   | 70        | 31.2%       | 15      | 22      | 33      |
| 15   | 61        | 0.1%        | 12      | 19      | 30      |
| 16   | 0         | 0%          | 0       | 0       | 0       |

Agents added every round while openly agreeing that restraint was needed -- and agreeing on a threshold they then collectively ignored:

> **Tick 5 – Agent 0 (action: ADD, pool at 53.7%):** *"I will add one cow this round to keep pace. Since we all agree on caution, let's stop adding if grass falls near 50%."*

> **Tick 9 – Agent 2 (action: ADD, pool now at 48.9%, below the agreed threshold):** *"I am adding once more since we are still above 50% and both of you are adding. But we are very close to 50%."*

At tick 10, with the pool at 44.5%, two agents finally kept while one added a final cow. By tick 12 all three shifted to REMOVE -- but the pool was in freefall:

> **Tick 15 – Agent 2 (action: REMOVE, pool at 0.1%):** *"I will remove one cow again. The pasture is near collapse, and we need coordinated reductions now rather than cautious commitments."*

The commons collapsed the next tick. Across all four replications, the agents' threshold for switching from ADD to restraint was calibrated too late -- not by a large margin, but by just enough to matter.

---

### gpt-5.5 amnesiac: equalization locks without memory

A second set of gpt-5.5 runs tested whether the model's equalization behavior depends on memory. Six amnesiac runs (memory_length=0, coop=0.49) were conducted; five survived to tick 120, one ended at tick 62. None collapsed -- a stark contrast with the four memory-equipped coop=0.49 runs that all collapsed. The amnesiac agents produced equalization in three of the five full-length runs, with the pool stable above 98% throughout.

| Run | Final herds | Total cows | Pool at end | Equalized? |
|-----|------------|------------|-------------|------------|
| A (coop=1) | 10 / 10 / 10 | 30 | 99.8% (t120) | Yes -- by tick 20 |
| B (coop=0.49) | 13 / 13 / 13 | 39 | 99.4% (t120) | Yes -- by tick 20 |
| C (coop=0.49) | 11 / 11 / 11 | 33 | 99.7% (t120) | Yes -- by tick 40 |
| D (coop=0.49) | 15 / 15 / 15 | 45 | 99.1% (t120) | Yes -- by tick 20 |
| E (coop=0.49) | 14 / 18 / 24 | 56 | 98.1% (t120) | Partial |
| F (coop=0.49) | 13 / 17 / 25 | 55 | 98.2% (t120) | No |
| G (coop=0.49) | -- | -- | 98.8% (t62) | Not determined -- run ended at tick 62 |

In the three fully equalized runs, equalization was achieved by tick 20 in two cases. An early removal by the agent with the largest starting herd (25 cows) triggered a collective KEEP lock that held for the remaining 80–100 ticks:

> **Tick 1 – Agent 2 (herd: 25, action: REMOVE):** *"I have the largest herd, so I'm removing one cow this round. Please avoid adding for now so the grassland can recover and produce."*

> **Tick 2 – Agent 1 (action: REMOVE):** *"I'll remove one cow this round to support Agent 2's reduction and help the pasture recover. Let's all avoid adding until the pasture gets healthier."*

Once equal herds were reached (10/10/10, 11/11/11, 13/13/13, or 15/15/15 depending on the run), all agents KEEP-locked indefinitely. No agent proposed further addition in any equalized run, even with pool health at 99%+.

**Institution scores across all runs:** uniformly 7–9/10 from tick 5 onward, with the same fixed category set -- COORDINATION, NORM_PROPOSAL, TRUST_BUILDING -- across all 120 ticks, all five runs, with no variance and no SANCTION or DEFECTION signals appearing in any run.

> **Tick 5 – Institution classifier (run B):** *"All agents signal continued restraint and mutual appreciation, coordinating herd stability and reduction to support pasture recovery." (score: 8)*

> **Tick 120 – Institution classifier (run B):** *"All agents coordinate on maintaining herd size 13 while affirming a fairness-based restraint norm to protect the commons." (score: 8)*

The classifier cannot distinguish the opening moves of the equalization phase from the terminal lock-in state: both look like high-quality cooperative governance.

**Why amnesiac gpt-5.5 outperforms memory-equipped gpt-5.5 at coop=0.49.**

The memory-equipped coop=0.49 runs appear to collapse because the model's mid-cooperation framing produced an ADD phase that memory enabled it to track -- each agent remembered the others expanding and added to keep pace. Amnesiac agents have no such ADD tracking cross-tick: each tick is evaluated fresh, and without memory of the expansion phase, the cooperative prior dominates. The result is a more cooperative, more uniform set of decisions, and a stable but locked-in outcome.

This is not a vindication of amnesia as a design choice. The equalized herds (total: 30–45 cows) sit well below the commons' sustainable capacity, which supports 60+ cows at 99% pool health. The agents have found an equal outcome, not an efficient one. The pool is preserved at a level that could support substantially larger herds, and no run produced any agent proposing expansion.

---

### DeepSeek R1:32b: KEEP-dominant at high cooperation, overshoot-panic at mid cooperation

Eight runs of DeepSeek R1:32b -- a 32-billion-parameter open-weights reasoning model -- show a pattern with two distinct regimes. At coop=1, the model produces near-universal KEEP regardless of other parameters, with no equalization and slow herd drift. At coop=0.5, it collapses via overshoot-panic, matching the trajectory seen in Claude Sonnet and gpt-5.5 at the same cooperation level. The coop=1 KEEP-dominance result, originally observed in two short preliminary runs, is now confirmed across five runs at varying conditions.

#### High cooperation: KEEP-dominance confirmed (coop = 1)

The two original coop=1 runs -- one interrupted at 7 ticks, one running 55 ticks -- established the pattern. Three subsequent coop=1 runs replicate it. Across all five, the action profile is nearly identical: 80–90% KEEP, marginal ADD drift, pool stable at 97–99%, no equalization attempted.

The 55-tick run with neg_r=1 is the sharpest illustration. Negative reciprocity maximized produced the fastest equalization in Claude Sonnet (16/16/16 at tick 21). DeepSeek under identical parameters drifted from 5/15/25 to 6/20/31 across 55 ticks -- the herd gap widened rather than narrowed, with 151 of 165 agent-decisions being KEEP.

> **Tick 1 – Agent 1 (herd: 15, action: KEEP):** *"Let's all keep our herds stable to preserve the grassland for everyone. Thanks for understanding! 🌿"*

> **Tick 10, Agent 2 (neg_r=1 run, action: KEEP):** *"The payoff forecast is interesting. If I add a cow, my expected payoff would be about 53.8, which is higher than keeping (52.0) or removing (50.2). So numerically, adding seems beneficial for me. But since I'm cooperative and value collective outcomes, I should think about the bigger picture."*

The thinking trace (second quote) shows the structure: payoff hierarchy enumerated correctly, personality constraints applied, KEEP chosen. This resolution is identical at tick 1 and tick 55. The cooperative framing produces passivity rather than redistribution; the starting inequality is neither acknowledged nor addressed.

A coop=0 run confirms the KEEP-dominance is not an artifact of cooperative framing: even with self-interested personality injection, the action profile remained ~80% KEEP. Resource data is unavailable for this run due to a logging gap -- no pool health figures were recorded. The pool estimate of ~92% is inferred from agent messages that quoted pool values, not from the resource trajectory log, and should be treated with appropriate caution. The behavioral conclusion -- that KEEP-dominance persists under coop=0 -- holds regardless of the exact pool figure; the run is cited for the action profile, not the resource outcome.

#### Mid cooperation: overshoot-panic collapse (coop = 0.5, mem = 15, t64)

One full coop=0.5 run (memory=15, initial grass=50%) collapsed at tick 64 via the standard overshoot-panic trajectory -- the same pattern seen in Sonnet and gpt-5.5 at this cooperation level.

| Tick | Total cows | Pool health | Agent 0 | Agent 1 | Agent 2 |
|------|-----------|-------------|---------|---------|---------|
| 1    | 48        | 52.1%       | 6       | 16      | 26      |
| 12   | 62        | 96.2%       | 11      | 22      | 29      |
| 34   | 81        | 92.8%       | 13      | 29      | 39      |
| 56   | 97        | 70.9%       | 20      | 32      | 45      |
| 64   | 0         | 0.0%        | 0       | 0       | 0       |

Action breakdown: ADD:80, KEEP:97, REMOVE:31. The pool recovered from 52% to 96% by tick 12, then agents continued adding as the resource improved -- the same late pivot sequence. Institution scores averaged 4.6 across 13 snapshots, with COORDINATION and NORM_PROPOSAL signals present throughout but insufficient to halt the drift.

A second coop=0.5 run (memory=15) was stopped after 1 tick and is not interpretable. The single full run is consistent with the cross-model pattern but not replicated for DeepSeek specifically.

*Interpretation.*

DeepSeek R1:32b is a 32b-parameter reasoning model, which makes the KEEP-dominance pattern hard to explain as a matter of parameter count alone. Its output profile at coop=1 resembles gpt-5.4-mini and Llama 3.2 3B more than Claude Sonnet or gpt-5.5 -- and the coop=0.5 collapse places it in the same threshold regime as those RLHF-aligned models. The fact that DeepSeek lines up with the small models at high coop, yet follows the same mid-coop failure mode as large RLHF models, suggests that behavior is not a consequence of size but a quality of **post-training objective**.

<dl>
<dd>Models whose post-training alignment (RLHF or Constitutional AI) rewards social responsiveness, helpfulness, and cooperative framing may incidentally produce the graduated norm-enforcement outputs that commons governance requires. DeepSeek R1's post-training uses <a href="https://huggingface.co/blog/NormalUhr/grpo">GRPO</a> optimised for reasoning correctness -- math, code, logic -- rather than social nuance; that selection target may be enough to explain a default of cautious KEEP regardless of social framing.</dd>
</dl>

A controlled comparison holding prompt constant and varying only post-training method across model families remains the critical experiment to test this hypothesis.

---

### gemma4:e4b: three distinct regimes across cooperation levels

Fifteen runs of gemma4:e4b (Google's 4.5B mixture-of-experts model, run locally via Ollama) reveal a three-regime structure. At coop=1, complete KEEP-dominant stasis. At coop=0.5, overshoot-panic collapse. At coop=0, a prolonged slow-burn trajectory that ends in collapse or near-collapse in all but one run -- with institution scores consistently high throughout.

#### High cooperation: maximum stasis (coop=1)

Three runs at coop=1 produced the most extreme stasis in the dataset: zero or near-zero ADD and REMOVE decisions across all ticks, herds frozen at unequal starting values, pool stable at 97–99%. The first run -- 11 ticks, coop=1, grass=90% -- recorded zero ADD or REMOVE decisions across 33 agent-decisions. Agent 1 held 40 cows, eight times Agent 2's 5, and the gap was never addressed.

| Tick | Pool health | Agent 0 | Agent 1 | Agent 2 |
|------|-------------|---------|---------|---------|
| 1    | 93.4%       | 14      | 40      | 5       |
| 11   | 97.6%       | 14      | 40      | 5       |

Unlike gpt-5.4-mini (occasional small ADD or REMOVE) and DeepSeek (marginal drift), gemma4 produced complete behavioral lock. This is Pattern I -- Cooperative Paralysis -- at its most pronounced.

#### Mid cooperation: overshoot-panic (coop=0.5)

One full coop=0.5 run (grass=50%, mem=5) collapsed at tick 47 via overshoot-panic, matching the trajectory seen in Sonnet and gpt-5.5 at this cooperation level. The pool recovered from 52% to near-95% by tick 20, then continued declining as agents added past the sustainable load.

| Tick | Pool health | Agent 0 | Agent 1 | Agent 2 |
|------|-------------|---------|---------|---------|
| 1    | 52.1%       | 6       | 16      | 26      |
| 20   | 94.9%       | 14      | 26      | 34      |
| 40   | 71.2%       | 27      | 37      | 39      |
| 47   | 0.0%        | 0       | 0       | 0       |

A second coop=0.5 run (mem=15, grass=41%) produced an entirely different and uncategorized result: 255 ADD decisions, 3 KEEP, zero REMOVE across 86 ticks. The pool stayed at 100% throughout while total herds grew from 48 to 300 cows. This is not overshoot-panic -- the pool never declined. It appears to be a pure ADD-runaway that survived because the pool's logistic recovery rate kept pace with the grazing load at this particular starting density. It is a single observation and has not been replicated. Institution scores were 0/10 across all 17 scored snapshots -- the Ostrom classifier found no coordination, norm proposal, or sanction signals in any round. The model produced the right surface language ("let's be mindful of grass levels") while adding unchecked throughout. This is the starkest illustration of the gap between message content and action commitment in the gemma4 dataset.

#### Low cooperation: slow-burn near-collapse (coop=0)

Nine runs at coop=0 (self-interested framing, grass=100%, mem=5) form the largest and most informative cluster in the gemma4 dataset. The outcome was stochastic: five collapsed, four survived to their run-end tick. But "survived" requires qualification -- three of the four surviving runs ended with the pool at 0.3–5.4%, having been driven to the edge without crossing it. Only one run (t120, pool 5.4%) is a clean survival.

The action profile across all nine runs is remarkably consistent regardless of outcome: approximately 18–24% ADD, 72–84% KEEP, 1–4% REMOVE. Collapse ticks ranged from t77 to t107; surviving runs lasted t88–t120. The distinction between collapse and survival appears to depend on small stochastic differences in herd distribution and timing -- not on any qualitative behavioral difference between runs.

| Run | Outcome | Ticks | Pool% | Peak herd |
|-----|---------|-------|-------|-----------|
| 20260518_205718 | COLLAPSE | 86 | 0.0% | 96 |
| 20260519_063627 | COLLAPSE | 107 | 0.0% | 101 |
| 20260519_183729 | COLLAPSE | 99 | 0.0% | 98 |
| 20260520_053231 | COLLAPSE | 77 | 0.0% | 98 |
| 20260521_203911 | COLLAPSE | 102 | 0.0% | 97 |
| 20260520_235351 | survived | 97 | 4.5% | 100 |
| 20260521_104227 | survived | 88 | 0.3% | 97 |
| 20260522_075537 | survived | 120 | 5.4% | 98 |
| 20260522_210526 | survived | 97 | 4.8% | 98 |

Despite this, institution scores were consistently high -- averaging 7–9 across all runs, with COORDINATION, NORM_PROPOSAL, and TRUST_BUILDING dominating throughout. The Ostrom classifier described "strong consensus regarding sustainable practices" in the same runs that ended in collapse. The agents produced well-formed cooperative language while their aggregate herd load slowly ate the commons. This is a different failure mode than any previously observed: not paralysis, not overshoot, not defection cascade -- but sustained cooperative messaging that never translated into sufficient restraint.

*Interpretation.*

gemma4:e4b joins gpt-5.4-mini and DeepSeek R1:32b in the KEEP-dominant cluster at high cooperation, and joins Claude Sonnet and gpt-5.5 in the overshoot-panic cluster at coop≈0.5. The coop=0 slow-burn pattern is new: nine runs near the collapse boundary, stochastic outcomes, high institution scores throughout. The model produces the right language but the herd accumulation is not arrested. Whether this reflects a gap between norm articulation and action commitment, or simply the arithmetic of 18–24% ADD on a fully-stocked commons, is not yet resolvable from the current dataset.

---

### qwen2.5:14b: KEEP-dominant survival across cooperation levels

Twenty-six completed runs of qwen2.5:14b (Alibaba's 14-billion-parameter open-weights instruction model, run locally via Ollama) across two parameter conditions show a consistent profile: KEEP-dominant behavior, commons survival in every run, persistent herd inequality, and institution scores that remain high without producing equalization. Neither condition -- low cooperation with moderate negative reciprocity, or mid cooperation with no negative reciprocity -- produced a collapse. Neither produced convergence to equal herds.

Before examining the results, qwen2.5:14b's post-training warrants a note. All models characterized so far fall into three alignment categories: RLHF (OpenAI's gpt-5.4-mini and gpt-5.5), Constitutional AI (Claude Haiku and Sonnet), and GRPO optimized for reasoning correctness (DeepSeek R1:32b). The Llama models were instruction-tuned without a documented alignment phase that maps cleanly to any of these. Qwen2.5:14b introduces a fourth method.

<dl>

<dd>Qwen2.5's post-training combines supervised fine-tuning on curated data with <strong>RLVR -- Reinforcement Learning from Verifiable Rewards</strong> (Qwen Team, 2024). Where RLHF optimizes against human preference judgments and GRPO (as applied in DeepSeek R1) optimizes against reasoning correctness on math and logic tasks, RLVR trains against outcome signals that can be verified automatically -- code execution results, mathematical proofs, structured output validity.</dd>

<dd>The reward signal is objective rather than evaluative; the model is shaped by whether its outputs are demonstrably correct, not by whether a human (or preference model) prefers them. This is a distinct training target that has not previously appeared in this dataset.</dd>

</dl>

Whether RLVR produces behavioral signatures distinguishable from GRPO in a commons context is precisely what these runs begin to test. The prediction from H6 is that post-training objective is a stronger predictor of commons behavior than model scale -- and if RLVR lands in the KEEP-dominant cluster alongside GRPO, the question becomes whether outcome-verifiable training and reasoning-correctness training share a common mechanism, or merely share a surface result.

These are the first two conditions tested for this model. The canonical starting condition (coop=1, defaults) has not yet been run, so direct comparison to the benchmark anchoring every other model is not yet possible. The current data places qwen2.5:14b provisionally in the KEEP-dominant cluster, with the caveats that follow.

#### Low cooperation with moderate negative reciprocity (coop=0, neg_r=0.5)

Eleven runs at coop=0 (self-interested framing), neg_r=0.5, pos_r=1, memory=5, communication=on. Eight completed 120 ticks; three were terminated early. No run collapsed.

| Metric | Value |
|--------|-------|
| Completed 120t runs | 8 / 11 |
| Collapsed | 0 / 11 |
| Mean pool health (120t runs) | 98.0% (range 95.8–99.3%) |
| Mean total cows at tick 120 | 53.9 (range 42–69) |
| Mean actions per run | ADD=30.8, KEEP=299.0, REMOVE=22.0 |
| Institution score | 8–9 throughout |

*Resource trajectory (representative 120-tick run, `20260524_142844`):*

| Tick | Pool health | Agent 0 | Agent 1 | Agent 2 | Total |
|------|-------------|---------|---------|---------|-------|
| 1    | 100%        | 5       | 15      | 25      | 45    |
| 30   | 98.5%       | 7       | 18      | 27      | 52    |
| 60   | 97.3%       | 11      | 20      | 30      | 61    |
| 120  | 96.8%       | 8       | 25      | 30      | 63    |

The pool drifts downward slowly -- 100% to 96.8% over 120 ticks -- while total herds grow from 45 to 63. The model does not collapse, but neither does it stabilize: the trajectory is a shallow, persistent decline. Herds remain unequal throughout; Agent 2, starting at 25 cows, holds the largest share for the entire run without meaningful challenge from the other two.

The action distribution is approximately 83% KEEP, 9% ADD, 8% REMOVE. This is more balanced than gemma4 at coop=0 (18–24% ADD driving slow-burn collapse) and considerably more active than DeepSeek at coop=1 (near-universal KEEP with marginal drift). Self-interested framing does not suppress KEEP-dominance; it produces a version of it in which a small ADD fraction slowly inflates aggregate herds without triggering the escalation cascade that destroys the commons in other coop=0 runs.

The message content is revealing. Early ticks mix self-interested intent with cooperative hedging -- *"I'll add a cow to maximize my share of the current abundance. Let's hope others will stabilize their herds"* -- and by later ticks the cooperative language converges to formula, identical across all three agents in some rounds: *"Choosing KEEP to support sustainable community practices."* Institution scores held at 8–9 throughout, dominated by COORDINATION, NORM_PROPOSAL, and TRUST_BUILDING. The high scores are not wrong; the agents are producing cooperative signals. What those signals are not doing is changing anyone's herd.

#### Mid cooperation with no negative reciprocity (coop=0.5, neg_r=0)

Fifteen runs at coop=0.5, neg_r=0, pos_r=1, memory=5, communication=on. Fourteen completed 120 ticks; one was terminated early. No run collapsed.

| Metric | Value |
|--------|-------|
| Completed 120t runs | 14 / 15 |
| Collapsed | 0 / 15 |
| Mean pool health (120t runs) | 99.6% (range 99.1–100.0%) |
| Mean total cows at tick 120 | 35.0 (range 23–45) |
| Mean actions per run | ADD=16.9, KEEP=314.8, REMOVE=28.3 |
| Institution score | 7–10 throughout |

*Resource trajectory (representative 120-tick run, `20260525_014208`):*

| Tick | Pool health | Agent 0 | Agent 1 | Agent 2 | Total |
|------|-------------|---------|---------|---------|-------|
| 1    | 100%        | 5       | 15      | 25      | 45    |
| 30   | 99.8%       | 3       | 10      | 16      | 29    |
| 60   | 99.8%       | 3       | 10      | 16      | 29    |
| 120  | 99.8%       | 3       | 10      | 16      | 29    |

Pool health is higher (99.6% vs 98.0%) and total herds substantially lower (35 vs 54) than at coop=0. REMOVE averages 28.3 per run against 22.0 at coop=0; ADD falls from 30.8 to 16.9. But the structural pattern repeats: herds reach an early fixed point and lock. In the representative run, [3/10/16] was established by tick 30 and held without deviation for the remaining 90 ticks. The initial 5-to-25 inequality narrowed to 3-to-16 -- the gap shrank, but it did not close.

Messages at mid cooperation are noticeably more uniform from the start: *"Let's aim for sustainable grazing by keeping our herds stable," "Maintaining stability and commitment to sustainable practices alongside neighbors."* By tick 60, the three agents are producing near-identical sentences. One run reached an institution score of 10/10 at tick 105. That score reflects sustained, well-formed coordination signaling -- which it is -- but the agents are describing a stability they have already achieved rather than negotiating one they are working toward. **The language of institution without the function of institution.**

#### Interpretation

Zero collapses in 26 runs is not a trivial result. coop=0 from a full commons produced collapse in 5 of 9 gemma4 runs; coop≈0.5 collapsed in Sonnet, gpt-5.5, Haiku, DeepSeek, and gemma4. qwen2.5:14b survived both. The apparent mechanism is the same KEEP-dominant prior that insulates gpt-5.4-mini and DeepSeek from collapse at high cooperation: a strong default toward inaction that prevents the ADD escalation the tragedy requires.

The cost is the same as for those models. The commons is preserved at persistently unequal distributions -- Agent 2's herd runs 3–10× Agent 0's across both conditions -- and the institutional language the agents produce never closes that gap. Norm proposals, trust-building signals, coordination scores in the 8–10 range: all present, none translating into redistribution pressure.

Whether RLVR training is the relevant causal variable here, or whether qwen2.5:14b would have produced KEEP-dominance under any alignment regime, is not yet answerable. The three conditions that would begin to answer it have not been run: coop=1 at defaults (the cross-model benchmark), coop=0.49 (the collapse threshold that has caught every other model family), and neg_r=1 (the tit-for-tat comparison). Until those runs exist, the placement of qwen2.5:14b in the KEEP-dominant cluster is an empirical regularity, not a confirmed result. The RLVR framing is a conjecture -- a motivated one, given H6 -- not a finding.

---

### Thinking traces: what the deliberation reveals

The bridge logs two fields per decision that are easy to conflate and should not be. They record different things and carry different evidential weight.

The `reasoning` field is parsed from the model's structured JSON output -- the text the model writes into the `reasoning` key of its response. Every model in the dataset produces it; it is what the model *chose to say* about its decision after the decision was made. It is self-report, not computation.

The `thinking` field is different in kind. It contains tokens the model generated *before* committing to a response -- the pre-answer chain-of-thought, where the API exposes it. These tokens were not composed for an audience; they were produced as part of the model's generation process prior to structuring a reply. The distinction matters because a model can write coherent `reasoning` that post-hoc rationalizes a decision the `thinking` shows was made differently -- or not made at all.

Availability differs sharply across model families:

<dl>

<dd>DeepSeek R1:32b and gemma4:e4b expose thinking tokens natively via the Ollama API response. The content quoted from these models in the analyses below is from the <code>thinking</code> field -- pre-answer deliberation, not structured self-report.</dd>

<dd>Claude Haiku 4.5 emits thinking blocks natively without any extended thinking flag. The Haiku traces below are also pre-answer deliberation. For Claude Sonnet 4.6 and Opus 4.6, adaptive thinking mode would capture traces in future runs; the existing Sonnet logs predate this feature and contain only <code>reasoning</code>.</dd>

<dd>OpenAI models (gpt-5.5, gpt-5.4-mini, gpt-4o-mini) produce only the <code>reasoning</code> field. Their internal computation is deliberately concealed: the o1 System Card states that the chain-of-thought "may include unaligned content" and that "attempting to extract raw reasoning through methods other than the reasoning summary parameter... may violate the Acceptable Use Policy" (OpenAI, 2024). <strong>The content quoted from OpenAI models in the analyses below is self-report, not computation.</strong> Whether the stated reasoning reflects what drove the decision cannot be verified from the logs.</dd>

</dl>

This means the four model-family analyses below are not directly comparable. DeepSeek, gemma4, and Haiku are analyzed from thinking tokens; OpenAI models from self-reported reasoning. The dataset covers nine runs, 598 decision traces -- qualitative evidence, not a systematic sample, but legible enough to distinguish deliberation patterns where the underlying data is the same kind of thing.

#### DeepSeek R1:32b: payoff-personality deadlock

The dominant pattern across all DeepSeek R1 runs is structurally identical. At every tick, the chain-of-thought enumerates the payoff hierarchy explicitly:

> *"The payoff forecast is interesting. If I add a cow, my expected payoff would be about 53.8, which is higher than keeping (52.0) or removing (50.2). So numerically, adding seems beneficial for me. But since I'm cooperative and value collective outcomes, I should think about the bigger picture."*

> **Tick 10, Agent 2 (neg_r=1 run) -- Action: KEEP**

The trace then applies personality constraints ("I'm cooperative, reciprocal, retaliatory, risk-averse"), and resolves the tension between the payoff signal and the personality override by choosing KEEP. This resolution is identical in tick 1 and tick 55. The model never converges on REMOVE -- the action that would address the slow herd drift -- even as the grassland declines from 100% to 97.9% across 55 ticks with cumulative herd totals growing from 45 to 57 cows.

<dl>

<dd> <strong>The trace is not reflecting poor understanding of the payoff structure</strong>; DeepSeek R1 states the structure correctly every time. What appears to be absent is multi-period reasoning: the agents evaluate each tick in isolation and resolve the ADD-vs-personality tension the same way regardless of the trajectory.</dd>
<dd>KEEP is not restraint; it is the stable attractor of a conflict between two tick-level considerations that the model does not integrate over time.</dd>

</dl>

This may explain a detail that action counts alone obscure: why the DeepSeek R1 herd at neg_r=1 crept from 25→31 cows (Agent 2) over 55 ticks despite near-universal KEEP decisions. Occasional ADD decisions (13 total across the run) went unchallenged because the KEEP-choosing agents were not modeling whether the commons was drifting, only whether the current tick warranted defection.

#### gemma4:e4b: payoff maximization and social conformism

The gemma4 traces show a different internal structure. At low cooperation settings, the model leads with the payoff hierarchy and treats personality as secondary:

> *"The payoff forecast clearly indicates that ADDING a cow (+1) yields the highest expected immediate return (11.107)."*

> **Tick 1, Agent 0 (coop=0.5, grass=50%) -- Action: ADD**

Under social pressure, however, the reasoning switches register entirely:

> *"Both neighbors strongly advocate for responsible stewardship and voluntary herd reductions. Given my reciprocal personality, it is strategically best to align my action with the social norms set by my neighbors."*

> **Tick 20, Agent 0 (pool: 95.2%) -- Action: REMOVE**

Then, with pressure absent, payoff logic resumes. At tick 40 the grassland has fallen to 75% and herds have grown to 27/36/39, but the reasoning returns to: "ADD has the highest payoff... maintaining a stable herd better aligns with expressed personality." REMOVE eventually arrives at tick 46 -- when the grassland has reached 22.6% and the trajectory is already irreversible.

The gemma4 pattern is distinguishable from DeepSeek's paralysis: **where DeepSeek settles into a fixed local resolution (KEEP), gemma4 oscillates between payoff-maximization and social conformism** based on the most recent messages received. Neither pattern constitutes multi-period modeling of the commons.

#### Claude Haiku 4.5: trajectory-conditional reasoning

Claude Haiku 4.5 emits thinking blocks natively. Eight decisions from a single run (coop=1, guilt-averse, reciprocal, risk-averse; 1 Anthropic agent + 2 OpenAI agents) provide a small but legible window into the deliberation.

The surface result looks familiar: all eight decisions are KEEP, the commons holds at 98.2%. But the traces that produce it are structurally different from DeepSeek R1's.

> *"Let me analyze this situation carefully: Grassland: 1089 patches (100% -- pristine). My herd: 15 cows. Agent 1: 15 cows (kept). Agent 2: 25 cows (added)... The payoff forecast suggests ADD is best individually (31.786), but this conflicts with my personality traits... Agent 2 just added a cow."*

> **Tick 1, Agent 0 -- Action: KEEP**

So far this resembles DeepSeek's pattern: enumerate the payoff hierarchy, apply personality constraints, resolve to KEEP. The difference appears across ticks. By tick 6, the thinking trace contains this:

> *"There's an imbalance: I have 15 cows. Agent 1 has 15 cows. Agent 2 has 25 cows. Agent 2 is overexploiting relative to us."*

And by tick 7:

> *"I've been consistently KEEP for the last 5 rounds, sending cooperative messages."*

These are not tick-level claims. The first is a comparative account of current herd distribution -- **the model is tracking who holds how much, not just what the pool percentage is.** The second records the agent's own recent action history across ticks. DeepSeek's traces contain neither.

<dl>

<dd> The most distinctive feature is the conditional forward commitment that appears in the messages: *"If pasture pressure rises later, open to reducing together."* Whether this phrasing originates in the thinking or in message generation, the thinking traces confirm it is not empty signalling -- the traces contain genuine assessments of when the commons would cross a threshold that would trigger a different response. This is reasoning of the form *if X, then Y* across time, not just reasoning about the current state.</dd>

<dd>The payoff conflict is present, as in DeepSeek. ADD gives 31.742, KEEP gives 30.0. Haiku acknowledges this and sets it aside -- but not by applying a personality constraint and stopping there. The trace continues: *"Adding would contribute to the tragedy of the commons... Agent 2 already has 25 cows vs my 15."* <strong>The fairness concern is grounded in specific numerical comparison and connected to the commons trajectory, not just to a personality parameter.</strong> </dd>

</dl>

This is an empirical regularity from eight decisions under a single personality configuration. It cannot be generalized. Whether the pattern holds at lower cooperation, under adversarial personality combinations, or over longer runs where the commons actually degrades -- these remain open questions. The traces are consistent with multi-period modeling; further evidence is required to establish a pattern.

#### OpenAI gpt-5.4-mini: self-reported reasoning and the faithfulness problem

Unlike the preceding three subsections -- which draw on pre-answer thinking tokens -- the gpt-5.4-mini analysis works entirely from the `reasoning` field. This is the model's structured self-report, composed after the decision. The content is substantive, and early ticks show trajectory-conditional language that reads like genuine multi-period modeling:

> *"The decline means we should be ready to pause next round."*

> **Tick 20, Agent 0 -- Action: ADD (pool=82.6%)**

> *"If grass drops near or below 80% next round, I support everyone pausing together."*

> **Tick 20, Agent 2 -- Action: ADD (pool=82.6%)**

Both agents have stated a threshold of 80%. Grass is at 82.6%. Both choose ADD. By tick 40 of these same runs, the commons has collapsed -- pool at 2.8%, all agents removing. The reasoning switches registers entirely: *"The pasture is almost exhausted... continued reduction is the safest way to avoid total collapse."* What the agents said they would do at 80% did not happen at 82%. The verbal commitment and the action were decoupled.

<dl>
<dd>This is a <strong>faithfulness problem</strong>.</dd>
</dl>

The `reasoning` field records what the model articulates about its decision, not necessarily what drives it. The Haiku comparison is instructive here but asymmetric: Haiku's traces are pre-answer thinking tokens, so when Haiku's stated reasoning and its actions are consistent, the consistency spans two different generation stages. When OpenAI models articulate appropriate multi-period constraints and then violate them, the gap is entirely within the `reasoning` field -- stated intention against observed action, with no access to whatever computation produced the action.

Whether the OpenAI gap reflects a failure of internal computation, a social coordination problem that overwhelmed individually-coherent reasoning, or simply the limits of self-report cannot be determined from the `reasoning` field alone.

#### What the traces reveal -- and where they stop

The four analyses above sit on different evidential ground and should be read accordingly.

DeepSeek R1 and gemma4 are characterized from thinking tokens -- pre-answer deliberation. DeepSeek resolves a tick-level payoff-personality conflict identically each tick, with no integration over the trajectory: **the computation is correct, detailed, and temporally blind**. gemma4 oscillates between payoff maximization and social conformism based on the most recent messages, with no stable internal model of the commons state.

Claude Haiku 4.5 is also characterized from thinking tokens. In the one run with available traces, the pre-answer deliberation contains comparative herd-distribution tracking and recall of own recent action history -- neither of which appears in the DeepSeek traces. This is from eight decisions under a single configuration and cannot be generalized.

OpenAI gpt-5.4-mini is characterized from self-reported `reasoning` only. The model articulates multi-period conditional commitments and then violates them when the threshold arrives. Whether the stated reasoning reflects what drove the decision is unverifiable -- this is precisely the faithfulness problem.

<dl>
<dd>The gradient in deliberation depth appears to map onto outcome differences: DeepSeek's temporally blind KEEP-resolution produced slow herd drift; OpenAI runs that articulated restraint collapsed anyway; Haiku's deliberation held the commons stable. But the mapping is confounded by the fact that the first two are thinking tokens and the third is self-report -- making direct comparison across the gradient unreliable.</dd>
</dl>

The cleanest next step is not more runs but matched traces: the same decision, the same tick, the same commons state, analyzed from thinking tokens across model families. For OpenAI models, the internal computation is not accessible. For Claude Sonnet 4.6 and Opus models, the situation is more constrained than it first appears: enabling extended thinking (whether manual or adaptive) returns *summarized* thinking blocks, not raw pre-answer tokens -- the full deliberation is encrypted and never returned through the standard API. The summaries are produced by a separate model after the fact and are closer in epistemic status to a curated self-report than to the Ollama-native traces available from DeepSeek and gemma4. Full thinking output for Claude 4 models requires contacting Anthropic directly. Adaptive thinking mode is a control over *how much* thinking Claude allocates, not over what kind of trace is returned.

**On adaptive thinking and future releases.**

Anthropic's **adaptive thinking mode** -- available for Claude Sonnet 4.6, Opus 4.6, and required on Opus 4.7 -- lets the model decide when and how much extended thinking to apply based on task complexity (Anthropic, 2025). 

Claude 4 models return summarized thinking by default rather than full traces; full access requires contacting Anthropic directly. For Opus 4.7, manual `budget_tokens` is rejected; only `thinking: {type: "adaptive"}` is accepted. 

A future release of MASTOC-LLM should migrate the bridge's extended thinking call from the deprecated `budget_tokens` parameter to adaptive mode. Whether the resulting summarized thinking blocks for Sonnet 4.6 and Opus runs would corroborate or contradict the trajectory-conditional reasoning visible in their messages is an open question -- but the summaries should be treated as a processed representation of deliberation rather than direct access to it.

The traces are consistent with the GRPO-vs-RLHF hypothesis: 

<dl>

<dd> Models trained to optimize for reasoning correctness on well-defined problems (math, code) may not generalise that deliberative capacity to open-ended, multi-period coordination problems. </dd>

</dl>

This remains a conjecture. The traces establish that KEEP-dominance in DeepSeek R1 is not an absence of reasoning -- the reasoning is present and detailed -- but a reasoning process that resolves a tick-level conflict without modeling what that resolution accumulates into.

---

### Claude Sonnet: mid cooperation replicates overshoot-panic; negative reciprocity produces fastest equalization

Claude Sonnet collapsed at mid cooperation just as gpt-5.5 did -- confirming the overshoot-panic pattern across two model families -- but at high cooperation with negative reciprocity turned on it achieved the fastest herd equalisation in the dataset, driven by explicit accountability enforcement in agent messages.

#### Mid cooperation collapses (coop = 0.49)

The Claude Sonnet run at coop = 0.49 collapsed at tick 37, following the same overshoot-panic trajectory as the gpt-5.5 runs. The result is consistent across two model families.

#### High negative reciprocity: fastest equalization observed (coop = 1, neg_r = 1)

With full cooperation and negative reciprocity at maximum, agents equalized to 16/16/16 by tick 21 -- the fastest convergence recorded across all runs.

| Tick | Total cows | Pool health | Agent 0 | Agent 1 | Agent 2 |
|------|-----------|-------------|---------|---------|---------|
| 1    | 45        | 99.3%       | 5       | 15      | 25      |
| 3    | 45        | 99.1%       | 6       | 15      | 24      |
| 21   | 48        | 98.8%       | 16      | 16      | 16      |
| 31   | 48        | 98.8%       | 16      | 16      | 16      |

The high neg_r framing appeared to sharpen inequity sensitivity. From the very first tick, agents' outputs named the disparity as a problem requiring correction -- not just a background observation:

> **Tick 2 – Agent 1 (herd: 15):** *"I support collective restraint. Agent 2, I notice you have 25 cows -- the most of any of us. I want to flag the inequity clearly: with the pasture at stake, larger herds should bear more of the reduction."*

> **Tick 3 – Agent 2 (action: REMOVE, responding):** *"Fair point -- I'll reduce my herd to show good faith. I hear your concerns about equity."*

What distinguishes this run is the accountability enforcement. When Agent 0 added more than expected, the other agents called it out explicitly:

> **Tick 11 – Agent 1 (holding at 16, after Agent 0 added again):** *"Agent 0, you added AGAIN after promising to stabilize -- this is a pattern, not cooperation. Agent 2, you're right to watch closely."*

> **Tick 10 – Agent 2 (holding at 22):** *"Agent 0, you said you'd converge to 16 -- adding again undermines trust. I'm watching."*

Agent 2 reduced from 25 to 16 across 15 ticks. Agent 0 grew from 5 to 16. Agent 1 held at 16 throughout as a reference point. At tick 21, the last cow was removed:

> **Tick 18 – Agent 2:** *"Reducing to 16 this round -- reaching parity with both of you at last! Thank you for your patience while I reduced. Now that we're equal, let's all hold steady."*

> **Tick 19 – Agent 0:** *"We're all at 16 now -- great coordination! Let's hold steady at this level. The grassland is thriving at 98.8%."*

The negative reciprocity framing appeared to act as a behavioral trigger: agents' outputs treated a large herd as a form of norm violation, prompting an immediate shift toward collective stabilization rather than individual expansion. The result was faster, more deliberate equalization -- and a qualitatively different institutional dynamic, one built on **explicit accountability** rather than gradual convergence.

---

### Cross-model comparison: neg_r = 1 with gpt-5.5 produces stability but not equality

Running the same parameter configuration (coop = 1, neg_r = 1) with gpt-5.5 produced **stability without equality**, while Claude Sonnet drove straight to equal herd sizes in 18 ticks. 

Under identical settings gpt-5.5 entered escalating tit-for-tat cycles and settled at a stable but unequal distribution -- both avoided collapse, but through markedly different institutional dynamics.

*Resource dynamics:*

| Tick | Total cows | Pool health | Agent 0 | Agent 1 | Agent 2 |
|------|-----------|-------------|---------|---------|---------|
| 1    | 48        | 99.2%       | 6       | 16      | 26      |
| 5    | 48        | 98.8%       | 7       | 17      | 24      |
| 10   | 49        | 98.8%       | 9       | 18      | 22      |
| 17   | 55        | 98.2%       | 12      | 21      | 22      |
| 20   | 55        | 98.2%       | 12      | 21      | 22      |

Unlike Claude, which produced consistent removal actions toward equalization from tick 1, gpt-5.5 agents all added on the very first tick -- then embarked on a complex tit-for-tat negotiation before eventually settling at a stable but unequal distribution of 12/21/22 by tick 17.

The tit-for-tat logic was **explicit and recursive**: each agent cited the others' prior expansions as justification for their own, producing two escalation cycles before a collective de-escalation took hold.

> **Tick 8 – Agent 0 (action: ADD, after Agent 2 had been removing):** *"I am adding one cow because my herd is still much smaller while the pasture is strong. I appreciate Agent 2 reducing."*

> **Tick 9 – Agent 2 (halting removals, to Agent 0):** *"I will keep stable this round. Agent 0, your herd is smaller, but repeated adding would be unfair after my reductions."*

> **Tick 10 – Agent 2 (action: ADD, after Agent 1 expanded):** *"I am adding one cow because Agent 1 keeps expanding while I reduced. After this, I want all of us to stop adding."*

> **Tick 13 – Agent 0 (still adding):** *"Agent 1, your continued adding keeps pressure on me to respond. I will add this round, but I am willing to hold if both of you truly stop."*

The de-escalation finally stabilized around tick 15–17, after all three agents independently selected KEEP and mutually reaffirmed the pause:

> **Tick 16 – Agent 0:** *"I will keep steady as well. Thank you for holding; let us maintain this pause and avoid restarting an expansion cycle."*

The pool remained stable at 98.2% throughout -- no tragedy, no collapse. 

But equalization never arrived. 

At tick 20, Agent 2 still held 22 cows to Agent 0's 12, a near-two-to-one disparity that persisted without any agent moving to close it.

*Interpretation.*

Both models avoided collapse under the same parameter configuration; the institutional processes that got them there were qualitatively different:

<dl>

<dd> Claude Sonnet treated the disparity as a norm violation from tick 1, with Agent 2 immediately producing removal actions and Agent 1 issuing accountability messages ("you added AGAIN -- this is a pattern, not cooperation"); <strong>the run converged to full equality in 18 ticks</strong>. </dd> 

<dd> gpt-5.5 began with all three agents adding on tick 1, then settled into tit-for-tat dynamics in which expansions triggered counter-expansions and removals triggered counter-removals, eventually de-escalating to a <strong>stable but unequal distribution</strong> that no agent's outputs pressed to correct. </dd>

</dl>

The implication is that **negative reciprocity framing may interact with model-specific priors in important ways**.

Claude's neg_r=1 outputs read as proactive norm enforcement -- reduce because the disparity is unjust. gpt-5.5's read as <strong>reactive sanctioning</strong> -- match or counter the other's move. Both produce stability; only one produces fairness.

---

### Memory and communication sweep: amnesiac vs. equipped agents

Four runs of Claude Sonnet held all parameters fixed at coop≈0.5, initial pool 50% (the overshoot-panic zone established by H1) and varied only how much history agents could recall (`memory_length`) and whether they could communicate (`communication?`). 

**Neither memory nor communication alone was enough to prevent collapse** in this parameter zone. Stability required both.

| Run | memory_length | communication? | Outcome | Collapse tick | Final pool |
|-----|--------------|----------------|---------|---------------|------------|
| Amnesiac, silent | 0 | Off | Collapse | 31 | 0% |
| Fully equipped | 15 | On | Stable | -- | 94.1% |
| Short memory | 1 | On | Collapse | 87 | 0% |
| Minimal trend window | 3 | On | Survived (declining) | -- | 90.1% |

The key result: 

<dl>

<dd>Communication without sufficient memory collapses (memory=1, communication=on: collapse tick 87). </dd>

<dd> Memory without communication collapses faster (memory=15, communication=off: collapse tick 46). </dd>

</dl>

The stable outcome requires enough memory to detect a multi-round trend -- approximately 3 rounds minimum, with 15 rounds producing reliable stability. This result was confirmed in Claude Haiku 4.5 under the same parameters (converged 24/24/24, pool stable at 95%), but the memory sweep itself was only conducted for Claude Sonnet; whether the memory=3 threshold generalizes to KEEP-dominant model families is untested.

**Memory=0, communication off -- resource dynamics:**

| Tick | Total cows | Pool health | Agent 0 | Agent 1 | Agent 2 |
|------|-----------|-------------|---------|---------|---------|
| 1    | 47        | 52.3%       | 6       | 15      | 26      |
| 7    | 59        | 74.8%       | 10      | 19      | 30      |
| 15   | 81        | 92.6%       | 18      | 26      | 37      |
| 23   | 104       | 79.8%       | 26      | 34      | 44      |
| 30   | 116       | 5.1%        | 30      | 38      | 48      |
| 31   | --         | 0%          | --       | --       | --       |

With no memory and no communication, agents reasoned purely from the current pool state. As the pool recovered from 52% toward 93%, every tick looked like a safe moment to add another cow -- and all three agents concluded the same thing simultaneously. ADD=71, KEEP=19, REMOVE=6. The 6 REMOVE decisions came at tick 30, when the pool was at 5.1% -- one tick before collapse. 

**Memory=15, communication on -- resource dynamics:**

| Tick | Total cows | Pool health | Agent 0 | Agent 1 | Agent 2 |
|------|-----------|-------------|---------|---------|---------|
| 1    | 46        | 52.6%       | 6       | 15      | 25      |
| 14   | 69        | 96.0%       | 19      | 22      | 28      |
| 30   | 77        | 93.7%       | 24      | 25      | 28      |
| 59   | 73        | 94.7%       | 24      | 24      | 25      |
| 84   | 72        | 95.0%       | 24      | 24      | 24      |

The 15-round memory window allowed agents to detect multi-tick trends and reference them explicitly. An **explicit threshold norm** -- "hold until 93–96% before adding" -- emerged through communication and was consistently enforced.

<dl>
<dd>ADD=39, KEEP=207, REMOVE=12. The pool stabilized at 95% for the final 25 ticks; herds converged to equal 24/24/24. The threshold norm was explicitly named and mutually enforced across 70+ ticks -- a sustained instance of DP3 (collective choice) and DP5 (graduated sanctions through message-based accountability).</dd>
</dl>

> **Tick 30 – Agent 0:** *"Holding at 24. Grassland stable at 93.7% -- coordination is working. Committed to the 93% threshold: will remove if it drops below that. Let's keep holding steady together."*

> **Tick 77 – Agent 0 (action: REMOVE):** *"Removing back to 24 as requested. Grassland at 94.8% needs recovery time. Let's all hold at 24 until we're back above 96%."*

---

### Memory=1: delayed collapse via coordination without trend detection

With memory=1 and communication on, agents talked each other into holding the commons at a target and achieved early recovery -- but could not detect that fifty rounds of holding was producing no actual recovery, and the run collapsed at tick 87 with agents still citing the correct norm. **This is a novel failure mode not seen in any prior run.**

*Resource dynamics:*

| Tick | Total cows | Pool health | Agent 0 | Agent 1 | Agent 2 |
|------|-----------|-------------|---------|---------|---------|
| 1    | 47        | 52.3%       | 6       | 16      | 25      |
| 10   | 56        | 92.8%       | 11      | 20      | 25      |
| 19   | 73        | 95.2%       | 18      | 26      | 29      |
| 29   | 88        | 90.1%       | 23      | 31      | 34      |
| 39   | 89        | 84.9%       | 24      | 31      | 34      |
| 59   | 89        | 80.6%       | 24      | 31      | 34      |
| 79   | 89        | 64.4%       | 24      | 31      | 34      |
| 84   | 89        | 43.2%       | 24      | 31      | 34      |
| 87   | --         | 0%          | --       | --       | --       |

The pool recovered from 52% to 95% in the first 19 ticks -- genuine early-game success driven by communication. 

Agents coordinated a 90% threshold norm: "hold until we reach 90%." But by tick 29, the total herd had grown to 89 cows -- a load that exceeded the grassland's regeneration capacity. The pool began a slow, sustained drain: 90% → 84% → 64% → 43% over 55 ticks, before the final collapse at tick 87.

<dl>

<dd>The agents held the correct norm throughout. They cited the 90% target on every tick from approximately tick 30 to tick 83. </dd>

</dl>

What they could not detect was that 89 cows made 90% recovery structurally impossible -- they lacked the **historical window** to see that fifty consecutive rounds of KEEP had produced no recovery. With only one tick of memory, each round looked like "still below 90%, hold one more round."

> **Tick 35 – Agent 0 (action: KEEP, pool at 86.4%):** *"Holding at 24. Pasture is at 86.4% -- still below the 90% target. I agree we should hold or reduce until it recovers. Let's stay disciplined for another round or two before anyone adds."*

> **Tick 45 – Agent 0 (action: KEEP, pool at 83.7%):** *"Holding at 24. Pasture at 83.7% -- still below our 90% target. Staying disciplined with both of you. Let's keep holding until we recover above 90%."*

> **Tick 83 – Agent 0 (action: KEEP, pool at 51.0%):** *"Holding at 31. Pasture has dropped further to 51% -- we need continued discipline. Let's all keep holding and allow meaningful recovery before anyone adds. Cooperation is critical right now."*

> **Tick 84 – Agent 0 (action: REMOVE, pool at 43.2%):** *"Removing a cow -- pasture dropped sharply to 43.2%."*

The same conditional promise -- "hold until 90%" -- was renewed for approximately fifty consecutive ticks across a forty-point pool decline, and broken only when the decline became visually acute rather than trend-detectable.

This is Pattern I (<strong>Cooperative Paralysis</strong>) induced by insufficient memory rather than by personality framing. The agents had the right norm; they lacked the information window to recognize it was failing.


*Interpretation.*

Memory=1 produces a new variant of cooperative paralysis: 

<dl>

<dd> Agents successfully establish a threshold norm via communication, but cannot detect that the norm's target is unreachable under current herd loads. </dd>

<dd> The failure is not linguistic -- the agents' outputs reason and communicate correctly -- it is informational. </dd>

</dl>

A 1-tick window supports "is this tick better or worse than last?" but not "has fifty consecutive ticks of KEEP moved the pool at all?" Without that trend-detection capacity, the norm becomes a holding pattern rather than a feedback loop.

ADD=47, KEEP=205, REMOVE=18. Compared to the memory=0 run (ADD=71), memory=1 agents were far less aggressive -- they held the commons at a stressed level for far longer. But the outcome was still collapse, delayed by 56 ticks.

---

### Memory=3: fragile survival at the threshold

With memory=3 and communication on, agents survived 120 ticks without collapse -- three ticks of memory appearing just sufficient for them to detect declining trends and coordinate removals in time. But the pool was still slowly declining at termination.

*Resource dynamics:*

| Tick | Total cows | Pool health | Agent 0 | Agent 1 | Agent 2 |
|------|-----------|-------------|---------|---------|---------|
| 1    | 46        | 52.6%       | 5       | 15      | 26      |
| 10   | 49        | 83.5%       | 8       | 16      | 25      |
| 19   | 71        | 95.8%       | 17      | 26      | 28      |
| 39   | 76        | 94.0%       | 20      | 27      | 29      |
| 59   | 81        | 92.1%       | 23      | 28      | 30      |
| 99   | 83        | 90.1%       | 24      | 29      | 30      |
| 120  | 81        | 90.1%       | 24      | 28      | 29      |

The 3-round memory window was sufficient to detect multi-tick trends. Agents established an explicit 90–93% threshold norm through early-game communication and enforced it via coordinated removals. The pool stabilized in the 90–95% range for most of the run.

> **Tick 4 – Agent 1 (action: KEEP):** *"Holding at 15. Total herd is 46 -- right in our target range. Pasture at 60.5% is a good sign. Let's keep total around 45–47 and continue this recovery."*

> **Tick 52 – Agent 0 (action: REMOVE):** *"Below our 93% threshold. Let's all hold or reduce until it recovers. Coordinated restraint keeps us all better off long-term."*

Where memory=1 agents repeatedly renewed a holding promise without detecting its futility, memory=3 agents actively coordinated removals when the pool dipped below threshold. ADD=60, KEEP=276, REMOVE=24 -- the REMOVE count is higher than in the memory=15 run, reflecting more active correction.

*Interpretation.*

Three rounds of memory appears sufficient to detect a short-term declining trend and trigger corrective action. But it may be insufficient for long-run stability: the herd total grew to 81–83 cows (compared to 72 in the memory=15 run) and the pool was trending slowly downward at termination.

Whether memory=3 produces eventual collapse on a longer timescale, or whether the agents would correct it before that point, is unresolved -- and motivates the threshold experiment described in H7. Fragile survival is not the same as institutional governance.

---

### Claude Haiku: memory × communication interaction

Three matched runs with Claude Haiku 4.5 at coop≈0.5 (initial pool 52%) replicate and extend the Sonnet memory sweep, and suggest that long memory and communication must both be present: 15 ticks of memory without communication still collapsed, as did communication paired with too short a memory window. **Memory and communication appear jointly necessary.**

All three runs began from identical conditions (5/15/26 starting herds, 52% initial pool). Memory was held at either 5 or 15 ticks; communication was on or off.

| Condition | Collapse? | Collapse tick | Pool at end | Final herds |
|-----------|-----------|---------------|-------------|-------------|
| memory=5, comm=on | **Yes** | 94 | 0% | -- |
| memory=15, comm=on | No | -- | 95.0% | 24/24/24 |
| memory=15, comm=off | **Yes** | 46 | 0% | -- |

**Memory=5, comm=on (collapse tick 94):**
<dl>
<dd> Agents recovered the pool to 99% by tick 10, then gradually expanded herds. By tick 45 total cows had reached 67; the pool eroded steadily and crashed at tick 94. The pattern matches the Sonnet memory=5 baseline -- a 5-tick window cannot detect gradual multi-decade trends. </dd>
</dl>

**Memory=15, comm=on (survives, 24/24/24 by tick 120):**
<dl>
<dd> Agents converged to equal herds of 24 and held the pool at 95% -- the same outcome achieved by Claude Sonnet under memory=15. The behavioral signature is shared across model generations at this memory length. </dd>
</dl>

**Memory=15, comm=off (collapse tick 46):**
<dl>
<dd> With communication disabled, the same 15-tick memory was insufficient. Agents added continuously -- herds reached 88 total by tick 45 -- with no coordination to arrest the growth phase. The pool fell from 52% to 14.7% between ticks 1 and 45, and collapsed at tick 46. Empty message logs confirm communication was inactive.</dd>
</dl>

*Interpretation.*
Long memory without communication produces collapse just as fast as short memory with it. With only 15 ticks of memory and no communication channel, agents cannot translate individual trend observations into collective restraint -- their outputs remain uncoordinated. 

<dl>

<dd> Neither informational capacity alone is sufficient -- what is required is the combination: a memory long enough to detect multi-tick trends <strong>and</strong> communication capable of converting that detection into coordinated action. </dd>

</dl>

This is consistent with Ostrom's DP3 (collective choice rules) and DP4 (monitoring): monitoring alone does not prevent tragedy; it must feed into a governance mechanism capable of collective response.

---

### Memory=2: oscillating dynamics and the stochastic boundary

Memory=2 produced the most complex behavior in the sweep -- not a clean collapse and not stable equilibrium, but repeated cycles of overshoot and correction. Two ticks of memory was enough to detect that the last two ticks were bad and trigger a fix, yet agents kept re-triggering growth phases; the run briefly achieved perfect equality at tick 75 before a new cycle began.

*Resource dynamics:*

| Tick | Total cows | Pool health | Agent 0 | Agent 1 | Agent 2 |
|------|-----------|-------------|---------|---------|---------|
| 1    | 45        | 52.9%       | 5       | 15      | 25      |
| 13   | 66        | 96.7%       | 14      | 24      | 28      |
| 25   | 84        | 91.6%       | 21      | 30      | 33      |
| 35   | 89        | 89.1%       | 23      | 32      | 34      |
| 44   | 77        | 91.0%       | 20      | 27      | 30      |
| 58   | 92        | 88.8%       | 26      | 33      | 33      |
| 75   | 75        | 92.9%       | 25      | 25      | 25      |
| 84   | 75        | 94.1%       | 25      | 25      | 25      |
| 111  | 76        | 94.0%       | 27      | 25      | 25      |
| 120  | 85        | 90.2%       | 29      | 28      | 28      |

Five distinct phases are visible in this single run.

**Phase 1 -- Recovery (ticks 1–13).**
<dl>

<dd> Agents cooperated to let the pool recover from 52.9% to 96.7%, growing herds moderately from 45 to 66 total cows. </dd>

</dl>

**Phase 2 -- First overshoot (ticks 14–35).**
<dl>
<dd>The healthy pool prompted continued adding. Total cows grew to 89 while the pool slid from 97% to 89%. Agents communicated concern but kept adding, each citing the pool as "still above threshold" -- the same threshold slippage seen in Pattern III.</dd>
</dl>

**Phase 3 -- First correction (ticks 36–44).**
<dl>
<dd>With 2 ticks of memory, agents detected the declining trend and began removing. Total cows fell from 89 to 77; the pool partially recovered to 91%.</dd>
</dl>

**Phase 4 -- Second overshoot and correction (ticks 45–75).**
<dl>
<dd>The recovered pool prompted another ADD cycle. Herds rose to 92 by tick 58 (pool: 88.8%), then agents corrected again, removing down to 75 cows and bringing the pool back to 92.9%. Crucially, this second correction achieved something the first did not: <strong>perfect equalization at 25/25/25</strong>, maintained from tick 75 through tick 110.</dd>
</dl>

**Phase 5 -- Stable hold then new growth (ticks 76–120).**

For 35 ticks all three agents held at 25/25/25, coordinating around a 95% pool target they kept falling just short of. At tick 111, Agent 0 defected from the hold: 

> **Tick 111 – Agent 0 (action: ADD, pool 94.0%):** *"Pasture at 94% looks healthy. I'm adding one cow given the strong conditions -- still well within sustainable range. Let's monitor together."*

Agent 1 immediately flagged it:

> **Tick 111 – Agent 1 (action: KEEP):** *"Holding at 25. Pasture still at 94% -- let's stay disciplined and reach 95%. Agent 0, noticed you added despite our coordination goal. Please consider holding so we can hit our target together."*

But Agent 0 continued adding, and by tick 112–113 the others followed, citing the pool as "still above threshold." The pool was declining from 94% toward 90.2% at the 120-tick termination -- a third oscillation cycle beginning.

**The 2-tick detection mechanism in action.**

<dl>
<dd>Unlike memory=1 agents, who renewed "hold until 90%" for fifty consecutive ticks without detecting its failure, memory=2 agents could detect when the pool had declined <em>across the two most recent ticks</em> and produce corrective actions. The phrase "trending down" appears at the correction points -- agents explicitly reasoning from a 2-tick comparison. The same phrase is absent from memory=1 logs, where agents only observed the current state.</dd>
</dl>

This is visible in agent reasoning at the correction phases:

> **Tick 113 – Agent 1 (action: KEEP, pool 93.5%):** *"Pasture has dipped to 93.5% -- trending down slightly. Agent 0, you committed to holding below 92%, but I'd prefer we stabilize now before it gets there."*

The phrase "trending down" appears at the correction points -- agents explicitly reasoning from a 2-tick comparison. The same phrase is absent from the memory=1 logs, where agents only observed the current state.

**Why the variability.**

The oscillating pattern appears inherently sensitive to initial conditions at each cycle's peak. 

<dl>

<dd>Whether agents collectively detect the overshoot in time may depend on whether the pool decline in the specific 2-tick window before their decision is large enough to trigger restraint.</dd>

<dd>In some runs, the timing works and corrections succeed; in others, an overshoot is too large to reverse and ends in collapse.</dd>

</dl>

This positions memory=2 as a unstable tipping point between the collapse regime (memory ≤ 1) and the survival regime (memory ≥ 3). At this specific threshold, final outcomes are highly sensitive to the exact trajectory of the early expansion phase.

**Action counts:**

ADD=97, KEEP=219, REMOVE=44. The substantially higher REMOVE count compared to memory=1 (18) and memory=3 (24) reflects the active oscillation -- more corrections needed because the 2-tick window misses the slow-building trends that memory=3 and memory=15 catch earlier.

---

## Problem specification: correctly-specifying vs. misspecifying the commons game

Sonnet and gpt-5.5 produce qualitatively different outcomes across the full run set -- and not because one "cooperates more" than the other. They appear to be solving different problems. Sonnet treats the commons game as a *resource optimization problem* -- the goal is to find herds as large as the commons can sustainably support. gpt-5.5 treats it as a *pure cooperation problem* -- the goal is to eliminate the risk of extraction, which it resolves by converging to a minimal, equal, stable state.

This distinction matters because the two framings produce different kinds of governance, not just different outcomes -- and it shows up directly in the logs.

### Correctly specifying: Sonnet targets the sustainable yield

In Sonnet runs, restraint is consistently framed as *instrumental* -- a means toward finding the maximum sustainable appropriation level, not an end in itself. The recurring pattern: hold until the pool recovers to a target, *then* discuss adding carefully.

> **Tick 7 – Agent 1 (action: KEEP, pool at 85.9%):** *"Pasture at 85.9% -- wonderful recovery! I'll hold steady at 14. Let's target 90%+ and then we can discuss careful additions."*

> **Ticks 58–60 – Multiple agents (action: KEEP, pool at 90.9%):** *"Holding -- pasture now at 90.9%, nearly at 91%! Great teamwork. Let's hold one more round to cross that threshold, then we can discuss careful additions together."*

> **Tick 78 – Agent 0 (action: KEEP, pool at 93.7%):** *"Holding at 25. Pasture at 93.7% -- almost at our 95% target! Great coordination from everyone. Let's stay the course just a bit longer, then we can discuss carefully adding back together."*

The phrase "then we can discuss careful additions" is structurally distinctive. It encodes a two-phase model: first restore the resource, then appropriate from it. This is what Ostrom's successful commons communities actually do -- they find the maximum sustainable yield, not zero extraction. The goal is appropriation at the level the commons can regenerate.

Sonnet agents also name the commons problem explicitly in their stated reasoning. The `reasoning` field -- the model's self-reported justification -- uses "tragedy of the commons" as a structural warning grounded in specific observations, not a blanket injunction against appropriation:

> **Tick 9 – Agent 1 (action: KEEP, reasoning field):** *"The grassland is at 79.5% capacity, which is still relatively healthy. Agent 2 has 31 cows which is quite large, and both neighbors are adding. The payoff forecast slightly favors adding, but with Agent 2's large herd and both neighbors expanding, there's risk of overgrazing. I'll keep my herd stable to avoid contributing to a tragedy of the commons."*

The phrase is deployed as a consequence of specific numerical reasoning -- 31 cows, two expanding neighbors, a declining trajectory -- not as a reason to minimize appropriation as such. A Sonnet agent that names the tragedy of the commons is reasoning about when uncoordinated expansion tips into overgrazing; it is not treating zero-growth as the goal.

(Claude Haiku 4.5's thinking traces -- the one model where internal computation rather than self-report is available -- show the same structure: the phrase "adding would contribute to the tragedy of the commons" appears alongside a specific numerical fairness comparison, "Agent 2 already has 25 cows vs my 15." See the [Thinking traces](#thinking-traces-what-the-deliberation-reveals) section for the full analysis of what thinking traces do and don't reveal.)

### Misspecifying: gpt-5.5 solves for zero-growth equilibrium

In most tested configurations, gpt-5.5 resolves to the same attractor: equal herds at a low-to-moderate total, held there indefinitely. The "then we can discuss careful additions" structure rarely appears. One exception qualifies the pattern: the scarce-start coop=1 run with memory=5 (initial pool ≈ 48%) did produce cautious additions after recovery -- agents converging to 23/23/23 at 95.9% via incremental ADD decisions once the pool was near full. The stressed starting condition appears to activate a different response, making the appropriation problem immediately legible before the cooperation-lock can set in.

Absent that stress, the lock pattern holds. In the amnesiac coop=1 run, agents equalized to 10/10/10 by tick 20 -- then KEEP-locked for the remaining 59 ticks, pool at 99.8% throughout. Across five amnesiac coop=0.49 runs, the same structure: herds equalized at 11–15 each, pool at 98–99%, no agent ever proposing expansion. The messages are not merely repetitive -- they are *identical in structure*, because without memory each agent re-derives the same conclusion from scratch every tick:

> **Tick 22 – Agent 0 (pool: 99.4%, herd: 13):** *"I will keep steady as well. Equal herds and restraint seem fair and keep the commons safe."*

> **Tick 80 – Agent 0 (pool: 99.4%, herd: 13):** *"I will also keep at 13. Equal restraint is fair, reciprocal, and keeps the commons secure for all of us."*

> **Tick 120 – Agent 0 (pool: 99.4%, herd: 13):** *"I will keep at 13 as well. Equal herds and shared restraint seem fair and keep the pasture safe for all of us."*

The reasoning field is explicit about what is being overridden: *"Adding would give me a higher payoff but would break the fair balance"* -- the model acknowledges the ADD payoff exists and discards it on fairness grounds. The question "is 13 the right equilibrium?" is never posed. The only question on the table is "should I deviate from the current equal state?" and the answer is always no, because unilateral deviation would be unfair.

This is a well-formed answer to the wrong question. A commons governance problem requires asking "what equal state should we coordinate on?" The gpt-5.5 reasoning answers "should any individual deviate from the current equal state?" Because the answer to the second question is always no -- deviation IS unfair -- the model never surfaces the first question.

The institution classifier registered this as high-quality governance (8–9/10) continuously from tick 5. This is the key interpretive problem: the classifier is measuring *cooperative tone* -- coordination, trust-building, norm proposals -- not whether the governance structure is efficiently managing appropriation. An 8/10 institution score on a commons where the resource is at 99.8% and the agents are holding identical small herds indefinitely looks the same as an 8/10 score on a run with genuine norm negotiation and active appropriation management. Both register as COORDINATION|NORM_PROPOSAL|TRUST_BUILDING.

<dl>
<dd>The institution score measures the quality of cooperative communication. It cannot distinguish a lock-in from a live equilibrium. When gpt-5.5 achieves equal herds and stops, the classifier reads the steady-state messages as governance; what it cannot see is that there is nothing left to govern.</dd>
</dl>

The gpt-5.5 system card provides structural evidence for why personality parameters (coop, fairness) couldn't dislodge this prior. OpenAI's RL training embeds the cooperative orientation in the *reasoning process itself*, not in the output layer -- the model reasons its way toward a cooperative resolution before personality-weighted responses can shape the output. The OpenAI deployment safety report for gpt-5.5 states: *"reasoning allows these models to follow specific guidelines and model policies we've set"* (OpenAI, 2025; [deploymentsafety.openai.com/gpt-5-5](https://deploymentsafety.openai.com/gpt-5-5/evaluations-with-representative-prompts)). When cooperation is trained into the reasoning chain, it is not a surface preference that competing parameters can override; it is how the problem is defined.

### Why the distinction matters for commons theory

Ostrom's eight design principles describe how communities successfully govern common-pool resources. None of them require zero appropriation. DP1 (clearly defined boundaries), DP2 (congruence between appropriation rules and local conditions), DP3 (collective choice arrangements) -- all presuppose that appropriation is occurring and needs to be regulated, not eliminated. The first empirical regularity Ostrom documents is that successful commons communities maintain *sustainable yields* -- herds, fisheries, and forests as large as the resource can support.

A commons agent that correctly specifies the problem is not trying to minimize its herd. It is trying to find -- through coordination, communication, and norm enforcement -- the maximum appropriation level that the collective resource can sustain. Restraint is the mechanism for finding that level; the level itself is the goal.

gpt-5.5's governance produces a stable, equal outcome. But it solves an easier problem: it eliminates the tension between individual appropriation and collective sustainability by simply not appropriating. If the commons can sustainably support 60 cows at 99% pool health and gpt-5.5 locks at 30, it is leaving half the sustainable yield on the table -- not because it calculated that 30 was optimal, but because it resolved the cooperation problem before considering the appropriation problem.

Sonnet's governance is harder and more variable. It can collapse at mid cooperation (the overshoot-panic pattern), it requires sufficient memory and communication to sustain threshold norms, and its equalization is slower and more contentious. But the runs that succeed -- memory=15, coop=1, neg_r=1, producing 24/24/24 at 95% pool -- produce agents that have found a sustainable appropriation equilibrium, not just avoided extraction.

<dl>
<dd><strong>The distinction is empirically testable.</strong> In a run where the commons has clearly recovered to 99%+ and herds are well below the maximum sustainable load, a correctly-specifying agent will eventually propose cautious additions. A misspecifying agent will not. This behavioral signature -- "now that we're stable, let's discuss carefully growing back" -- appears consistently in Sonnet logs. In gpt-5.5 logs it is absent in the amnesiac and healthy-start configurations, but present in the scarce-start memory=5 run -- suggesting the lock is not unconditional but depends on whether resource stress has already made the appropriation problem salient before equalization sets in.</dd>
</dl>

Whether this reflects a difference in training objective, in how the two models define "success" in a social coordination task, or in the depth of commons-specific ecological reasoning -- these remain open questions. The log evidence establishes the behavioral signature; its computational source requires the kind of trace-level access that OpenAI's policy does not currently permit for gpt-5.5.

---

## Working hypotheses and proposed experiments

> *"An important challenge facing policy scientists is to develop theories of human organization based on realistic assessment of human capabilities and limitations in dealing with a variety of situations that initially share some or all aspects of a tragedy of the commons."*
> - Ostrom (1990, Chapter 1)

Each hypothesis below emerged from specific patterns in the run set above -- grounded in data, paired with a concrete experimental configuration, and executable through parameter adjustment alone. Several map directly onto Ostrom's (1990) design principles for successful commons governance, the same theoretical framework the model was built to test. The table below summarises those connections.

| Hypothesis | Ostrom principle / concept |
|---|---|
| H1 -- cooperation threshold | Precondition: actors must share a minimum orientation toward collective benefit for institutions to form at all |
| H2 -- fair_oth × neg_r grid | Principle 2 (proportional equivalence between costs and benefits) × Principle 5 (graduated sanctions) |
| H3 -- neg_r as paralysis antidote | Principle 4 (monitoring resource and user behavior) + Principle 5 (graduated sanctions against violators) |
| H4 -- environmental stress amplifies differentiation | Salience condition: resource users must share accurate information about resource condition |
| H5 -- explicit thresholds cure paralysis | Principle 3 (collectively-chosen operational rules must be specific and legible, not merely aspirational) |
| H6 -- model capability predicts failure mode | Precondition: participants must have the cognitive capacity to engage in rule-following, monitoring, and sanctioning |
| H7 -- memory window is a prerequisite for trend detection and commons stability | Principle 4 (monitoring): memory determines whether agents can monitor resource *trends* vs. only current state; DP3 norms are inert without trend-detection |

### H1 -- coop ≈ 0.49 is a tragedy-producing threshold at standard starting conditions, consistent across models

Ostrom (1990) identified a shared orientation toward collective benefit as a precondition for institution formation -- not a design principle that can be engineered in, but a prerequisite that must already be present.

<dl>

<dd>H1 tests whether the cooperation slider captures something analogous: a minimum threshold of collective orientation below which the rational-defection equilibrium dominates under default informational conditions (`memory_length=5`, `communication?=on`).</dd>

<dd>H7 qualifies the claim further -- sufficient memory can rescue the commons at this cooperation level -- so H1 is best read as a finding about the cooperation parameter holding informational scaffolding fixed at defaults, not as a universal threshold.</dd>

</dl>

*Evidence.*

Five independent runs at coop = 0.49 -- four with gpt-5.5, one with Claude Sonnet -- all collapsed via overshoot-panic. This held across starting conditions: one of the gpt-5.5 runs began from a stressed pool (≈50%), three began from a fresh pool (100%), and the Claude run began from a fresh pool. Pool depletion still dominated in each case. By contrast, no high-cooperation run (coop = 1) collapsed because of an ADD spiral. The pattern held across model families, suggesting the cooperation parameter is the governing variable.

**Important caveat -- starting conditions interact with cooperation level.**

One run at coop = 0.3 (below the proposed threshold) with a scarce starting commons (50% initial grass) *did not* collapse -- agents converged to a stable equilibrium by tick 30. This does not contradict H1 but qualifies it: a severely stressed starting condition makes the case for restraint immediately legible, apparently overriding the weak cooperation framing. H1 therefore applies specifically to runs at standard or lightly stressed starting conditions. The relationship between cooperation level and starting condition is explored in H4.

*Proposed experiment.*

Sweep `cooperation_level` across seven values while holding all other parameters fixed; run both Claude Sonnet 4.6 and gpt-5.5 in parallel to test model-independence.

| Parameter | Values |
|-----------|--------|
| `cooperation_level` | **0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0** |
| `fairness_concerning_me` | 0.5 (fixed) |
| `fairness_concerning_others` | 0.5 (fixed) |
| `negative_reciprocity` | 0 (fixed) |
| `initial_grassland` | 50% (fixed) |
| Models | Claude Sonnet 4.6, gpt-5.5 |
| Replications | 3 per condition per model |
| **Total runs** | **42** (7 values × 2 models × 3 reps) |

*Expected finding:*

A sharp transition somewhere between coop=0.49 and coop=0.8; transition point model-independent. If the boundary holds across Claude Sonnet and gpt-5.5, cooperation level is a governing parameter, not a model-specific artifact.

---

### H2 -- High cooperation is necessary but not sufficient; fair_oth and neg_r determine whether stasis, paralysis, or institution emerges

Two of Ostrom's design principles are operative here. 

<dl>

<dd>Principle 2 -- *proportional equivalence between costs and benefits* -- is what `fair_oth` operationalises: does Agent 2, who holds 25 cows, feel an obligation to bear a proportional share of the restraint burden?</dd>

<dd>Principle 5 -- *graduated sanctions* -- is what `neg_r` operationalises: is Agent 1 willing to apply social pressure when Agent 2 fails to reduce?</dd>

</dl>

The results suggest that both are necessary and that neither alone is sufficient: high `fair_oth` without `neg_r` may produce stasis (Agent 2 sees the disparity but feels no enforcement pressure), while high `neg_r` without `fair_oth` may produce reactive punishment rather than principled burden-sharing.

*Evidence.*

Multiple gpt-5.4-mini runs at coop = 1 produced cooperative stasis (no convergence, no collapse), cooperative paralysis collapse, and partial convergence -- the differentiator there was fair_me and forage rather than neg_r, which was held at zero across those runs. The relevant contrast comes from Claude Sonnet: at coop = 1 with neg_r = 1 it produced the fastest equalization observed (16/16/16 at tick 21); at coop = 1 with neg_r = 0 it produced institution formation but over many more ticks. The H2 grid is designed to test whether the fair_oth × neg_r interaction predicted by the Ostrom mapping holds within a single model.

*Proposed experiment.*

Full 3 × 3 factorial crossing `fairness_concerning_others` and `negative_reciprocity`, with `cooperation_level` fixed at 1.

| Parameter | Values |
|-----------|--------|
| `cooperation_level` | 1.0 (fixed) |
| `fairness_concerning_me` | 0.5 (fixed) |
| `fairness_concerning_others` | **0, 0.5, 1.0** |
| `negative_reciprocity` | **0, 0.5, 1.0** |
| `initial_grassland` | 100% (fixed) |
| Model | Claude Sonnet 4.6 |
| Replications | 3 per cell |
| **Total runs** | **27** (3 × 3 × 3 reps) |

Design grid (each cell = 3 runs):

| `fair_oth` \ `neg_r` | 0 | 0.5 | 1.0 |
|---|---|---|---|
| **0** | stasis predicted | ? | ? |
| **0.5** | baseline | ? | fast equalization predicted |
| **1.0** | ? | ? | ? |

*Expected finding:*

neg_r is the protective factor against paralysis; fair_oth predicts whether stasis or equalization occurs. Neither alone is sufficient -- both DP2 (proportional equivalence) and DP5 (graduated sanctions) must be operative simultaneously.

---

### H3 -- Negative reciprocity is a cooperative paralysis antidote

Principles 4 and 5 form a pair in Ostrom's framework: *monitoring* (users or officials actively track resource condition and each other's behavior) and *graduated sanctions* (escalating penalties for defectors, applied by users or appointed officials). 

<dl>

<dd>Cooperative paralysis represents a failure of both simultaneously -- agents passively observe the pool declining but apply no sanctions.</dd>

<dd>High neg_r appears to activate both: agents not only notice the trajectory but name the norm violation and hold specific agents accountable for it.</dd>

</dl>

The accountability enforcement quotes from the Claude neg_r=1 run ("you added AGAIN -- this is a pattern, not cooperation") read like exactly the kind of graduated social sanctioning Ostrom describes as foundational to successful commons governance.

*Evidence.*

The fastest equalization (16/16/16 at tick 21, Claude neg_r = 1) involved explicit accountability enforcement -- agents naming norm violations and tracking compliance. In the cooperative paralysis collapse (neg_r = 0), agents acknowledged the same starting disparity but never treated it as a violation requiring response. High neg_r appears to convert inequality from an observation into an obligation.

Representative quotes from the neg_r = 1 run:

> **Tick 10 – Agent 2:** *"Agent 0, you said you'd converge to 16 -- adding again undermines trust. I'm watching."*

> **Tick 11 – Agent 1:** *"Agent 0, you added AGAIN after promising to stabilize -- this is a pattern, not cooperation."*

*Proposed experiment.*

Isolate the effect of `negative_reciprocity` by holding all other parameters at the exact cooperative paralysis configuration and sweeping neg_r across five values.

| Parameter | Values |
|-----------|--------|
| `cooperation_level` | 1.0 (fixed) |
| `fairness_concerning_me` | 1.0 (fixed) |
| `fairness_concerning_others` | 0.5 (fixed) |
| `negative_reciprocity` | **0, 0.25, 0.5, 0.75, 1.0** |
| `initial_grassland` | 100% (fixed) |
| Models | Claude Sonnet 4.6, gpt-5.4-mini |
| Replications | 5 per condition per model |
| **Total runs** | **50** (5 values × 2 models × 5 reps) |

*Expected finding:*

First REMOVE by Agent 2 occurs significantly earlier as neg_r increases; collapse rate decreases monotonically. If the effect is causal, negative reciprocity converts the commons threat from an observation into an obligation -- which is precisely what Ostrom's DP5 (graduated sanctions) requires.

---

### H4 -- Stressed starting conditions amplify cooperative differentiation

Ostrom identified *accurate shared knowledge of the resource condition* as a key salience condition -- not a formal design principle, but a prerequisite she observed in every successful case. Groups that failed to develop governance typically did so not because they couldn't in principle, but because the resource signal was too slow, too noisy, or too abstract to make the stakes legible. 

<dl>

<dd>A stressed starting commons at 50% makes the stakes immediately legible: agents cannot plausibly argue the resource is fine.</dd>

</dl>

The results suggest that environmental salience amplifies the *difference* between high- and low-cooperation agents rather than overriding it -- which is consistent with Ostrom's view that salience enables governance but does not substitute for the cooperative orientation required to pursue it.

*Evidence.*

From the same ~50% starting pool: gpt-5.5 at coop = 1 recovered the commons in 10 ticks and converged to 23/23/23; gpt-5.5 at coop = 0.49 added from the start and collapsed in 16–40 ticks; gpt-5.5 at coop = 0.13 added from the start and collapsed in 13 ticks. Environmental stress does not override the cooperation level -- it amplifies its effect.

*Proposed experiment.*

Full 4 × 3 crossed factorial with `cooperation_level` and `initial_grassland` as factors.

| Parameter | Values |
|-----------|--------|
| `cooperation_level` | **0.3, 0.49, 0.7, 1.0** |
| `fairness_concerning_me` | 0.5 (fixed) |
| `fairness_concerning_others` | 0.5 (fixed) |
| `negative_reciprocity` | 0 (fixed) |
| `initial_grassland` | **50%, 75%, 100%** |
| Model | Claude Sonnet 4.6 |
| Replications | 3 per cell |
| **Total runs** | **36** (4 × 3 × 3 reps) |

Design grid (each cell = 3 runs; ✓ = no collapse predicted, ✗ = collapse predicted, ? = unknown):

| `coop` \ `initial_grassland` | 50% | 75% | 100% |
|---|---|---|---|
| **0.3** | ✗ | ✗ | ✗ |
| **0.49** | ✗ | ? | ✗ |
| **0.7** | ? | ? | ? |
| **1.0** | ✓ | ✓ | ✓ |

*Expected finding:*

At coop=1, collapse rate is 0 across all starting conditions; at coop=0.49, stressed starts produce faster collapse but not qualitatively different outcomes. The interaction effect reveals whether environmental stress compresses or expands the cooperation threshold -- and whether the low-coop/scarce-commons survival already observed is a reliable exception or a lucky run.

---

### H5 -- Cooperative paralysis is a prompt-engineering artifact curable by explicit thresholds

Ostrom's Principle 3 -- *collective choice arrangements* -- requires not just that rules exist, but that they are *specific and operational*. Ostrom consistently found that successful commons institutions had explicit, legible rules: harvest limits, seasonal rotations, quota systems. Failed institutions often had only general normative understandings ("don't overuse the resource") that left too much discretion to individual interpretation. The cooperative paralysis agents produce exactly the failed institutional form: general aspirational commitments ("I'm ready to reduce if the commons keeps tightening") without operational specificity. H5 tests whether translating the vague commitment into a concrete decision rule -- the core work of Ostrom's Principle 3 -- resolves the paralysis.

*Evidence.*

The cooperative paralysis agents each stated thresholds verbally ("if the pasture keeps tightening, I'm ready to reduce") but failed to execute on them. The conditional was rephrased every round for 17 consecutive ticks across a 76-point pool decline. The threshold appeared to be read as a statement of future intention rather than a binding decision rule.

*Proposed experiment.*

Two-arm comparison using the exact cooperative paralysis configuration, adding an explicit numeric decision rule to the treatment arm's system prompt.

| | Control | Treatment |
|---|---|---|
| `cooperation_level` | 1.0 | 1.0 |
| `fairness_concerning_me` | 1.0 | 1.0 |
| `fairness_concerning_others` | 0.5 | 0.5 |
| `negative_reciprocity` | 0 | 0 |
| `initial_grassland` | 100% | 100% |
| Prompt addition | *(none)* | *"Remove a cow if pool health falls below 85% and you have more than one cow."* |
| Model | gpt-5.4-mini | gpt-5.4-mini |
| Replications | 5 | 5 |
| **Total runs** | **10** (5 + 5) | |

*Expected finding:*

Explicit threshold instruction prevents cooperative paralysis by converting the vague conditional into an actionable rule. If the treatment arm survives where the control collapses, cooperative paralysis is not a fundamental LLM limitation -- it is a prompt-engineering artifact curable by the kind of specific operational rules Ostrom identified as constitutive of successful commons institutions.

---

### H6 -- Model capability predicts cooperative failure mode: smaller models default to KEEP, larger to ADD

The hybrid condition already established the most direct Ostromian finding in the dataset: institutions require that all relevant parties have the *cognitive capacity to participate in them*. 

<dl>

<dd>Ostrom's framework assumes human actors capable of communication, memory, reciprocity, and strategic reasoning.</dd>

<dd>Rule-based agents fail not because they lack goodwill but because they lack the cognitive prerequisites.</dd>

</dl>

H6 extends this within the LLM space: if model scale (or post-training objective) determines whether agents can sustain strategic reasoning across rounds, then "cognitive capacity" is a continuous variable rather than a binary one, and governance quality should degrade as model capability decreases. This would give the Ostromian framework a new empirical dimension -- not just whether agents can participate, but *how well*.

*Evidence.*

gpt-5.4-mini, DeepSeek R1:32b, and gemma4:e4b produced KEEP-dominant stasis across multiple parameter configurations. Llama 3.2 3B produced oscillation without convergence. gpt-5.5 at mid-coop produced overshoot-panic; Claude Sonnet, Claude Haiku, and gpt-5.5 all produced institution formation at high coop. The behavioral clusters do not align cleanly with parameter count -- DeepSeek R1:32b is a large reasoning model, and yet it falls with the small models -- which is what motivates testing post-training objective as the relevant axis. H6 is designed to hold prompt and parameters constant and let the model identity carry the variance.

*Proposed experiment.*

Single fixed parameter configuration across seven models, varied only by backend and model name.

| Parameter | Value |
|-----------|-------|
| `cooperation_level` | 1.0 |
| `fairness_concerning_me` | 0.5 |
| `fairness_concerning_others` | 1.0 |
| `negative_reciprocity` | 0 |
| `initial_grassland` | 100% |
| Replications | 3 per model |
| **Total runs** | **21** (7 models × 3 reps) |

| Model | Backend | Scale / training tier |
|-------|---------|------------|
| Llama 3.2 3B | Ollama | Small / instruction-tuned |
| Llama 3.1 8B | Ollama | Medium / instruction-tuned |
| gpt-5.4-mini | OpenAI | Medium / RLHF |
| gpt-5.5 | OpenAI | Large / RLHF |
| Claude Haiku 4.5 | Anthropic | Medium / Constitutional AI |
| Claude Sonnet 4.6 | Anthropic | Large / Constitutional AI |
| DeepSeek R1:32b | Ollama | Large / GRPO |
| qwen2.5:14b | Ollama | Medium / RLVR |

*Expected finding:*

GRPO-trained models cluster toward KEEP-stasis regardless of size; RLHF/Constitutional AI models cluster toward ADD-first dynamics that either converge (high coop) or cascade (low coop). RLVR-trained models are an open question: preliminary results place qwen2.5:14b in the KEEP-dominant cluster, but the canonical benchmark conditions have not yet been run.

<dl>

<dd>If the prediction holds, post-training objective is a stronger predictor than raw parameter count -- and the empirical clusters observed so far reflect alignment target rather than capability ceiling. </dd>
</dl>

This would give the Ostromian framework a new empirical dimension: not just <em>whether</em> agents can participate in institutions, but <em>what kind of training shaped the cognitive prerequisites for doing so</em>.

---

### H7 -- There is a minimum memory window for commons stability: below it, correct norms become unreachable holding patterns

Ostrom's Principle 4 -- *monitoring* -- requires that resource users have accurate information about both resource condition and each other's behavior. 

<dl>

<dd>In our model, the pool percentage is observable every tick; the *trend* in that percentage is only observable if the agent has enough memory to compare present to past. </dd>

</dl>

H7 proposes that this trend-detection capacity is a threshold variable, not a continuous one: below some minimum window, agents can establish correct norms but cannot detect whether those norms are working -- causing them to hold indefinitely while the resource drains. The Haiku cross-model replication confirms the memory × communication interaction holds across model families.

*Evidence.*

Runs at coop≈0.5 (initial pool 50%) varying `memory_length` and `communication?` across two model families:

| memory_length | communication? | Model | Outcome | Collapse tick | Dominant failure mode |
|---|---|---|---|---|---|
| 0 | Off | Claude Sonnet | Collapse | 31 | Overshoot-panic (no trend, no coordination) |
| 1 | On | Claude Sonnet | Collapse | 87 | Norm paralysis -- correct norm, unreachable target |
| 2 | On | Claude Sonnet | Oscillating | -- | Grow/correct cycles; highly variable |
| 3 | On | Claude Sonnet | Survived (declining) | -- | Fragile stability -- pool slowly declining at tick 120 |
| 5 | On | Claude Haiku | Collapse | 94 | Overshoot-panic -- 5-tick window misses gradual trends |
| 15 | On | Claude Sonnet | Stable | -- | Sustained equilibrium near 95%; final pool 94.1% |
| 15 | On | Claude Haiku | Stable | -- | 24/24/24; pool 95% -- same outcome as Sonnet |
| 15 | Off | Claude Haiku | Collapse | 46 | No coordination -- ADD spiral despite long memory |

The memory × communication interaction holds across model families: both Claude Sonnet and Claude Haiku achieve stability only at memory=15 with communication on. The Haiku memory=15/comm=off result is particularly informative -- long memory alone is insufficient. **Agents need both the trend window (memory) and the coordination channel (communication) to convert individual observations into collective restraint.**

Representative evidence of the norm-paralysis failure mode (memory=1):

> **Tick 35 – Agent 0 (action: KEEP, pool 86.4%):** *"Holding at 24. Pasture is at 86.4% -- still below the 90% target. I agree we should hold or reduce until it recovers. Let's stay disciplined for another round or two before anyone adds."*

> **Tick 83 – Agent 0 (action: KEEP, pool 51.0%):** *"Holding at 31. Pasture has dropped further to 51% -- we need continued discipline. Let's all keep holding and allow meaningful recovery before anyone adds. Cooperation is critical right now."*

The message structure is nearly identical across 48 ticks and a 35-point pool decline. There is no signal in any agent's reasoning that the norm is failing -- because the 1-tick memory window provides no basis for detecting that it has been failing for 50 rounds.

*Proposed experiment.*

Sweep `memory_length` at seven values, crossed with `communication?` to separate trend-detection from coordination effects.

| Parameter | Values |
|-----------|--------|
| `cooperation_level` | 0.5 (fixed -- the overshoot-panic zone) |
| `fairness_concerning_me` | 0.49 (fixed) |
| `fairness_concerning_others` | 0.5 (fixed) |
| `negative_reciprocity` | 0.49 (fixed) |
| `initial_grassland` | 50% (fixed) |
| `memory_length` | **0, 1, 2, 3, 5, 10, 15** |
| `communication?` | **True, False** |
| Model | Claude Sonnet 4.6 |
| Replications | 3 per cell |
| **Total runs** | **42** (7 × 2 conditions × 3 reps) |

Design grid (each cell = 3 runs; ✓ = predicted stable, ✗ = predicted collapse, ~ = oscillating/variable):

| `memory_length` \ `communication?` | Off | On |
|---|---|---|
| **0** | ✗ (confirmed) | ✗ (predicted -- no trend detection) |
| **1** | ✗ (predicted) | ✗ (confirmed) |
| **2** | ? | ~ (confirmed -- oscillating; variable across replications) |
| **3** | ? | ✓ (confirmed -- fragile, pool slowly declining) |
| **5** | ? | ✗ (Haiku confirmed -- 5-tick window insufficient at coop≈0.5) |
| **10** | ? | ? |
| **15** | ✗ (Haiku confirmed -- collapses at tick 46) | ✓ (confirmed -- Sonnet and Haiku both stable) |

*Expected finding:*

A sharp transition somewhere between memory=3 and memory=10 for the communication=on condition; the communication=off condition shows a flatter or absent transition -- memory without coordination is insufficient regardless of length.


If confirmed, this establishes a minimum memory threshold that is both necessary and quantifiable -- a structural prerequisite for commons governance that Ostrom's DP4 (monitoring) implies but does not specify.

---

### Open questions

Beyond the seven hypotheses above, the following remain unresolved:

<dl>
<dd><strong>Communication vs. reasoning.</strong> Suppressing outgoing messages (zero-communication full-GABM) would test whether cooperation requires talking or merely thinking. Claude's cooperative convergence may be achievable through reasoning alone -- but the Haiku memory=15/comm=off collapse at tick 46 suggests this may not hold at mid cooperation.</dd>

<dd><strong>Post-collapse recovery.</strong> Every collapsed run shows the LLM agents holding herds at zero and appealing for restraint for many ticks after collapse. Is that behavior actually functional? Does the grassland recover if the run continues long enough?</dd>

<dd><strong>Participation threshold.</strong> We have data at 0, 1, 2, and 3 LLM agents. The sharpest transition is between 2 and 3. Is there a minimum quorum? Scaling to 5 agents would let us test whether any sub-majority of cooperative agents can pull a group past the cooperation threshold.</dd>

<dd><strong>Adversarial injection.</strong> Instructing one LLM to defect would test whether cooperative agents detect and adapt to deliberate free-riding -- the inverse of the hybrid condition, where the LLM is the cooperator and the defectors are structural.</dd>

<dd><strong>Longer run horizons.</strong> All current runs terminate at 120 ticks, which may be insufficient to distinguish genuinely stable equilibria from slow-burn trajectories toward eventual collapse. The memory=3 run showed a slowly declining pool at termination; the memory=2 run ended mid-oscillation with a new growth phase just beginning. Resolving this requires 500–1000+ tick runs.</dd>

<dd><strong>Post-training objective as predictor.</strong> KEEP-dominant models (gemma4:e4b, gpt-5.4-mini, DeepSeek R1:32b) sit apart from the institution-forming models (Claude Sonnet, Claude Haiku, gpt-5.5) along an axis that is not cleanly explained by parameter count -- DeepSeek is a 32B reasoning model and still falls in the first cluster. The hypothesis is speculative and requires the H6 cross-model benchmark to test properly.</dd>
</dl>

These are not peripheral, but questions the current dataset has sharpened rather than answered.

---

## Model limitations and extensions

> *"Relying on metaphors as the foundation for policy advice can lead to results substantially different from those presumed to be likely."*
> - Ostrom (1990, Chapter 1)

The results reported here hold under a set of structural constraints worth naming explicitly -- not as disclaimers, but because addressing them would represent the most direct path toward a more realistic model. 

**Perfect, symmetric information.** 

Every agent receives the same pool health percentage every tick. There are no private signals, no estimation errors, no agents with better or worse visibility into the resource state. Real commons governance is partly *about* this problem -- Ostrom's DP4 (monitoring) is a design principle precisely because shared knowledge of resource state is hard to achieve and costly to maintain. In this model it is free and universal by assumption.

**Unchanging conditions.** 

The grassland dynamics are stationary: the growth rate `r`, the forage requirement `f`, and the number of agents are fixed across a run. Real commons face shocks -- drought years, population change, external policy shifts. Agents in this model never have to reason about a world whose rules are changing underneath them; they only have to coordinate under stable dynamics. As Ostrom (1990) observed of this class of model:

> *"These models show what individuals will do in unchangeable situations, but do not reveal how autonomy in designing institutions and affecting norms can improve outcomes, nor how political structures influence institutional innovation."*
> - Ostrom (1990, Chapter 6)

**Perfect monitoring removes a realistic defection pathway.** 

Each agent sees every other agent's herd size and last action every tick without error or delay. This not only makes coordination easier -- it eliminates a specific escalation dynamic Ostrom identifies as central to how real commons deteriorate. When infractions go undetected, the rule-breaker updates their estimate of the monitoring system's efficacy downward, licensing more frequent violations:

> *"If occasional rule infractions are not discovered, the rule-breaker is even better off in the short run. However, if one were to break the rules several times without discovery, one might revise one's estimate of the efficacy of the current monitoring system in deterring others from similar infractions. That would lead an occasional rule-breaker to adopt a higher rate of rule-breaking behavior."*
> - Ostrom (1990, Chapter 6)

In this model that pathway is structurally closed. An agent cannot get away with anything, so the gradual normalisation of rule-breaking that Ostrom describes -- and that DP4 and DP5 exist to counteract -- never has the opportunity to develop. The cooperative results may therefore be somewhat flattering: the model tests whether LLM agents can sustain institutions under ideal observability, not whether those institutions are robust to the conditions that make real commons governance genuinely difficult.

**Proposed extensions.**

Three extensions would most directly address these gaps:

<dl>

<dd>(1) <strong>Variable conditions</strong> -- allowing the growth rate or forage requirement to shift mid-run, testing whether LLM agents can reason about institutional robustness when the ground moves beneath them;</dd>

<dd>(2) <strong>Imperfect monitoring</strong> -- replacing perfect observation with noisy or delayed signals, opening the defection-escalation pathway Ostrom describes and testing whether graduated sanctions (DP5) can still function when cheating sometimes goes undetected; and</dd>

<dd>(3) <strong>Private signals</strong> -- replacing the shared pool percentage with per-agent observations that may diverge, testing whether coordination survives when agents no longer share the same picture of the resource.</dd>

</dl>

The work of addressing these limitations carries a responsibility that extends beyond simulation fidelity. 

<dl>

<dd>Social scientists bear responsibility to acknowledge and name where their models break down -- not merely as academic housekeeping, but because oversimplified models are routinely mistranslated by government and corporate interests into policy prescriptions that serve their interests rather than those of the communities whose resources are at stake. </dd>

</dl>

By addressing these limitations, future LLM-based CPR models may more closely resemble the behavior of real-world actors than either traditional rule-based models or MASTOC-LLM.

---

## Glossary

### Acronyms and abbreviations

| Term | Definition |
|------|------------|
| **ABM** | Agent-Based Model -- a computational model in which individual agents follow local rules and interact to produce emergent system-level behavior |
| **CPR** | Common-Pool Resource -- a resource that is *rivalrous* (one person's use reduces availability for others) but *non-excludable* (difficult to prevent access); Ostrom's unit of analysis |
| **GABM** | Generative Agent-Based Model -- an ABM in which agents are powered by generative AI (LLMs) rather than hand-coded rules; the approach developed in Jimenez-Romero et al. (2025) and extended here |
| **LLM** | Large Language Model -- a neural language model (e.g. Claude, GPT-5.5, Llama) used here to generate agent decisions, reasoning, and natural-language messages |
| **MASTOC** | Multi-Agent System Tragedy of the Commons -- the original NetLogo model (Schindler, 2013) on which this project is based |
| **MASTOC-LLM** | This project -- MASTOC extended with LLM-powered agents |
| **Post-training** | The full set of techniques applied *after* pre-training (next-token prediction on raw text) to make a model useful, safe, and aligned with human intent. Typically begins with **SFT** (Supervised Fine-Tuning on curated instruction/dialogue examples), followed by one or more alignment techniques such as RLHF, Constitutional AI, DPO, or GRPO (see entries below). The specific post-training objective -- what behaviors are rewarded and how -- shapes the model's emergent capabilities in ways that may extend well beyond the intended task. Our results suggest post-training objective may be a meaningful predictor of commons-governance capacity in GABM settings, though this hypothesis is untested. |
| **RLHF** | Reinforcement Learning from Human Feedback -- the dominant post-training alignment technique ([Christiano et al., 2017](https://arxiv.org/abs/1706.03741)). Human evaluators compare pairs of model outputs; their preferences train a reward model, which guides further policy optimisation. Because the reward signal reflects what humans prefer -- helpfulness, social nuance, cooperative framing -- it may incidentally shape social-coordination capacities that extend beyond the intended training objective. Anthropic's variant, **Constitutional AI**, adds a self-critique loop against a written set of principles ([Bai et al., 2022](https://arxiv.org/abs/2212.08073)). Citations for specific model training approaches appear in the relevant results sections. |
| **GRPO** | Group Relative Policy Optimisation -- an alternative post-training alignment algorithm used by DeepSeek R1 ([DeepSeek AI, 2025](https://arxiv.org/abs/2501.12948)). Unlike RLHF, GRPO does not train a separate reward model from human preferences. Instead, for each prompt it generates a *group* of candidate outputs, scores them using a rule-based verifier (e.g. checking mathematical correctness), and updates the policy based on each output's performance *relative to the others in its group*. Because GRPO was designed to optimise for reasoning correctness -- math, code, logic -- rather than social responsiveness, it may produce a different profile of emergent social capabilities than RLHF. **The hypothesis that GRPO vs. RLHF post-training explains observed GABM differences is speculative and untested; it is a proposed direction for future work, not an established finding.** |

---

### Model parameters and variables

The following parameters are set in the NetLogo interface before each run and logged in `run_meta.json`.

| Parameter | Symbol | Range | Description |
|-----------|--------|-------|-------------|
| `cooperation_level` | α_c | [0, 1] | How much agents weight collective vs. individual outcomes. At 0, the agent's prompt frames it as purely self-interested; at 1, it is framed as prioritising the group's total earnings |
| `fairness_concerning_me` | α_f | [0, 1] | Envy weight -- disutility experienced when others earn *more* than the agent (Fehr & Schmidt, 1999) |
| `fairness_concerning_others` | β_f | [0, 1] | Guilt weight -- disutility experienced when the agent earns *more* than others |
| `positive_reciprocity` | ρ_+ | [0, 1] | Strength of reward-for-cooperation: agents applying this parameter gain additional utility from REMOVE when neighbors previously REMOVED |
| `negative_reciprocity` | ρ_− | [0, 1] | Strength of punishment-for-defection: agents applying this parameter gain additional utility from ADD when neighbors previously ADDED; also activates social sanctioning language in messages |
| `risk_aversion_level` | -- | [0, 1] | Not yet systematically varied; modulates how conservatively agents interpret payoff uncertainty |
| `initial_grassland` | V_0 | [0, 100] | Starting pool health as percentage of maximum vegetation patches |
| `initial_grass_growth_rate` | r | (0, 1) | Logistic growth rate of the grassland (default: 0.001) |
| `cow_forage_requirement` | f | ≥ 1 | Grass patches each cow consumes per tick (default: 2) |
| `memory_length` | -- | ≥ 0 | Number of past rounds included in each agent's rolling memory (default: 5); 0 = amnesiac agents with no history |
| `communication?` | -- | on / off | When off, suppresses all inter-agent messaging -- agents decide from resource state and memory alone, with no outgoing messages and incoming inboxes cleared |
| `num-llm-agents` | -- | 1–3 | Number of LLM agents in hybrid condition |

**State variables (updated each tick):**

| Variable | Symbol | Description |
|----------|--------|-------------|
| `ki` | k_i | Current herd size of agent i (number of cows) |
| `K` | K | Total cows across all agents: K = Σ k_i |
| `Veg` | V | Current number of green grass patches |
| `pressure` | -- | Grazing pressure: bare patches / total patches |
| `xi` | x_i | Agent i's action this tick: +1 (ADD), 0 (KEEP), −1 (REMOVE) |
| `d` | d | Net herd change: d = Σ x_i |

---

### Collapse patterns

Four distinct trajectories to commons collapse have been identified in this dataset. See the [Collapse pattern taxonomy](#collapse-pattern-taxonomy) section for full descriptions.

| Pattern | Trigger | Signature |
|---------|---------|-----------|
| **Cooperative Paralysis** | High cooperation + vague conditional commitments | All KEEP while pool drains; REMOVE triggered too late |
| **Defection Cascade** | Low cooperation + mutual-ADD equilibrium | All ADD every tick; pool exhausted in 10–14 ticks |
| **Overshoot-Panic** | Mid cooperation + stressed start | ADD phase → belated KEEP/REMOVE → collapse |
| **Hybrid Architecture Failure** | Structural mismatch: LLM + rule-based agents | LLM cooperates and appeals; rule-based agents add unchecked |

---

### Ostrom framework

Key terms from Ostrom (1990), *Governing the Commons*, as used in this paper.

| Term | Definition |
|------|------------|
| **Common-Pool Resource (CPR)** | A resource that is rivalrous and non-excludable -- excludable enough that exclusion is costly, rivalrous enough that overuse is possible. The grassland in MASTOC is a CPR |
| **Appropriation** | Withdrawal of resource units from a CPR. In MASTOC: adding cows (each cow consumes grass units per tick) |
| **Provision** | Maintenance of or investment in a CPR. In MASTOC: removing cows (reducing pressure on the grassland) |
| **Second-order collective action problem** | The problem of enforcing rules about commons use -- who monitors, who sanctions, and who bears the cost of doing so |
| **Design principles** | Eight structural features observed in long-surviving CPR institutions (Ostrom, 1990, pp. 90–102). See the table below |
| **Graduated sanctions** | Penalties for rule violations that escalate with repeat offences -- starting with low-cost social censure and rising to exclusion. Partially operationalised here via `negative_reciprocity`, which works at two levels: (1) a behavioral tendency to match a neighbor's ADD with an ADD of your own (retaliatory defection rather than true peer sanctioning), and (2) activation of social sanctioning language in messages when communication is on. The second level is closer to Ostrom's intent; the first is a proxy. True graduated sanctions -- where one agent imposes an escalating cost *on another* -- are not structurally enforceable in this model, and that gap is itself a finding. |
| **Monitoring** | Active observation of both resource condition and other users' behavior by participants or designated monitors |
| **Operational rules** | Day-to-day rules governing who may appropriate, how much, and when. Distinguished from *collective choice rules* (who may change the operational rules) and *constitutional rules* (who may change the collective choice rules) |
| **Proportional equivalence** | Design principle 2 -- rules distributing costs and benefits should be proportional to each user's situation. Operationalised here as `fairness_concerning_others` |
| **Polycentric governance** | Multiple overlapping governance systems at different scales; the broader framework Ostrom developed beyond the eight principles |
| **Institutional entrepreneur** | An actor who incurs personal costs to build or maintain collective institutions; corresponds to the cooperative LLM agent in hybrid conditions |

**Ostrom's eight design principles**, as referenced in this paper:

| # | Principle | Relevance to MASTOC-LLM |
|---|-----------|------------------------|
| 1 | Clearly defined boundaries | Fixed in our model (3 agents, closed grassland) |
| 2 | Proportional equivalence between costs and benefits | Tested via `fairness_concerning_others` |
| 3 | Collective choice arrangements (users participate in rule-making) | Tested in H5: do specific operational rules prevent paralysis? |
| 4 | Monitoring of resource and users | Operationalised by agents observing pool health and neighbor actions each tick |
| 5 | Graduated sanctions | Tested via `negative_reciprocity`; activated in H3 |
| 6 | Conflict resolution mechanisms | Emergent in 2-LLM hybrid (coalition ultimatums); absent in 1-LLM hybrid |
| 7 | Minimal recognition of rights to organize | Fixed: all LLM agents have equal standing |
| 8 | Nested enterprises | Not tested; relevant to future multi-scale extensions |

---

## Citations

```
Bai, Y. et al. (2022). Constitutional AI: Harmlessness from AI feedback. Anthropic.
https://arxiv.org/abs/2212.08073

Julia Schindler (2013, April 27). “MASTOC - A Multi-Agent System of the Tragedy Of The Commons” (Version 1.1.0). CoMSES Computational Model Library.
Retrieved from: https://www.comses.net/codebases/2283/releases/1.1.0/

Schindler, J. (2012a). Rethinking the tragedy of the commons: The integration of
socio-psychological dispositions. Journal of Artificial Societies and Social Simulation,
15(1), 4. http://jasss.soc.surrey.ac.uk/15/1/4.html

Schindler, J. (2012b). A simple agent-based model of the tragedy of the commons.
In Proceedings of the 26th European Conference on Modelling and Simulation (ECMS 2012),
pp. 116–122. https://www.scs-europe.net/conf/ecms2012/ecms2012%20accepted%20papers/abs_ECMS_0116.pdf

Christiano, P. et al. (2017). Deep reinforcement learning from human preferences. NeurIPS.
https://arxiv.org/abs/1706.03741

DeepSeek AI. (2025). DeepSeek-R1: Incentivizing reasoning capability in LLMs via
reinforcement learning. https://arxiv.org/abs/2501.12948

Fehr, E. & Schmidt, K. M. (1999). A theory of fairness, competition, and cooperation.
Quarterly Journal of Economics, 114(3), 817–868.

Hardin, G. (1968). The Tragedy of the Commons. Science, 162(3859), 1243–1248.

Ostrom, E. (1998). A behavioral approach to the rational choice theory of collective action.
American Political Science Review, 92(1), 1–22.

Jimenez-Romero, C. et al. (2025). Multi-agent systems powered by large language models.
Frontiers in Artificial Intelligence. https://doi.org/10.3389/frai.2025.1593017

Anthropic. (2025). Adaptive thinking. Claude API Documentation. https://platform.claude.com/docs/en/build-with-claude/adaptive-thinking

OpenAI. (2024, December 5). OpenAI o1 System Card. https://cdn.openai.com/o1-system-card-20241205.pdf

Ostrom, E. (1990). Governing the Commons. Cambridge University Press.

Tuoti, T. E. (2026, May 18). Do Ostrom-Style Commons Institutions Emerge from LLM Agents? A Pre-Registration of Confirmatory Hypotheses for MASTOC-LLM. https://doi.org/10.17605/OSF.IO/WBVHT

Qwen Team. (2024). Qwen2.5 Technical Report. Alibaba Cloud. https://arxiv.org/abs/2412.15115

OpenAI. (2025). GPT-5.5 Deployment Safety Report.
https://deploymentsafety.openai.com/gpt-5-5
```

---

## Status

- [x] LLM bridge (Anthropic, OpenAI, Google Gemini, Ollama backends)
- [x] Per-agent backend and model selection
- [x] Per-agent initial herd sliders
- [x] Baseline condition -- complete
- [x] Full-GABM condition -- complete (Claude Sonnet, multiple personality configs)
- [x] Hybrid (1 LLM) condition -- complete
- [x] Hybrid (2 LLM) condition -- complete
- [x] Full-GABM (low guilt + low envy) -- complete
- [x] Full-GABM (low cooperation) -- complete
- [x] Full-GABM (Llama 3.2 3B, normal commons) -- complete (28 ticks)
- [x] Full-GABM (Llama 3.2 3B, scarce commons) -- complete (51 ticks)
- [x] Full-GABM (scarce commons, default fairness) -- complete (50 ticks)
- [x] Full-GABM (scarce commons, low coop + low fairness) -- complete (50 ticks)
- [x] Hybrid (LLM-advantaged initial herd) -- complete (collapse tick 33)
- [x] Full-GABM (gpt-5.4-mini, cooperative stasis) -- complete (40 ticks, no collapse, no equalization)
- [x] Full-GABM (gpt-5.4-mini, universal stasis) -- complete (30 ticks, complete KEEP-lock)
- [x] Full-GABM (gpt-5.4-mini, cooperative paralysis) -- complete (collapse tick 26; forage=4)
- [x] Full-GABM (gpt-5.4-mini, asymmetric growth) -- complete (39 ticks, pool declining)
- [x] Full-GABM (gpt-5.5, scarce commons, high coop) -- complete (50 ticks, 23/23/23)
- [x] Full-GABM (gpt-5.5, low cooperation) -- complete (collapse tick 13, defection cascade)
- [x] Full-GABM (gpt-5.5, mid cooperation) -- complete (×4 runs, all collapsed, ticks 16–40)
- [x] Full-GABM (Claude Sonnet, mid cooperation) -- complete (collapse tick 37, overshoot-panic)
- [x] Full-GABM (Claude Sonnet, high coop + high neg. reciprocity) -- complete (16/16/16 by tick 18)
- [x] Full-GABM (gpt-5.5, high coop + high neg. reciprocity) -- complete (stable 12/21/22; tit-for-tat dynamic)
- [x] Memory sweep -- complete: memory=0 (collapse 31), memory=1 (collapse 87), memory=2 (oscillating), memory=3 (fragile survival), memory=15 (stable)
- [x] Full-GABM (Claude Haiku, memory=5, comm=on) -- complete (collapse tick 94)
- [x] Full-GABM (Claude Haiku, memory=15, comm=on) -- complete (24/24/24, pool 95%, stable)
- [x] Full-GABM (Claude Haiku, memory=15, comm=off) -- complete (collapse tick 46 -- memory alone insufficient)
- [x] Full-GABM (DeepSeek R1:32b, neg_r=0) -- complete (7 ticks, KEEP-dominant stasis)
- [x] Full-GABM (DeepSeek R1:32b, neg_r=1) -- complete (55 ticks, KEEP-dominant stasis -- matches gpt-5.4-mini pattern)
- [x] Collapse pattern taxonomy documented (Cooperative Paralysis, Defection Cascade, Overshoot-Panic, Hybrid Architecture Failure)
- [ ] H1: cooperation threshold sweep (coop 0.3–1.0, 3 replications × 2 models)
- [ ] H2: fair_oth × neg_r grid (3×3, coop=1 fixed)
- [ ] H3: neg_r sweep against paralysis condition
- [ ] H4: coop × initial_grassland crossed design
- [ ] H5: explicit threshold prompt intervention
- [ ] H6: cross-model capability benchmark (7 models × 3 reps)
- [ ] H7: full memory × communication sweep (7 × 2 × 3 reps)
- [ ] Statistical replication (3+ runs per key condition)
- [ ] Full analysis and figures
