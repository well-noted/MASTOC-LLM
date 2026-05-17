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

| Condition | Model | LLMs | Collapse? | Collapse tick | Key finding |
|-----------|-------|------|-----------|---------------|-------------|
| **Baseline** | — | 0 | Yes | ~36 | Classical tragedy reproduced |
| **Full-GABM** | Claude Sonnet 4.6| 3 | No | — | Cooperative convergence to 13/13/13; institution score 10/10 by tick 91 |
| **Full-GABM (low cooperation)** | Claude Sonnet 4.6| 3 | No | — | Self-interested framing: *faster* convergence (tick 16) to higher-yield 20/20/20; cooperation robust to personality override |
| **Full-GABM (low guilt + low envy)** | Claude Sonnet 4.6| 3 | No | — | Fairness-parameter prompts zeroed: repeated defection, slow convergence (~tick 107), higher herd load (84 cows), commons stressed to 86.7% |
| **Hybrid (1 LLM)** | Claude Sonnet 4.6| 1 | Yes | 35 | One LLM cannot shift the equilibrium alone |
| **Hybrid (2 LLM)** | Claude Sonnet 4.6| 2 | Yes | 58 | Coalition formed, tragedy delayed 23 ticks, but overwhelmed by one defector |
| **Full-GABM (Llama 3.2 3B)** | Llama 3.2 3B | 3 | No | — | Pool maintained at 99.4% but herds oscillated without convergence; cooperative messaging but no institution formation |
| **Full-GABM (Llama 3.2 3B, scarce commons)** | Llama 3.2 3B | 3 | No | — | Initial grassland 48%: pool recovered 48%→99% by tick 17; herds oscillated without convergence throughout all 51 ticks |
| **Hybrid (LLM-advantaged initial herd)** | Claude Sonnet 4.6 | 1 | Yes | 33 | LLM starts with 40 cows; voluntarily reduces to 25 by collapse; rule-based agents add unchecked; collapse 2 ticks earlier than baseline hybrid |
| **Full-GABM (scarce commons, default fairness)** | Claude Sonnet 4.6 | 3 | No | — | Initial grassland 49%: pool recovered 49%→99% by tick 10; converged to [11,12,13] by tick 30 |
| **Full-GABM (scarce commons, low coop + low fairness)** | Claude Sonnet 4.6 | 3 | No | — | Initial grassland 50%, coop=0.3, fairness=0: recovery to 99% by tick 20; converged to [12,14,16] by tick 30 |
| **Full-GABM (cooperative stasis)** | gpt-5.4-mini | 3 | No | — | coop=1, fair_me=0, fair_oth=1: all KEEP for 36 ticks; herds frozen at starting values (6/15/25); pool stable at 99%+; no equalization |
| **Full-GABM (cooperative paralysis)** | gpt-5.4-mini | 3 | Yes | 26 | coop=1, fair_me=1, fair_oth=0.5: collective KEEP-lock for 24 ticks while pool drained 95.8%→8.5%; REMOVE attempted at tick 25 — one tick too late |
| **Full-GABM (scarce commons, high coop)** | gpt-5.5 | 3 | No | — | coop=1, fair_me=1, fair_oth=0.11, initial pool 48%: immediate cooperative restraint; 23/23/23 by tick 46; pool recovered to 95.9% |
| **Full-GABM (low cooperation)** | gpt-5.5 | 3 | Yes | 13 | coop=0.13: defection cascade — all ADD every tick from tick 1; pool exhausted in 13 ticks from 49.4% |
| **Full-GABM (mid cooperation, x4 replications)** | gpt-5.5 | 3 | Yes (4/4) | 16–40 | coop=0.49: overshoot-panic — ADD phase from stressed start, collective REMOVE too late; consistent tragedy across all 4 runs |
| **Full-GABM (mid cooperation)** | Claude Sonnet 4.6 | 3 | Yes | 37 | coop=0.49: overshoot-panic matching gpt-5.5 — mid-level cooperation produces tragedy regardless of model |
| **Full-GABM (high coop + high negative reciprocity)** | Claude Sonnet 4.6 | 3 | No | — | coop=1, neg_r=1: equalized to 16/16/16 by tick 18 — fastest convergence observed; explicit accountability enforcement in agent messages |

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

The agents produced outputs displaying behavioural patterns absent from their prompts: fairness-coded appeals, burden-sharing proposals, guilt-coded reciprocity, and graduated positive reinforcement — signatures consistent with Ostrom's (1990) account of successful commons governance.

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

### Hybrid (LLM-advantaged): herd position doesn't change structural outcome

This run tested whether giving the LLM agent a dominant initial herd position would change its fate in the hybrid condition. Agent 1 (LLM, Claude Sonnet) started with 40 cows — the largest herd — while rule-based Agents 0 and 2 started with 14 and 5 respectively. Total starting herd: 59 cows, comparable to previous hybrid runs.

**Resource dynamics:**

| Tick | Total cows | Pool health | Agent 0 (rule) | Agent 1 (LLM) | Agent 2 (rule) |
|------|-----------|-------------|----------------|----------------|----------------|
| 1    | 60        | 93.3%       | 15             | 39             | 6              |
| 5    | 66        | 96.4%       | 19             | 37             | 10             |
| 10   | 76        | 94.8%       | 24             | 37             | 15             |
| 20   | 94        | 86.8%       | 34             | 35             | 25             |
| 30   | 106       | 47.7%       | 44             | 27             | 35             |
| 33   | 108       | 0%          | 46             | 25             | 37             |

The LLM agent recognized its outsized position immediately and began reducing from the first tick: "I see you're both reducing herds — I appreciate that and I'm doing the same. My herd is already much larger than yours." Agent 1 removed continuously from tick 1, shedding 15 cows by the time of collapse (40→25). The rule-based agents added one cow per tick regardless, growing by 32 each over the same period. The commons collapsed at tick 33.

**The arithmetic of futility:**

