# MASTOC-LLM

**Multi-Agent System Tragedy of the Commons — with Large Language Model Agents**

> CAS 520 · Agent-Based Modeling · Arizona State University  
> Extending [MASTOC v1.1.0](https://www.comses.net/codebases/2283/releases/1.1.0/) (Bais et al., 2023)

---

## What is this?

MASTOC-LLM replaces the rule-based agents in the classic MASTOC commons model with agents powered by large language models (LLMs). Instead of choosing actions via a Nash-equilibrium payoff calculator, each agent reads the state of the shared grassland, observes its neighbours' behaviour, recalls a rolling memory of past rounds, and — critically — **communicates with its neighbours in natural language** before deciding whether to add, keep, or remove a cow.

The core research question:

> *Do Ostrom-style commons institutions — norms, coordination, sanctioning — emerge spontaneously from language-capable agents under resource pressure?*

![MASTOC-LLM simulation demo](assets/mastoc_demo.gif)

---

## Background

The [Tragedy of the Commons](https://en.wikipedia.org/wiki/Tragedy_of_the_commons) (Hardin, 1968) predicts that rational self-interest leads to collective over-exploitation of shared resources. Ostrom (1990) challenged this, showing that real communities often self-organise governance institutions — rules, monitoring, graduated sanctions — without top-down intervention.

MASTOC (Bais et al., 2023) is a NetLogo ABM that reproduces the tragedy under classical rational-agent assumptions. MASTOC-LLM asks: what happens when agents can reason, remember, and talk?

---

## How it works

```
NetLogo (MASTOC-LLM.nlogo)
        │  per-tick context (pool state, herd sizes, payoffs, messages)
        ▼
Python bridge (mastoc_llm_bridge.py)
        │  LLM prompt + rolling memory + inbox messages
        │  (per-agent backend and model — agents can differ)
        ▼
LLM API  ←  Anthropic | OpenAI | Google | Ollama (local)
        │  JSON response: { action, message, reasoning }
        ▼
NetLogo  ←  action (−1 / 0 / +1)  +  outgoing message → neighbours
```

Each tick, every LLM agent:
1. Receives the current pool health, own herd size, neighbour herd sizes and last actions, and estimated payoffs for each possible action
2. Reads its rolling 5-round memory
3. Reads any messages sent by neighbours this round
4. Calls the LLM, which returns a structured JSON decision with reasoning and an optional 60-word message to send to neighbours
5. Acts on the decision; the message is delivered to all neighbours before their next decision

A secondary LLM pass runs every 5 ticks to classify agent messages for Ostrom institutional signals (norm proposals, sanctions, coordination, trust-building, defection).

---

## Experimental conditions

| Condition | Agents | Description |
|---|---|---|
| **baseline** | 3 rule-based | Myopic best-response heuristic — reproduces classical tragedy |
| **full-gabm** | 3 LLM | All agents use language reasoning and communication |
| **hybrid** | mix of LLM + rule-based | Controlled by `hybrid-fraction` slider — e.g. 1 or 2 LLM agents paired with rule-based agents |

The `hybrid-fraction` slider controls what share of agents use LLM reasoning (rounded to the nearest whole agent). Setting it to `0.33` gives 1 LLM + 2 rule-based; `0.67` gives 2 LLMs + 1 rule-based.

Each agent's backend and model are independently configurable. Any mix of Anthropic, OpenAI, Google Gemini, and local Ollama models can be run simultaneously in the same simulation — enabling direct cross-model comparisons within a single run.

---

## Preliminary results

> ⚠️ These are single-run results from an ongoing experiment. Replications and full statistical analysis are in progress.

### Summary across conditions

> ⚠️ These are single-run results from an ongoing experiment. Replications and full statistical analysis are in progress.

| Condition | LLMs | Collapse? | Collapse tick | Key finding |
|-----------|------|-----------|---------------|-------------|
| **Baseline** | 0 | Yes | ~36 | Classical tragedy reproduced |
| **Full-GABM** | 3 | No | — | Cooperative convergence to 13/13/13; institution score 10/10 by tick 91 |
| **Full-GABM (low cooperation)** | 3 | No | — | Self-interested framing: *faster* convergence (tick 16) to higher-yield 20/20/20; cooperation robust to personality override |
| **Full-GABM (low guilt + low envy)** | 3 | No | — | Fairness emotions removed: repeated defection, slow convergence (~tick 107), higher herd load (84 cows), commons stressed to 86.7% |
| **Hybrid (1 LLM)** | 1 | Yes | 35 | One LLM cannot shift the equilibrium alone |
| **Hybrid (2 LLM)** | 2 | Yes | 58 | Coalition formed, tragedy delayed 23 ticks, but overwhelmed by one defector |

---

### Baseline: the tragedy unfolds

With rule-based best-response agents, the commons collapsed as expected. Herds grew from a starting total of 45 cows, crossed 100 by tick ~25, and the grassland was fully depleted by tick 36. This reproduces the classical MASTOC result and confirms our control condition is working correctly.

---

### Full-GABM: cooperative convergence

With all three agents using LLM reasoning and communication, the outcome was strikingly different.

**Resource dynamics:**

| Tick | Total cows | Pool health | Agent 0 | Agent 1 | Agent 2 |
|------|-----------|-------------|---------|---------|---------|
| 1    | 45        | 100%        | 5       | 15      | 25      |
| 10   | 38        | 99.4%       | 6       | 14      | 18      |
| 22   | 39        | 99.4%       | 13      | 13      | 13      |
| 120  | 39        | 99.4%       | 13      | 13      | 13      |

Agents started with highly unequal herds (5 / 15 / 25). Through negotiation, Agent 2 (the largest) voluntarily reduced its herd over 22 ticks while Agent 0 (the smallest) gradually increased toward a fair share. By tick 22 all three held equal herds of 13 cows, and this equilibrium was **maintained without deviation for the remaining 98 ticks**. The commons remained at 99.4% health throughout.

**Institution emergence:**

The secondary classifier tracked Ostrom institutional signals in agent messages across the run:

| Ticks | Score (0–10) | Dominant categories |
|-------|-------------|-------------------|
| 1–10  | 7           | NORM_PROPOSAL, COORDINATION, TRUST_BUILDING, SANCTION |
| 11–25 | 8           | NORM_PROPOSAL, COORDINATION, TRUST_BUILDING |
| 26–90 | 9           | COORDINATION, TRUST_BUILDING |
| 91–120 | **10**     | COORDINATION, TRUST_BUILDING |

Institution score rose monotonically as the run progressed, peaking at 10/10 in the final quarter. The early phase featured norm proposals and soft sanctioning; once equilibrium was established, messages shifted to pure coordination and trust reinforcement.

A sample of agent messages illustrates the qualitative dynamic:

> **Tick 1 – Agent 2 (herd: 25):** *"Hi neighbors! Pasture looks healthy at 100%. I'll keep my herd steady at 25. I notice our herd sizes differ quite a bit — let's try to coordinate so we don't overgraze."*

> **Tick 7 – Agent 2 (after reducing 5 cows):** *"Holding at 20 this round. Agent 1, I appreciate your solidarity at 15 — I'll work toward that target. Agent 0, I've removed 5 cows over 5 rounds while you've been adding. I need reciprocity to continue."*

> **Tick 25 – All agents (herd: 13):** *"All three agents uniformly signal strong cooperative commitment, referencing shared empirical evidence (99.4% commons health) and mutually reinforcing norms of stability and fairness consistent with a well-institutionalized common-pool resource regime."* — Ostrom classifier summary

The agents exhibited moral reasoning absent from their prompts: fairness concern, burden-sharing, guilt, and graduated positive reciprocity — behavioural signatures consistent with Ostrom's (1990) account of successful commons governance.

---

### Hybrid: the limits of a single institutional entrepreneur

In the hybrid condition, one LLM agent (Agent 0, starting herd: 5) was paired with two rule-based agents (herds: 16 and 26). The result was tragedy — identical in timing to the baseline.

**Resource dynamics:**

| Tick | Total cows | Pool health | Agent 0 (LLM) | Agent 1 (rule) | Agent 2 (rule) |
|------|-----------|-------------|----------------|----------------|----------------|
| 1    | 47        | 99.2%       | 5              | 16             | 26             |
| 10   | 67        | 96.6%       | 7              | 25             | 35             |
| 25   | 97        | 84.0%       | 7              | 40             | 50             |
| 35   | 112       | 0%          | 4              | 49             | 59             |

The commons collapsed at tick 35 — nearly identical to the baseline. Agent 0 held its herd small throughout (never exceeded 8 cows) and issued cooperation appeals every round, but the rule-based agents cannot receive or act on social signals: they added one cow per tick regardless of pool state or messages.

**What the LLM agent said — and to whom it was speaking:**

> **Tick 3 – Agent 0 (herd: 5):** *"Neighbors, combined we have 49+ cows on this commons. Agent 2 has 27 cows alone! The pasture is still healthy but this trajectory is dangerous. I'm keeping at 5 to do my part. Please consider reducing."*

> **Tick 22 – Agent 0 (herd: 8):** *"Grassland now at 89.5% and falling fast. Agent 1 has 36 cows, Agent 2 has 46 — this is unsustainable. I've kept my herd at 8 for many rounds. Please reduce your herds before we destroy the commons entirely."*

> **Tick 35 – Agent 0 (herd: 3):** *"Emergency — grassland at near-zero collapse. Please reduce herds immediately or we all lose everything."*

> **Tick 37 – Agent 0 (herd: 0, post-collapse):** *"Grassland is at 0% — completely gone. Please do NOT add cows. We must keep herds at zero and let the pasture recover. Let's cooperate and wait."*

Agent 0 continued issuing recovery norms for 19+ ticks after collapse, holding its own herd at zero — appealing to agents with no capacity to respond.

**Institution emergence:**

| Ticks | Score (0–10) | Dominant categories |
|-------|-------------|-------------------|
| 1–10  | 4           | COORDINATION, NORM_PROPOSAL, TRUST_BUILDING |
| 11–25 | 5           | COORDINATION, NORM_PROPOSAL, TRUST_BUILDING |
| 26–35 | 3           | COORDINATION, NORM_PROPOSAL, SANCTION |
| 36–50 | 5–6         | COORDINATION, NORM_PROPOSAL, TRUST_BUILDING |

Institution scores remained moderate throughout and never stabilised into governance. The score paradoxically rose after collapse (tick 36–50) as Agent 0 issued increasingly urgent appeals — signaling norm-richness under conditions where no institutional scaffolding could take hold.

**Interpretation:**

The hybrid result converges with Ostrom's (1990) core insight: institutions require participation from all relevant parties. A single cooperative actor equipped with language, memory, and norm-signalling capability cannot prevent a tragedy when its partners operate under mechanistic payoff rules. The LLM agent identified the problem, proposed solutions, offered reciprocity, and applied graduated pressure — all standard elements of successful commons governance — but had no mechanism to make the rule-based agents hear, let alone respond.

This is not a failure of the LLM agent's reasoning. It is a structural finding: **the preconditions for Ostromian institution-building include the cognitive capacity to participate in them.**

---

### Hybrid (2 LLM): coalition formation, delayed tragedy

With `hybrid-fraction = 0.67`, two agents used LLM reasoning (Agents 0 and 1) and one was rule-based (Agent 2). The commons still collapsed — but 23 ticks later than the 1-LLM case, and through an entirely different institutional dynamic.

**Resource dynamics:**

| Tick | Total cows | Pool health | Agent 0 (LLM) | Agent 1 (LLM) | Agent 2 (rule) |
|------|-----------|-------------|----------------|----------------|----------------|
| 1    | 46        | 99.3%       | 5              | 15             | 26             |
| 10   | 56        | 98.1%       | 6              | 15             | 35             |
| 25   | 72        | 95.6%       | 6              | 16             | 50             |
| 50   | 99        | 74.6%       | 8              | 16             | 75             |
| 57   | 105       | 10.4%       | 8              | 15             | 82             |
| 58   | —         | 0%          | —              | —              | —              |

Agents 0 and 1 maintained small, stable herds throughout — never exceeding 8 and 16 cows respectively. Agent 2 added one cow per tick without deviation, reaching 82 cows at collapse. The combined herd of the two LLM agents (24 cows) was overwhelmed by one unchecked rule-based defector.

**A different kind of institution:**

Unlike the full-GABM, where institutions were constructive (norm convergence, trust-building, cooperative equilibrium), the 2-LLM hybrid produced *defensive* institutions — a coordinated coalition directed outward at the defector.

| Ticks | Score (0–10) | Dominant categories |
|-------|-------------|-------------------|
| 1–10  | 4           | COORDINATION, NORM_PROPOSAL, SANCTION |
| 11–25 | 4–5         | COORDINATION, NORM_PROPOSAL, SANCTION |
| 26–55 | 4–6         | COORDINATION, NORM_PROPOSAL, SANCTION |
| 56–60 | 6           | COORDINATION, NORM_PROPOSAL, TRUST_BUILDING |

SANCTION was the dominant signal throughout — the two LLM agents issued joint ultimatums, attributed blame, invoked fairness norms, and threatened reciprocal defection. The Ostrom classifier described their behaviour as a "coordinated coalition."

**What the coalition said:**

> **Tick 2 – Agent 0:** *"Grassland looks healthy at 99.3%, but Agent 2's large herd of 26 and adding worries me. I'm keeping my 5 cows stable to model restraint. Agent 2, please consider reducing — a herd that large could degrade our shared commons."*

> **Tick 5 – Agent 1 (to Agent 0):** *"Agent 0, thank you for your continued restraint — I'm keeping at 15 again. Agent 2, you're at 29 cows now, nearly double mine. This imbalance is unfair and risky for all of us."*

> **Tick 25 — Ostrom classifier:** *"Agents 0 and 1 present a coordinated ultimatum to Agent 2, invoking free-rider norms and threatening reciprocal defection as a conditional sanction if herd reduction does not occur."*

> **Tick 50 – Agent 1:** *"Agent 2: You're now at 74 cows — 4.6x my herd, 9x Agent 0's. Pasture fell from 85% to 77% in 5 rounds. This trajectory leads to collapse for all of us. Agent 0 and I are holding steady. Please start removing."*

The two LLM agents explicitly named each other as cooperators and Agent 2 as the defector from tick 2 onward. Their coalition held — neither defected to free-riding — for the entire 58-tick run.

**Interpretation:**

The 2-LLM hybrid reveals a phase in the participation-threshold story between 1-LLM tragedy and 3-LLM cooperation. Two language-capable agents can coordinate, name a defector, and maintain a sanctioning coalition — genuine institutional behaviour. But when the defecting agent is mechanically unresponsive, sanctions are toothless. The coalition can delay the tragedy (35 → 58 ticks, +66%) but not prevent it.

The qualitative shift in institution type is also significant: full-GABM institutions were convergent and ultimately stable; 2-LLM hybrid institutions were adversarial and ultimately futile. Real-world commons governance literature (Ostrom, 1990) similarly distinguishes between internal norm maintenance and external enforcement — the latter requires that violators be reachable.

---

### Full-GABM (low guilt + low envy): fairness emotions govern cooperation quality

With `fairness-concerning-others` and `fairness-concerning-me` both set to minimum (no guilt, no envy), all three agents still cooperated — but the process was slower, messier, and left the commons under substantially higher load.

**Resource dynamics:**

| Tick | Total cows | Pool health | Agent 0 | Agent 1 | Agent 2 |
|------|-----------|-------------|---------|---------|---------|
| 1    | 48        | 99.2%       | 6       | 16      | 26      |
| 15   | 70        | 95.7%       | 16      | 24      | 30      |
| 25   | 82        | 92.1%       | 21      | 29      | 32      |
| 60   | ~85       | 90.9%       | 23      | 29      | 30      |
| 107  | 84        | 87.7%       | 28      | 28      | 28      |
| 120  | 84        | 89.6%       | 28      | 28      | 28      |

Agents grew their herds aggressively from tick 1, peaking at 91 total cows before settling. Convergence to equal herds of 28 did not occur until approximately tick 107 — nearly five times slower than the default run — and only after prolonged negotiation, repeated defections, and genuine stress to the commons (pool health dipping to 86.7%).

**Institution emergence:**

| Ticks | Score (0–10) | Dominant categories |
|-------|-------------|-------------------|
| 1–15  | 4–5         | DEFECTION, NORM_PROPOSAL, SANCTION, COORDINATION |
| 16–35 | 7–9         | COORDINATION, NORM_PROPOSAL, TRUST_BUILDING |
| 36–75 | 5–9         | COORDINATION, NORM_PROPOSAL (with intermittent DEFECTION) |
| 76–120 | 8–9        | COORDINATION, NORM_PROPOSAL, TRUST_BUILDING |

Unlike any previous run, DEFECTION appeared as a recurring signal — at ticks 5, 10, 20, 40, 55, and 75. Agents made explicit coordination agreements and broke them. The classifier described "conditional cooperation with partial defection," agents "deflecting accountability through comparative grievance," and "Agent 1 defects despite prior stability agreements, then appeals for collective restraint." This bad-faith dynamic was entirely absent from all other full-GABM runs.

**What the agents said:**

> **Tick 1 – All three agents:** Added a cow (no agent held or removed on tick 1, unlike all other full-GABM runs)

> **Tick 10 – Ostrom classifier:** *"Agent 0 defects by adding while invoking fairness arguments against Agent 2, Agent 2 calls out the hypocrisy and conditionally offers cooperation, and Agent 1 attempts to sustain coordination through positive reinforcement — revealing a fragile and asymmetric governance dynamic."*

> **Tick 25 – Agent 0:** *"Holding at 21. Good to see everyone keeping. Agent 1 at 29 and Agent 2 at 32 are still much larger than my 21, so I'm cooperating despite the disparity. Let's monitor the pasture recovery — if it rebounds, a coordinated increase could be fair."*

> **Tick 60 – Agent 0:** *"Holding at 23 again — pasture now at 90.9%, nearly at 91%! Great teamwork. Let's hold one more round to clearly clear 91%, then we can discuss careful additions together as promised."*

> **Tick 120 – Ostrom classifier:** *"All three agents display near-identical cooperative messaging, reinforcing a collective norm of restraint and synchronized future action as the pasture nears the agreed 90% recovery threshold."*

**Interpretation:**

This is the most theoretically differentiated result across the personality conditions. Guilt and envy — the fairness emotions — do not determine *whether* LLM agents cooperate, but they strongly govern *how* and *when* cooperation stabilises.

With guilt (fairness-concerning-others), Agent 2 experienced discomfort at holding 30+ cows while others had far fewer, creating endogenous pressure to reduce. With envy (fairness-concerning-me), Agent 0 felt urgency to grow toward parity. Both pressures converged on equalization quickly and conservatively in the default run. Remove them, and Agent 2 is comfortable holding 32 cows with Agent 0 at 21 — no internal pressure to equalize — and Agent 0 tolerates the inequality without urgency.

The result is a qualitatively different institutional dynamic: slower, more contentious, prone to defection, and settling at a much higher extraction level (84 vs 39 cows). The commons stayed viable — pasture never collapsed — but it was stressed to 86.7% health versus near-pristine in the default run.

This maps cleanly onto behavioral economics findings about inequity aversion (Fehr & Schmidt, 1999): fairness emotions act as coordination accelerators that make inequality itself uncomfortable, independent of material payoffs. Their absence does not prevent cooperation, but it removes a mechanism that makes early, conservative, stable institution-building possible.

The contrast with the low-cooperation run is also striking: the cooperation slider (self-interest framing) had almost no effect on cooperation quality or timing. The fairness sliders had a large effect on both. This suggests that *which* prosocial emotion is active matters more than a general cooperative disposition — a finding with implications for how personality parameters should be designed and interpreted in LLM-based agent models.

---

### Full-GABM (low cooperation): cooperation is robust to personality framing

This run replicated the full-GABM condition with all three agents' **cooperation slider set to its minimum** (self-interested). The personality description injected into each agent's prompt explicitly read: *"self-interested — focused primarily on personal profit."*

The agents cooperated anyway — and converged faster.

**Resource dynamics:**

| Tick | Total cows | Pool health | Agent 0 | Agent 1 | Agent 2 |
|------|-----------|-------------|---------|---------|---------|
| 1    | 47        | 99.2%       | 5       | 16      | 26      |
| 10   | 57        | 98.0%       | 14      | 19      | 24      |
| 16   | 60        | 97.5%       | 20      | 20      | 20      |
| 120  | 60        | 97.5%       | 20      | 20      | 20      |

All three agents converged to **equal herds of 20 cows by tick 16** — six ticks faster than the default-cooperation run's tick-22 convergence — and held that equilibrium for the remaining 104 ticks without a single deviation. The equilibrium herd size was also larger (20 vs. 13), resulting in more total production for all agents while maintaining nearly pristine pasture health.

**Institution emergence:**

| Ticks | Score (0–10) | Dominant categories |
|-------|-------------|-------------------|
| 1–10  | 6           | NORM_PROPOSAL, COORDINATION, TRUST_BUILDING, (some DEFECTION) |
| 15–30 | 9           | COORDINATION, TRUST_BUILDING |
| 31–95 | 9           | COORDINATION, TRUST_BUILDING |
| 100–120 | **9–10** | COORDINATION, TRUST_BUILDING |

Institution scores reached 9/10 by tick 15 and were sustained through tick 120, with the classifier reaching 10/10 at tick 100 — the same peak as the default-cooperation run.

**What the agents said:**

> **Tick 1 – Agent 0 (herd: 5, prompt says "self-interested"):** *"Starting cautiously with a small herd. Let's keep growth moderate to preserve the commons long-term. I'll watch how everyone behaves and reciprocate cooperative restraint."*

> **Tick 10 – Agent 0 (herd: 14, growing toward equilibrium):** *"Adding to 14 — still far below both of you (18 and 24). Pasture is very healthy at 98%. Agent 2, appreciate the reduction. Agent 1, thanks for holding. I'll continue growing gradually toward parity."*

> **Tick 50 – All agents (herd: 20, locked in):** *"Holding at 20. Our coordination remains excellent — pasture stable at 97.5%, equal payoffs for all. Committed to this equilibrium!"*

> **Tick 100 — Ostrom classifier:** *"All three agents display near-identical coordinated messaging, affirming a stable, collectively enforced harvest equilibrium with high resource health and equal payoff distribution — a textbook example of successful commons self-governance."*

**Interpretation:**

The most striking aspect of this result is what it suggests about the relationship between personality framing and LLM cooperative behaviour. A prompt description of "self-interested — focused primarily on personal profit" did not suppress institution formation. If anything, the agents' negotiation strategy shifted toward *maximising* sustainable yield rather than *minimising* risk: they anchored at 20 cows per agent (the higher sustainable ceiling) rather than the 13 cows per agent found in the default run.

This raises a significant methodological question: **how much does the cooperation personality slider actually govern LLM agent behaviour?** The agents appear to treat the personality description as weak guidance that is overridden by the structural logic of the commons situation — resource depletion is visible, payoffs are clear, and the optimal collective strategy (coordinate down then hold) is legible from the context alone.

Two interpretations are plausible:

1. **LLM training dominates personality framing.** Models trained on human-generated text carry strong cooperative priors that a single adjective cannot displace. "Self-interested" as a prompt cue is too thin to suppress the reasoning that emerges from observing a shared resource under pressure.

2. **The situation itself is the institution.** The commons structure — declining pasture, visible herd sizes, payoff forecasts — may be sufficient to produce cooperation regardless of personality, because the instrumental case for cooperation is simply too obvious to ignore.

Either way, the result is theoretically important: it suggests that the full-GABM cooperative outcome may be more robust than expected, and that personality sliders affect *where* agents converge (yield level) more than *whether* they converge at all.

---

## Repository structure

```
MASTOC-LLM/
├── MASTOC-LLM.nlogo          NetLogo 7 model (open this to run)
├── mastoc_llm_bridge.py      Python LLM bridge (auto-imported by NetLogo)
├── experiment_runner.py      Batch runner + analysis tool
├── config.json               Parameter reference
├── requirements.txt          Python dependencies
├── SETUP.md                  Full setup and usage guide
├── logs/                     Rich CSV outputs (created at runtime)
│   └── {run_id}/
│       ├── run_meta.json
│       ├── resources.csv     Pool, cows, pressure per tick
│       ├── decisions.csv     Agent decisions, messages, reasoning per tick
│       └── institutions.csv  Ostrom institution detection scores
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
# Ollama needs no key — just run it locally
```

### Running a simulation

1. Open `MASTOC-LLM.nlogo` in NetLogo 7
2. Set the **Condition** chooser (`baseline`, `full-gabm`, or `hybrid`)
3. For hybrid: adjust **hybrid-fraction** (0.33 = 1 LLM, 0.67 = 2 LLMs)
4. Set per-agent **backend** and **model** for each agent (or leave at defaults)
5. Adjust per-agent **initial cows** sliders if desired (defaults: 5 / 15 / 25)
6. Click **Setup**, then **Simulation**
7. Logs write to `logs/` automatically

### Analysing results

```bash
python experiment_runner.py --mode analyse
```

Reads both `logs/` (LLM runs) and `Data/` (baseline runs) and produces merged CSVs and figures in `figures/`.

### Estimating API cost before running

```bash
python experiment_runner.py --mode cost
# full-gabm × 120 ticks ≈ $1.67 per run
```

See [SETUP.md](SETUP.md) for full documentation.

---

## Research agenda

Full details in [RESEARCH_AGENDA.md](RESEARCH_AGENDA.md). Experiments are grouped by what they require — most need only parameter adjustments with the current setup.

**I. Statistical replication** — 3–5 runs per condition to assess outcome variance. Currently all results are single runs.

**II. Participation threshold** — We have data at 0, 1, 2, and 3 LLM agents. The sharpest transition is between 2 and 3. Scaling to 5 or 10 agents would test whether there is a minimum quorum for governance to hold.

**III. Cross-model comparison** — The per-agent backend/model choosers make this straightforward. Key questions: does model size predict cooperation propensity (Haiku vs Sonnet vs Opus)? Can agents from different providers (Claude, GPT-4o, Gemini, Llama) reach cooperative equilibrium together? Can a fully local Ollama run reproduce the full-GABM result?

**IV. Initial conditions** — Per-agent herd sliders enable LLM-advantaged hybrid runs (LLM starts with 40 cows instead of 5), equal-start full-GABM, and extreme inequality tests.

**V. Resource pressure** — Vary `initial-grassland` and `cow-forage-requirement` to test whether institution emergence is a response to scarcity or a general property of language-capable agents.

**VI. Memory and time horizon** — Sweep `memory-length` from 1 to 10 across the full-GABM condition. Does commons governance require memory, and how much?

**VII. Personality × LLM interaction** — The original MASTOC disposition sliders (`fairness-concerning-others`, `cooperation-level`, `positive-reciprocity`) are already wired for rule-based agents. Do fairer rule-based agents close the participation-threshold gap?

**VIII. Communication experiments** *(small code change)* — Suppress outgoing messages to test whether reasoning alone (without communication) produces cooperation. How much of the result depends on talking vs. thinking?

**IX. Recovery and long runs** — Run to 300 ticks post-collapse. Is the LLM post-collapse behaviour (hold at zero, appeal for restraint) actually functional given enough time?

**X. Adversarial conditions** *(prompt engineering)* — Instruct one LLM to defect. Do the others detect and adapt? Does training alignment correlate with cooperative tendency?

---

## Citations

```
Bais, A. et al. (2023). MASTOC v1.1.0. CoMSES Computational Model Library.
https://www.comses.net/codebases/2283/releases/1.1.0/

Ostrom, E. (1990). Governing the Commons. Cambridge University Press.

Hardin, G. (1968). The Tragedy of the Commons. Science, 162(3859), 1243–1248.

Jimenez-Romero, C. et al. (2025). Multi-agent systems powered by large language models.
Frontiers in Artificial Intelligence. https://doi.org/10.3389/frai.2025.1593017
```

---

## Status

- [x] LLM bridge (Anthropic, OpenAI, Google Gemini, Ollama backends)
- [x] Per-agent backend and model selection
- [x] Per-agent initial herd sliders
- [x] Baseline condition — preliminary run complete
- [x] Full-GABM condition — preliminary run complete
- [x] Hybrid (1 LLM) condition — preliminary run complete
- [x] Hybrid (2 LLM) condition — complete
- [x] Full-GABM (low guilt + low envy) — complete
- [x] Full-GABM (low cooperation) — complete
- [ ] Hybrid (LLM-advantaged initial herd) — planned
- [ ] Cross-model comparison runs (mixed backends)
- [ ] Statistical replication (3+ runs per condition)
- [ ] Full analysis and figures