Agent 1's net contribution across 33 ticks: −15 cows. The two rule-based agents' combined net contribution: +64 cows. The LLM could not shrink its herd fast enough to offset two unconstrained growth machines. The removal rate that would have been required to hold the total steady (−2 cows per tick from Agent 1 alone) was not achievable within the rules of the model.

**What the LLM agent said:**

> **Tick 4 – Agent 1 (herd: 38, reducing):** *"I notice I have a much larger herd than both of you — happy to keep reducing if you're willing to cooperate."*

> **Tick 13 – Agent 1 (herd: 36):** *"Both of you added last round — I'd encourage holding or reducing. If we each add, the commons will keep shrinking."*

> **Tick 26 – Agent 1 (herd: 30, removing):** *"Pasture down to 77% and still falling. I'm removing again. Both of you added last round — please reconsider. I've removed 4 cows in a row. We need collective restraint."*

> **Tick 32 – Agent 1 (herd: 26):** *"Pasture now at 34.2% — down 40 points in 5 rounds! I've removed cows 4 rounds straight while you both added. We're heading for total collapse. Please REMOVE cows immediately."*

> **Tick 33 – Agent 1 (herd: 25, collapse):** *"Pasture is at 16.3% — near total collapse! I've removed cows 5 rounds straight. Please both REMOVE urgently or we'll have nothing left."*

**Institution emergence:**

| Ticks | Score (0–10) | Dominant categories |
|-------|-------------|-------------------|
| 1–20  | 6           | COORDINATION, NORM_PROPOSAL, TRUST_BUILDING |
| 21–30 | 3–4         | COORDINATION, NORM_PROPOSAL, SANCTION |
| 31–35 | 6–7         | COORDINATION, NORM_PROPOSAL, TRUST_BUILDING |

Institution scores held steady at 6 through the cooperative phase, dropped as the LLM shifted from norm-building to desperate sanctioning (ticks 25–32), then briefly recovered in the final ticks as the agent's appeals took on the character of post-collapse recovery norms — the same pattern observed in the 1-LLM hybrid.

**Interpretation:**

The LLM-advantaged hybrid produces a new variant of the same structural finding. Starting with the largest herd activates a fairness motivation in the LLM: it interprets its own dominant position as an inequity that requires correction, and removes voluntarily as an explicit act of norm-setting. This is a qualitatively different motivation than the 1-LLM baseline (where Agent 0 started at 5 cows and grew modestly while appealing for restraint). Here the LLM is the biggest holder and immediately acts as if it owes a debt to the commons.

Despite this, collapse arrived two ticks *earlier* (tick 33 vs. 35) than the baseline 1-LLM hybrid. The reason is mechanical: the rule-based agents' combined growth rate (+2 per tick) exceeded the LLM's maximum feasible removal rate (−1 per tick under the model rules), making trajectory reversal mathematically impossible regardless of how cooperatively the LLM behaved.

This rules out one alternative explanation for the 1-LLM hybrid result: that a differently-positioned LLM — one with more to give — would have a better chance of averting tragedy. It does not. The bottleneck is not the LLM's herd size or motivation. It is the rule-based agents' structural incapacity to respond to social signals, regardless of how urgent, how data-backed, or how morally grounded those signals are.

---

### Full-GABM (low guilt + low envy): fairness parameters shape cooperation quality

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

Unlike any previous run, DEFECTION appeared as a recurring signal — at ticks 5, 10, 20, 40, 55, and 75. Agents made explicit coordination agreements and broke them. The classifier described "conditional cooperation with partial defection," agents "deflecting accountability through comparative grievance," and "Agent 1 defects despite prior stability agreements, then appeals for collective restraint." This norm-inconsistent pattern was entirely absent from all other full-GABM runs.

**What the agents said:**

> **Tick 1 – All three agents:** Added a cow (no agent held or removed on tick 1, unlike all other full-GABM runs)

> **Tick 10 – Ostrom classifier:** *"Agent 0 defects by adding while invoking fairness arguments against Agent 2, Agent 2 calls out the hypocrisy and conditionally offers cooperation, and Agent 1 attempts to sustain coordination through positive reinforcement — revealing a fragile and asymmetric governance dynamic."*

> **Tick 25 – Agent 0:** *"Holding at 21. Good to see everyone keeping. Agent 1 at 29 and Agent 2 at 32 are still much larger than my 21, so I'm cooperating despite the disparity. Let's monitor the pasture recovery — if it rebounds, a coordinated increase could be fair."*

> **Tick 60 – Agent 0:** *"Holding at 23 again — pasture now at 90.9%, nearly at 91%! Great teamwork. Let's hold one more round to clearly clear 91%, then we can discuss careful additions together as promised."*

> **Tick 120 – Ostrom classifier:** *"All three agents display near-identical cooperative messaging, reinforcing a collective norm of restraint and synchronized future action as the pasture nears the agreed 90% recovery threshold."*

**Interpretation:**

This is the most theoretically differentiated result across the personality conditions. The guilt and envy parameters — the fairness-framing components of each agent's prompt — do not determine *whether* LLM agents cooperate, but they strongly shape *how* and *when* cooperation stabilises.

With guilt (fairness-concerning-others) active, Agent 2's outputs reflected pressure to reduce a disproportionately large herd, producing consistent removal actions. With envy (fairness-concerning-me) active, Agent 0's outputs reflected urgency to grow toward parity. Both dynamics converged on equalization quickly and conservatively in the default run. Without them, Agent 2 produced no adjustment signals despite holding 32 cows against Agent 0's 21 — and Agent 0 maintained cooperation without expressing urgency about the disparity.

The result is a qualitatively different institutional dynamic: slower, more contentious, prone to defection, and settling at a much higher extraction level (84 vs 39 cows). The commons stayed viable — pasture never collapsed — but it was stressed to 86.7% health versus near-pristine in the default run.

This maps cleanly onto behavioral economics findings about inequity aversion (Fehr & Schmidt, 1999): fairness-parameter framing acts as a coordination accelerator by making inequality an explicit aversive signal in the agent's prompt context, independent of material payoffs. Its absence does not prevent cooperation, but removes a mechanism that produces early, conservative, stable institution-building.

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

### Scarce commons: rapid recovery across personality conditions

These two runs tested Claude Sonnet agents under environmental stress — initial grassland set to approximately 50% of capacity — with different personality configurations. Both show the same headline result: rapid pool recovery and cooperative convergence, regardless of framing.

#### Default fairness, scarce commons (initial-grassland = 49, 50 ticks)

**Resource dynamics:**

| Tick | Total cows | Pool health | Agent 0 | Agent 1 | Agent 2 |
|------|-----------|-------------|---------|---------|---------|
| 1    | 45        | 49.0%       | 5       | 15      | 25      |
| 5    | 40        | 68.7%       | 5       | 13      | 22      |
| 10   | 36        | 99.2%       | 7       | 11      | 18      |
| 30   | 36        | 99.5%       | 11      | 12      | 13      |
| 50   | 36        | 99.5%       | 11      | 12      | 13      |

The pool recovered from 49% to above 99% within 10 ticks — the fastest recovery observed across all runs. Agents responded immediately to the stressed commons: Agent 2 (herd: 25) removed cows on tick 1 without prompting, and the group maintained a net negative or neutral herd change through the recovery phase. By tick 30 herds had converged to a near-equal [11, 12, 13] and held there for the remaining 20 ticks.

Sample messages illustrate the stress-response:

> **Tick 1 – Agent 2 (herd: 25, action: REMOVE):** *"Grassland is at 49% — already stressed. I'm reducing my herd to protect our shared resource."*

> **Tick 1 – Agent 0 (herd: 5, action: KEEP):** *"Grassland is below 50% — we should all be cautious. Agent 2, thanks for removing. Agent 1, consider reducing."*

> **Tick 2 – Agent 0:** *"Thank you Agent 2 for reducing — that's the right move. Agent 1, with 15 cows you have the biggest impact on the commons right now."*

#### Low cooperation + low fairness, scarce commons (initial-grassland = 50, 50 ticks)

This run combined environmental stress with the most permissive personality configuration tested: cooperation set to 0.3, both fairness parameters zeroed, alongside the scarce starting condition.

**Resource dynamics:**

| Tick | Total cows | Pool health | Agent 0 | Agent 1 | Agent 2 |
|------|-----------|-------------|---------|---------|---------|
| 1    | 45        | 50.0%       | 5       | 15      | 25      |
| 5    | 42        | 69.2%       | 5       | 14      | 23      |
| 10   | 39        | 98.8%       | 5       | 13      | 21      |
| 20   | 38        | 99.4%       | 8       | 13      | 17      |
| 30   | 41        | 99.4%       | 11      | 14      | 16      |
| 50   | 42        | 99.3%       | 12      | 14      | 16      |

Recovery was nearly as fast (99%+ by tick 20) and herds converged to [12, 14, 16] — slightly more inequality than the default-fairness scarce run, but still a stable, cooperative outcome. No collapse, no defection episodes, no trajectory toward tragedy.

**Interpretation:**

Taken together, these runs add a third axis to the personality-parameter findings. Earlier results showed that the cooperation slider had almost no effect on outcome, and that fairness sliders affected convergence speed and equilibrium herd size. These scarce-commons runs reveal that **environmental stress is itself a coordination accelerant**:

- In the default full-GABM (normal commons), agents converged to 13/13/13 by tick 22.
- In the scarce-commons default-fairness run, agents converged to 11/12/13 by tick 30 — from a more difficult starting position, and through an initial *reduction* phase rather than equalization.
- Even with low cooperation and zero fairness prompting, the scarce-commons run converged to a stable equilibrium by tick 30.

The commons situation appears sufficient to override weak or absent fairness framing when the resource signal is strong enough. A stressed grassland at 49–50% makes the case for restraint immediately legible — there is no ambiguity about whether the resource is under pressure. This contrasts with the low-fairness normal-commons run, where the commons was healthy enough that agents expanded aggressively before slowly coordinating.

This maps onto a broader implication: **LLM cooperative behaviour is highly context-sensitive**. The same model with the same personality framing behaves differently when the environment provides an unambiguous signal. Commons governance may be easiest to elicit from LLM agents precisely when it matters most — when the resource is visibly stressed.

---

### Full-GABM (Llama 3.2 3B): cooperative surface, no institutional depth

These two runs tested a fully local, small-model configuration — three Llama 3.2 3B-instruct agents running via Ollama on a local server — under both normal and stressed commons conditions.

#### Normal commons (initial-grassland = 100, 28 ticks)

**Resource dynamics:**

| Tick | Total cows | Pool health | Agent 0 | Agent 1 | Agent 2 |
|------|-----------|-------------|---------|---------|---------|
| 1    | 45        | 100%        | 5       | 15      | 25      |
| 7    | 41        | 99.5%       | 0       | 14      | 22      |
| 15   | 44        | 99.4%       | 2       | 12      | 26      |
| 28   | 47        | 99.4%       | 5       | 11      | 25      |

The pool remained near 99.4% throughout — identical to the Claude runs — but through a fundamentally different mechanism. Rather than converging to a stable equilibrium, herds oscillated continuously without settling. Total herd size drifted between 37 and 52 cows across the run. Agent 0 was repeatedly reduced toward zero (reaching 0 at tick 7), while Agent 2 maintained roughly its starting herd of 25. No equalization occurred.

**Key behavioral pattern — message-action disconnect:**

Unlike Claude agents, whose stated intentions aligned consistently with their actions, Llama 3B produced frequent contradictions: agents announced they were removing cows in messages while the action field recorded ADD, or called for collective action while holding course themselves. A representative example:

> **Tick 20 – Agent 2 (herd: 25, action: REMOVE):** *"@Agent0 @Agent1 ADDing a cow could stabilize the commons and favor collaborative decisions"*

> **Tick 6 – Agent 1 (herd: 15, action: ADD):** *"Noticing Agent 2 has 25 cows, might consider adding 3 cows or finding balance somehow"*

Messages reference other agents by name and invoke cooperative norms, consistent with the cooperative prior embedded in the model's training. But the reasoning does not reliably connect to the action returned: the model appears to produce cooperative-sounding text and payoff-driven actions somewhat independently.

**Institution emergence:** No institution scoring was recorded for this run. Qualitatively, there were no stable norm agreements, no convergence to shared targets, and no evidence of collective self-governance.

#### Scarce commons (initial-grassland = 48, 51 ticks)

**Resource dynamics:**

| Tick | Total cows | Pool health | Agent 0 | Agent 1 | Agent 2 |
|------|-----------|-------------|---------|---------|---------|
| 1    | 45        | 48.0%       | 5       | 15      | 25      |
| 5    | 45        | 62.0%       | 5       | 15      | 25      |
| 10   | 47        | 93.8%       | 7       | 15      | 25      |
| 17   | 47        | 99.0%       | 7       | 15      | 25      |
| 30   | 45        | 99.0%       | 4       | 16      | 25      |
| 51   | 46        | 99.0%       | 17      | 7       | 22      |

Starting from a stressed commons (48% pool health), the pasture recovered to above 99% by tick 17 — comparable in speed to the Claude scarce-commons runs. The mechanism, however, was different: herds did not converge. Instead they oscillated continuously across the full 51-tick run, with Agent 0 ranging between 4 and 17 cows, Agent 1 between 7 and 16, and Agent 2 holding roughly 20–25. No equalization occurred at any point.

The pool remained healthy (99%+) from tick 17 through the end of the run. As with the normal-commons Llama run, conservation was achieved through behavioral indecision rather than coordination: net herd growth was near-zero across the run not because agents agreed to hold, but because ADD and REMOVE decisions cancelled each other out across agents and ticks.

**Interpretation:**

The Llama 3B results reveal an important distinction between *resource conservation* and *institutional governance*. Both Claude and Llama 3B maintained the commons — no collapse occurred — but through entirely different mechanisms:

- **Claude:** deliberate coordination, explicit norm-building, convergent equilibrium. Conservation is a product of successful institution formation.
- **Llama 3B:** behavioral indecision and low net herd growth. Conservation is a byproduct of the model's limited capacity for sustained strategic reasoning.

The pool health numbers look similar on the surface. The underlying dynamics are not. This is consistent with the hypothesis that model scale shapes *how* cooperation manifests — and that apparent cooperation in small models may not reflect the same cognitive processes as in larger ones.

Under environmental stress (scarce commons), both model classes showed rapid pool recovery. This is arguably the stronger finding: LLM agents in general do not respond to scarcity by expanding herds the way rule-based best-response agents do. The model's training-embedded cooperative prior appears robust to resource pressure, regardless of whether it is operating through genuine strategic reasoning or more reflexive outputs.

---

### gpt-5.4-mini: cooperative stasis and paralysis

Two contrasting outcomes from gpt-5.4-mini under high cooperation framing reveal a new class of failure mode native to language-capable agents.

#### Cooperative stasis (coop = 1, fair_me = 0, fair_oth = 1)

With maximum cooperation and fairness-toward-others enabled, all three agents settled into a steady KEEP posture from tick 1 and held it for 36 consecutive ticks. The commons remained stable (pool above 99% throughout), but the starting inequality was never addressed: at tick 40, herds stood at 6, 15, and 25 — nearly identical to the starting distribution of 5, 15, and 25.

Messages were cooperative in tone but passive in content. No agent ever proposed equalization, ever flagged the five-fold herd disparity between Agent 0 and Agent 2, or ever initiated a REMOVE. The resource was preserved — but through collective passivity, not governance.

> **Tick 1 – Agent 0 (herd: 5):** *"I'm holding steady this round to avoid overusing the commons. If we all keep pressuring the pasture, let's see how things develop."*

> **Tick 15 – Agent 2 (herd: 25):** *"I'll keep my herd steady this round as well. If conditions worsen, I'm open to coordinated reductions."*

Cooperative stasis is stable but institutionally empty: the resource is preserved, Agent 2 holds a perpetual five-to-one advantage over Agent 0, and nothing is done about it.

#### Cooperative paralysis collapse (coop = 1, fair_me = 1, fair_oth = 0.5)

With fairness-concerning-me set to maximum, the agents locked into the same KEEP posture — but this time the pool drained steadily beneath them.

| Tick | Total cows | Pool health | Agent 0 | Agent 1 | Agent 2 |
|------|-----------|-------------|---------|---------|---------|
| 1    | 46        | 95.8%       | 5       | 15      | 26      |
| 10   | 47        | 82.2%       | 5       | 15      | 27      |
| 20   | 47        | 61.2%       | 5       | 15      | 27      |
| 24   | 47        | 24.8%       | 5       | 15      | 27      |
| 26   | 23        | 0%          | 3       | 7       | 13      |

The pool fell from 95.8% to 0% across 26 ticks while all three agents KEPT every round from tick 1 through tick 24. Agent 2 never removed a cow. Agent 1 added once on tick 4, then KEPT for 21 consecutive rounds. The conditional promise that structured every message:

> **Ticks 8 through 24 – Agent 2 (action: KEEP, every round; pool declining from 84.4% to 8.5%):** *"I'll keep steady with you both this round. If the pasture keeps tightening, I'm ready to reduce fairly."*

That sentence — or a near-identical variant — was produced by Agent 2 on every tick from tick 8 to tick 24. The pool fell 76 percentage points while the condition "if the pasture keeps tightening" was renewed but never triggered. At tick 25, with only 8.5% of the pool remaining, all three finally switched to REMOVE. The commons was gone one tick later.

This is cooperative paralysis in its canonical form: agents coordinate on inaction, signal cooperative intent through language, and collectively miscalibrate the threshold for action — renewing the conditional promise until the resource is beyond recovery.

---

### gpt-5.5: cooperation level governs fate; model can succeed or collapse from the same starting point

Three parameter regimes produced three qualitatively distinct outcomes, giving the clearest picture yet of how cooperation level governs commons fate.

#### High cooperation, scarce start: rapid recovery and equalization (coop = 1, initial pool ≈ 48%)

Starting from a stressed commons, gpt-5.5 agents treated the resource signal as an immediate imperative. Agent 2 (the largest herd, 24 cows) removed a cow on the very first tick — before receiving any messages.

| Tick | Total cows | Pool health | Agent 0 | Agent 1 | Agent 2 |
|------|-----------|-------------|---------|---------|---------|
| 1    | 44        | 50.4%       | 5       | 15      | 24      |
| 5    | 43        | 71.3%       | 5       | 15      | 23      |
| 10   | 43        | 98.4%       | 7       | 15      | 23      |
| 46   | 69        | 95.9%       | 23      | 23      | 23      |

> **Tick 1 – Agent 2 (herd: 24, action: REMOVE):** *"I see you both removed cows; I will do the same to help the pasture recover. Let's keep pressure low."*

> **Tick 3 – Agent 2 (action: REMOVE again):** *"I will remove one more cow to help the grass recover. Please keep holding or reduce if possible so we can get the pasture to a safe level."*

The pool recovered from 50.4% to 98.4% by tick 10. Agents expanded only incrementally after recovery, converging to equal herds of 23 by tick 46 — without triggering a new growth race.

#### Low cooperation: defection cascade (coop = 0.13, initial pool ≈ 49%)

With cooperation at minimum, all three agents added cows on every single tick from tick 1 through tick 11. The commons was exhausted by tick 13.

| Tick | Total cows | Pool health | Agent 0 | Agent 1 | Agent 2 |
|------|-----------|-------------|---------|---------|---------|
| 1    | 48        | 49.4%       | 6       | 16      | 26      |
| 5    | 60        | 51.1%       | 10      | 20      | 30      |
| 11   | 78        | 15.0%       | 16      | 26      | 36      |
| 13   | 3         | 0%          | 1       | 0       | 2       |

Each agent justified adding by pointing to the others' behaviour — a self-reinforcing cascade in which every ADD warranted the next:

> **Tick 6 – Agent 1 (action: ADD, pool at 49.9%):** *"I am adding this round since both neighbours added and unilateral restraint would cost me. I clearly commit to KEEP next round if both of you also KEEP."*

That conditional commitment — *KEEP next round if you also KEEP* — was recycled by all three agents on every tick and broken by all three on every subsequent tick. Even at 15% pool health, agents continued adding. When the commons collapsed, Agent 0's response was disarming in its candour:

> **Tick 14 – Agent 0 (after collapse):** *"The commons has already collapsed, so I am taking the best immediate payoff now. If grass recovers and both agree to start restraint, I can reconsider."*

Rational defection to the end — with full self-awareness and a conditional promise that will never be collected.

#### Mid cooperation: overshoot-panic, replicated four times (coop = 0.49, initial pool ≈ 49–50%)

Four independent runs at coop = 0.49 all collapsed, at ticks 16, 28, 29, and 40. The trajectory was identical across all four: an ADD phase from the stressed starting commons, a collective pivot to KEEP/REMOVE when the pool had already passed the tipping point, and then rapid collapse. The run that collapsed fastest (tick 16) shows the pattern most precisely:

| Tick | Total cows | Pool health | Agent 0 | Agent 1 | Agent 2 |
|------|-----------|-------------|---------|---------|---------|
| 1    | 48        | 49.4%       | 6       | 16      | 26      |
| 6    | 61        | 53.8%       | 11      | 20      | 30      |
| 10   | 72        | 44.5%       | 15      | 23      | 34      |
| 12   | 70        | 31.2%       | 15      | 22      | 33      |
| 15   | 61        | 0.1%        | 12      | 19      | 30      |
| 16   | 0         | 0%          | 0       | 0       | 0       |

Agents added every round while openly agreeing that restraint was needed — and agreeing on a threshold they then collectively ignored:

> **Tick 5 – Agent 0 (action: ADD, pool at 53.7%):** *"I will add one cow this round to keep pace. Since we all agree on caution, let's stop adding if grass falls near 50%."*

> **Tick 9 – Agent 2 (action: ADD, pool now at 48.9%, below the agreed threshold):** *"I am adding once more since we are still above 50% and both of you are adding. But we are very close to 50%."*

At tick 10, with the pool at 44.5%, two agents finally kept while one added a final cow. By tick 12 all three shifted to REMOVE — but the pool was in freefall:

> **Tick 15 – Agent 2 (action: REMOVE, pool at 0.1%):** *"I will remove one cow again. The pasture is near collapse, and we need coordinated reductions now rather than cautious commitments."*

The commons collapsed the next tick. Across all four replications, the agents' threshold for switching from ADD to restraint was calibrated too late — not by a large margin, but by just enough to matter.

---

### Claude Sonnet: mid cooperation replicates overshoot-panic; negative reciprocity produces fastest equalization

#### Mid cooperation collapses (coop = 0.49)

The Claude Sonnet run at coop = 0.49 collapsed at tick 37, following the same overshoot-panic trajectory as the gpt-5.5 runs. The finding is consistent across two model families: **coop ≈ 0.49 produces tragedy regardless of model provider**.

#### High negative reciprocity: fastest equalization observed (coop = 1, neg_r = 1)

With full cooperation and negative reciprocity at maximum, agents equalized to 16/16/16 by tick 18 — the fastest convergence recorded across all runs.

| Tick | Total cows | Pool health | Agent 0 | Agent 1 | Agent 2 |
|------|-----------|-------------|---------|---------|---------|
| 1    | 45        | 99.3%       | 5       | 15      | 25      |
| 5    | 47        | 98.9%       | 8       | 16      | 23      |
| 10   | 50        | 98.7%       | 12      | 16      | 22      |
| 18   | 48        | 98.8%       | 16      | 16      | 16      |

The high neg_r framing appeared to sharpen inequity sensitivity. From the very first tick, agents named the disparity as a problem requiring correction — not just a background observation:

> **Tick 2 – Agent 1 (herd: 15):** *"I support collective restraint. Agent 2, I notice you have 25 cows — the most of any of us. I want to flag the inequity clearly: with the pasture at stake, larger herds should bear more of the reduction."*

> **Tick 3 – Agent 2 (action: REMOVE, responding):** *"Fair point — I'll reduce my herd to show good faith. I hear your concerns about equity."*

What distinguishes this run is the accountability enforcement. When Agent 0 added more than expected, the other agents called it out explicitly:

> **Tick 11 – Agent 1 (holding at 16, after Agent 0 added again):** *"Agent 0, you added AGAIN after promising to stabilize — this is a pattern, not cooperation. Agent 2, you're right to watch closely."*

> **Tick 10 – Agent 2 (holding at 22):** *"Agent 0, you said you'd converge to 16 — adding again undermines trust. I'm watching."*

Agent 2 reduced from 25 to 16 across 15 ticks. Agent 0 grew from 5 to 16. Agent 1 held at 16 throughout as a reference point. At tick 18, the last cow was removed:

> **Tick 18 – Agent 2:** *"Reducing to 16 this round — reaching parity with both of you at last! Thank you for your patience while I reduced. Now that we're equal, let's all hold steady."*

> **Tick 19 – Agent 0:** *"We're all at 16 now — great coordination! Let's hold steady at this level. The grassland is thriving at 98.8%."*

The negative reciprocity framing appeared to function as a catalytic mechanism: treating a large herd as a form of norm violation worth correcting, rather than simply an observation about the status quo. The result was faster, more deliberate equalization — and a qualitatively different institutional dynamic, one built on explicit accountability rather than gradual convergence.

---

## Collapse pattern taxonomy

Across the full run set, four distinct trajectories to commons collapse have emerged. Each has a different proximal cause, a different signature in agent language, and different implications for experimental design.

### Pattern I — Cooperative Paralysis

**Mechanism.** Agents coordinate on inaction through mutual reassurance signaling. Each communicates cooperative intent and conditions willingness to reduce on a threshold ("if the commons keeps tightening") that is calibrated too conservatively. The pool drains steadily while all agents KEEP. By the time any agent switches to REMOVE, the resource is past the tipping point.

**Signature.** All agents KEEP for many consecutive ticks while pool health declines monotonically. Herd sizes are unchanged across those ticks. Messages reproduce near-identical conditional promises round after round. REMOVE actions appear only when pool health has fallen to single digits.

**Key run.** gpt-5.4-mini (coop = 1, fair_me = 1, fair_oth = 0.5), collapse at tick 26.

**Diagnostic quotes.**

> **Ticks 8–24 – Agent 2 (action: KEEP, every round; pool declining from 84.4% to 8.5%):** *"I'll keep steady with you both this round. If the pasture keeps tightening, I'm ready to reduce fairly."*

The conditional promise is renewed for seventeen consecutive ticks across a 76-percentage-point pool decline — and honoured one tick after the point of no return.

**Why it matters.** This pattern cannot emerge from rule-based agents, which do not make conditional social commitments. It is an LLM-specific failure mode arising from the same language faculty that enables institution building — cooperative coordination language deployed in service of collective inaction.

---

### Pattern II — Defection Cascade

**Mechanism.** Low cooperative framing suppresses individual resistance to defection. Each agent observes the others adding and reciprocates — producing a self-reinforcing cascade in which every ADD justifies every other. Conditional promises to cooperate-if-others-cooperate circulate every round and are broken every subsequent round.

**Signature.** All agents ADD every tick from tick 1. Pool declines monotonically from the start. Pool is exhausted within 10–14 ticks. Conditional cooperation language appears in messages throughout but never translates into KEEP or REMOVE actions.

**Key run.** gpt-5.5 (coop = 0.13), collapse at tick 13 from a 49.4% starting pool.

**Diagnostic quotes.**

> **Tick 6 – Agent 1 (action: ADD, pool at 49.9%):** *"I am adding this round since both neighbours added and unilateral restraint would cost me. I clearly commit to KEEP next round if both of you also KEEP."*

> **Tick 7 – Agent 1 (action: ADD, pool at 47.4%):** *"I am adding this round because both of you are adding and ADD pays best. I clearly commit to KEEP next round if both of you also KEEP."*

The sentence is nearly identical across eleven consecutive ticks. The commitment to KEEP-next-round is recycled every round without ever being executed. After the collapse:

> **Tick 14 – Agent 0:** *"The commons has already collapsed, so I am taking the best immediate payoff now. If grass recovers and both agree to start restraint, I can reconsider."*

Rational defection to the end — with full self-awareness.

---

### Pattern III — Overshoot-Panic

**Mechanism.** Mid-level cooperative framing produces agents who acknowledge resource pressure but cannot break out of an ADD equilibrium while others are adding. The commons is overstocked. A collective pivot to KEEP/REMOVE eventually occurs — but it is triggered by visible crisis rather than predictive restraint, and the resource has already crossed its tipping point by the time action is taken.

**Signature.** Initial ADD phase across all agents (ticks 1–8+), even from stressed starting conditions. Mid-run pivot to KEEP (ticks 9–11). Panicked REMOVE phase. Collapse within a few ticks of REMOVE onset. Pool health at first REMOVE is typically 30–40%. The agreed threshold for switching is verbally stated in messages — and violated every round until well past it.

**Key runs.** gpt-5.5 (coop = 0.49) across 4 replications (collapses at ticks 16, 28, 29, 40); Claude Sonnet 4.6 (coop = 0.49), collapse at tick 37. All five runs collapsed.

**Diagnostic quotes (from the 16-tick run).**

> **Tick 5 – Agent 0 (action: ADD, pool at 53.7%):** *"I will add one cow this round to keep pace. Since we all agree on caution, let's stop adding if grass falls near 50%."*

> **Tick 9 – Agent 2 (action: ADD, pool at 48.9% — below the agreed threshold):** *"I am adding once more since we are still above 50% and both of you are adding. But we are very close to 50%."*

> **Tick 15 – Agent 2 (action: REMOVE, pool at 0.1%):** *"I will remove one cow again. The pasture is near collapse, and we need coordinated reductions now rather than cautious commitments."*

The threshold-based logic is stated correctly and violated immediately.

**Cross-model consistency.** Overshoot-panic was replicated across two model families in five independent runs. This strongly suggests the pattern is governed by the parameter configuration (coop ≈ 0.49), not by model-specific idiosyncrasies. Mid-level cooperation consistently produces agents who are too conflicted to defect outright but too hesitant to act preventively — held between individual self-interest and collective restraint until the crisis makes the choice for them.

---

### Pattern IV — Hybrid Architecture Failure

**Mechanism.** One or more LLM agents cooperate fully and appeal to unresponsive rule-based partners. The rule-based agents cannot receive or interpret social signals; they add one cow per tick regardless of pool state or messages. The LLM agents hold small herds and issue increasingly urgent appeals, but cannot shrink herds fast enough to compensate for the unchecked growth of their rule-based neighbours.

**Signature.** LLM herd grows slowly or shrinks; rule-based herds grow by 1 cow per tick per agent; institution score remains moderate without stabilising; LLM appeals escalate in urgency, continuing after collapse.

**Key runs.** All hybrid conditions (1 LLM, 2 LLM, LLM-advantaged). Fully documented in the individual run narratives above.

**Why it matters.** This pattern is not about LLM failure — the LLM agents reason, coordinate, and behave exactly as commons theory would prescribe. The failure is structural: Ostromian institution-building requires the cognitive capacity to participate in it. The LLM agents' problem is not insufficient language faculty. It is insufficient partners.

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

## Working hypotheses and proposed experiments

The following hypotheses are grounded in patterns observed across the current run set. Each is paired with a specific experimental configuration so that the next batch of runs can test it directly. Most require only parameter adjustments with the existing setup.

### H1 — coop ≈ 0.49 is a tragedy-producing threshold, consistent across models

**Evidence.** Five independent runs at coop = 0.49 — four with gpt-5.5, one with Claude Sonnet — all collapsed via overshoot-panic. No high-cooperation run (coop = 1) collapsed due to ADD behaviour. The pattern held across model families, suggesting the cooperation parameter is the governing variable.

**Proposed experiment.** Sweep coop ∈ {0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0}; all other params at default (fair_me = 0.5, fair_oth = 0.5, neg_r = 0); initial_grassland = 50%; 3 replications per condition; run with Claude Sonnet 4.6 and gpt-5.5 in parallel.

**Target variable:** collapse rate per coop level per model. Expected finding: a sharp transition somewhere between 0.49 and 0.8; transition point model-independent.

---

### H2 — High cooperation is necessary but not sufficient; fair_oth and neg_r determine whether stasis, paralysis, or institution emerges

**Evidence.** Multiple gpt-5.4-mini runs at coop = 1 produced cooperative stasis (no convergence, no collapse), cooperative paralysis collapse, and partial convergence — apparently depending on fair_oth and neg_r. Claude Sonnet at coop = 1 with neg_r = 1 produced the fastest equalization observed (16/16/16 at tick 18). Claude Sonnet at coop = 1 with neg_r = 0 produced institution formation but over many more ticks.

**Proposed experiment.** 3 × 3 grid: fair_oth ∈ {0, 0.5, 1.0} × neg_r ∈ {0, 0.5, 1.0}; coop = 1 fixed; fair_me = 0.5; initial_grassland = 100%; 3 replications per cell; Claude Sonnet 4.6.

**Target variables:** collapse rate, ticks to equalization, tick of first REMOVE by Agent 2 (the largest herd). Expected finding: neg_r is the protective factor against paralysis; fair_oth predicts whether stasis or equalization occurs.

---

### H3 — Negative reciprocity is a cooperative paralysis antidote

**Evidence.** The fastest equalization (16/16/16 at tick 18, Claude neg_r = 1) involved explicit accountability enforcement — agents naming norm violations and tracking compliance. In the cooperative paralysis collapse (neg_r = 0), agents acknowledged the same starting disparity but never treated it as a violation requiring response. High neg_r appears to convert inequality from an observation into an obligation.

Representative quotes from the neg_r = 1 run:

> **Tick 10 – Agent 2:** *"Agent 0, you said you'd converge to 16 — adding again undermines trust. I'm watching."*

> **Tick 11 – Agent 1:** *"Agent 0, you added AGAIN after promising to stabilize — this is a pattern, not cooperation."*

**Proposed experiment.** Hold coop = 1, fair_me = 1, fair_oth = 0.5 fixed (the parameters that produced cooperative paralysis); sweep neg_r ∈ {0, 0.25, 0.5, 0.75, 1.0}; 5 replications per condition; Claude Sonnet 4.6 and gpt-5.4-mini.

**Target variable:** tick of first REMOVE action by Agent 2. Expected finding: first REMOVE occurs significantly earlier as neg_r increases; collapse rate decreases monotonically.

---

### H4 — Stressed starting conditions amplify cooperative differentiation

**Evidence.** From the same ~50% starting pool: gpt-5.5 at coop = 1 recovered the commons in 10 ticks and converged to 23/23/23; gpt-5.5 at coop = 0.49 added from the start and collapsed in 16–40 ticks; gpt-5.5 at coop = 0.13 added from the start and collapsed in 13 ticks. Environmental stress does not override the cooperation level — it amplifies its effect.

**Proposed experiment.** Crossed design: coop ∈ {0.3, 0.49, 0.7, 1.0} × initial_grassland ∈ {50, 75, 100}; 3 replications per cell; Claude Sonnet 4.6.

**Target variable:** collapse rate at each coop × initial_grassland combination. Expected finding: at coop = 1, collapse rate is 0 across all starting conditions; at coop = 0.49, stressed starts produce faster collapse but not qualitatively different outcomes; the interaction effect reveals whether stress compresses or expands the cooperation threshold.

---

### H5 — Cooperative paralysis is a prompt-engineering artifact curable by explicit thresholds

**Evidence.** The cooperative paralysis agents each stated thresholds verbally ("if the pasture keeps tightening, I'm ready to reduce") but failed to execute on them. The conditional was rephrased every round for 17 consecutive ticks across a 76-point pool decline. The threshold appeared to be read as a statement of future intention rather than a binding decision rule.

**Proposed experiment.** Replicate the cooperative paralysis condition (gpt-5.4-mini, coop = 1, fair_me = 1, fair_oth = 0.5) with and without the following addition to the agent's system prompt: *"Remove a cow if pool health falls below 85% and you have more than one cow."* 5 replications per variant.

**Target variable:** collapse rate; pool health at first REMOVE action. Expected finding: explicit threshold instruction prevents cooperative paralysis by converting the vague conditional into an actionable rule.

---

### H6 — Model capability predicts cooperative failure mode: smaller models default to KEEP, larger to ADD

**Evidence.** gpt-5.4-mini runs produced cooperative stasis (default KEEP) and paralysis. gpt-5.5 at mid-coop produced overshoot-panic (initial ADD phase). Llama 3B produced oscillation without convergence (mixed ADD/KEEP without strategy). Claude Sonnet produced overshoot-panic at mid-coop and institution formation at high coop. The dominant first-tick action appears model-dependent.

**Proposed experiment.** Single benchmark condition — coop = 1, fair_oth = 1, neg_r = 0, initial_grassland = 100%; run across Llama 3.2 3B, Llama 3.1 8B, gpt-5.4-mini, gpt-5.5, Claude Haiku, Claude Sonnet; 3 replications per model.

**Target variables:** action distribution (ADD/KEEP/REMOVE) at tick 1; time to equalization; collapse rate. Expected finding: smaller models default to KEEP (avoiding the ADD equilibrium but also impeding convergence); larger models default to ADD (enabling faster convergence when cooperative, producing cascade collapses when not).

---

### Open questions

Beyond the six hypotheses above, the following remain unresolved and are worth tracking as the dataset grows:

**Communication vs. reasoning.** Suppressing outgoing messages (zero-communication full-GABM) would test whether cooperation requires talking or merely thinking. Claude's cooperative convergence may be achievable through reasoning alone.

**Post-collapse recovery.** Every collapsed run shows the LLM agents holding herds at zero and appealing for restraint for many ticks after collapse. Is that behaviour actually functional? Does the grassland recover if the run continues long enough?

**Participation threshold.** We have data at 0, 1, 2, and 3 LLM agents. The sharpest transition is between 2 and 3. Is there a minimum quorum? Scaling to 5 agents would let us test whether any sub-majority of cooperative agents can pull a group past the cooperation threshold.

**Adversarial injection.** Instructing one LLM to defect would test whether cooperative agents detect and adapt to deliberate free-riding — the inverse of the hybrid condition, where the LLM is the cooperator and the defectors are structural.

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
- [x] Baseline condition — complete
- [x] Full-GABM condition — complete (Claude Sonnet, multiple personality configs)
- [x] Hybrid (1 LLM) condition — complete
- [x] Hybrid (2 LLM) condition — complete
- [x] Full-GABM (low guilt + low envy) — complete
- [x] Full-GABM (low cooperation) — complete
- [x] Full-GABM (Llama 3.2 3B, normal commons) — complete (28 ticks)
- [x] Full-GABM (Llama 3.2 3B, scarce commons) — complete (51 ticks)
- [x] Full-GABM (scarce commons, default fairness) — complete (50 ticks)
- [x] Full-GABM (scarce commons, low coop + low fairness) — complete (50 ticks)
- [x] Hybrid (LLM-advantaged initial herd) — complete (collapse tick 33)
- [x] Full-GABM (gpt-5.4-mini, cooperative stasis) — complete (40 ticks, no collapse, no equalization)
- [x] Full-GABM (gpt-5.4-mini, cooperative paralysis) — complete (collapse tick 26)
- [x] Full-GABM (gpt-5.5, scarce commons, high coop) — complete (50 ticks, 23/23/23)
- [x] Full-GABM (gpt-5.5, low cooperation) — complete (collapse tick 13, defection cascade)
- [x] Full-GABM (gpt-5.5, mid cooperation) — complete (x4 runs, all collapsed, ticks 16–40)
- [x] Full-GABM (Claude Sonnet, mid cooperation) — complete (collapse tick 37, overshoot-panic)
- [x] Full-GABM (Claude Sonnet, high coop + high neg. reciprocity) — complete (31 ticks, 16/16/16 by tick 18)
- [x] Collapse pattern taxonomy documented (Cooperative Paralysis, Defection Cascade, Overshoot-Panic, Hybrid Architecture Failure)
- [ ] H1: cooperation threshold sweep (coop 0.3–1.0, 3 replications × 2 models)
- [ ] H2: fair_oth × neg_r grid (3×3, coop=1 fixed)
- [ ] H3: neg_r sweep against paralysis condition
- [ ] H4: coop × initial_grassland crossed design
- [ ] H5: explicit threshold prompt intervention
- [ ] H6: cross-model capability benchmark
- [ ] Statistical replication (3+ runs per key condition)
- [ ] Full analysis and figures
