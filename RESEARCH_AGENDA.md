# MASTOC-LLM Research Agenda

Questions and experiments runnable with the current setup, organised by theme.
Marked with whether they require code changes or just parameter adjustments.

---

## I. Statistical replication

**No code changes needed — just run more.**

All current results are single runs. Before drawing strong conclusions, each
condition needs at least 3–5 replications to assess outcome variance.

| Experiment | Parameters | What to measure |
|---|---|---|
| Baseline ×5 | default | Collapse tick variance; does it always hit ~36? |
| Full-GABM ×5 | default | Does 13/13/13 convergence always occur? How fast? |
| Hybrid 1-LLM ×5 | `hybrid-fraction=0.33` | Collapse tick variance; does the LLM always hold small? |
| Hybrid 2-LLM ×5 | `hybrid-fraction=0.67` | Coalition consistency; collapse tick variance |

**Research question:** How deterministic is LLM cooperative behaviour? Is the full-GABM
convergence robust, or was it a lucky run?

---

## II. Participation threshold

**No code changes needed.**

We have data at 0, 1, 2, and 3 LLM agents. The gap between 2 (collapse tick 58)
and 3 (no collapse) is the sharpest transition. Is it a cliff or a gradient?

| Experiment | Parameters | What to measure |
|---|---|---|
| Equal-split hybrid | `hybrid-fraction=0.5` (rounds to 2 LLMs with 3 agents — same as 0.67) | — |
| **Scale up to 5 agents** | modify agent count | Does 3/5 LLMs prevent tragedy? What about 4/5? |
| **Scale up to 10 agents** | modify agent count | Does institution emergence get harder or easier at scale? |

**Research question:** Is there a minimum quorum of language-capable agents for
commons governance to hold? Does it scale with group size?

---

## III. Cross-model comparison

**No code changes needed — use per-agent backend/model choosers.**

The most novel experiment the current setup enables. Run agents on different models
simultaneously and compare cooperative propensity directly within a single run.

### A. Within-provider comparison (model size)

| Experiment | Agent 0 | Agent 1 | Agent 2 | What to test |
|---|---|---|---|---|
| Haiku vs Sonnet vs Opus | `claude-haiku-4-5` | `claude-sonnet-4-6` | `claude-opus-4-6` | Does larger model = more cooperative? |
| GPT size gradient | `gpt-4o-mini` | `gpt-4o` | `o1-mini` | Same question for OpenAI family |

### B. Cross-provider comparison

| Experiment | Setup | What to test |
|---|---|---|
| Claude vs GPT-4o vs Gemini (full-GABM) | One agent each | Can agents from different providers reach cooperative equilibrium? |
| Claude vs GPT-4o vs Llama (full-GABM) | Cloud vs local | Does a local model cooperate as readily as cloud models? |
| Claude coalition vs GPT defector | 2 Claude + 1 GPT rule-prompted | Does the defector model matter? |

### C. Same model, different roles

| Experiment | Setup | What to test |
|---|---|---|
| All Haiku (full-GABM) | `claude-haiku-4-5` ×3 | Can a cheaper model reproduce the 13/13/13 result? |
| All Llama 3.2 local (full-GABM) | `ollama/llama3.2` ×3 | Fully offline cooperative commons — does it work? |
| All GPT-4o (full-GABM) | `gpt-4o` ×3 | Cross-provider replication of the core finding |

**Research question:** Do different LLMs have meaningfully different cooperation
propensities? Is the full-GABM result model-specific or a general property of
language-capable agents?

---

## IV. Initial conditions and inequality

**No code changes needed — use per-agent initial herd sliders.**

### A. LLM-advantaged hybrid

Currently the LLM agent in hybrid-1 started with the smallest herd (5 cows).
Does economic leverage change the outcome?

| Experiment | Agent 0 (LLM) | Agent 1 (rule) | Agent 2 (rule) | Hypothesis |
|---|---|---|---|---|
| LLM-dominant | 40 | 5 | 5 | LLM controls the commons; do rule-based agents hit Nash equilibrium sooner? |
| LLM-equal | 15 | 15 | 15 | Equal start — does the LLM converge with rule-based agents at parity? |
| LLM-moderate | 25 | 15 | 5 | LLM starts large but not dominant |

### B. Inequality in full-GABM

| Experiment | Setup | What to test |
|---|---|---|
| Extreme inequality | Agent 0: 1, Agent 1: 5, Agent 2: 49 | Does severe inequality slow convergence? |
| Equal start | All agents: 18 cows | Does equal starting point change institution dynamics? |

**Research question:** Does initial herd size give an LLM agent economic leverage
to shift a hybrid equilibrium? Or is cognitive accessibility the binding constraint
regardless of initial endowment?

---

## V. Resource pressure

**No code changes needed — use existing sliders.**

| Experiment | Parameter change | What to test |
|---|---|---|
| Scarce commons | `initial-grassland=50` | Does scarcity accelerate institution emergence or accelerate collapse? |
| Abundant commons | `initial-grassland=100` + `initial-grass-growth-rate=0.005` | Slack resources — does cooperation still emerge under low pressure? |
| High forage demand | `cow-forage-requirement=5` | Faster degradation — does it sharpen LLM responses? |
| Low pressure | `cow-forage-requirement=1` | Slow degradation — does institution emergence slow too? |

**Research question:** Is Ostromian institution emergence a response to resource
pressure? Would agents cooperate without scarcity forcing the issue?

---

## VI. Memory and time horizon

**No code changes needed — use `memory-length` slider.**

| Experiment | `memory-length` | What to test |
|---|---|---|
| Amnesiac agents | 1 | Can cooperation emerge without memory? |
| Short memory | 3 | Partial memory — does it slow institution formation? |
| Default | 5 | Current baseline |
| Long memory | 10 | Does richer history strengthen institutions? |

**Research question:** How much memory does commons governance require? Is the
rolling 5-round window sufficient, or would longer memory change institution quality?

---

## VII. Personality and disposition (rule-based agents)

**No code changes needed — MASTOC personality sliders are already wired.**

The original MASTOC model includes disposition sliders for rule-based agents:
`fairness-concerning-others`, `cooperation-level`, `positive-reciprocity`,
`negative-reciprocity`, `risk-aversion-level`. These currently sit at their defaults.

| Experiment | Setup | What to test |
|---|---|---|
| High-fairness rule agents | `fairness-concerning-others=1.0` for rule agents | Do fairer rule-based agents cooperate more with the LLM? |
| Risk-averse rule agents | `risk-aversion-level=1.0` | Does risk aversion produce more conservative extraction? |
| Hybrid: 1 LLM + 1 fair + 1 defector | mixed dispositions | Can an LLM convert a fair-but-dumb agent while being overwhelmed by a defector? |

**Research question:** Do LLM and rule-based cooperative dispositions interact?
Can the right disposition parameterisation close the gap that language alone cannot?

---

## VIII. Communication experiments

**Requires small code changes.**

| Experiment | Change needed | What to test |
|---|---|---|
| Silent LLM | Suppress outgoing messages in bridge | Does reasoning-only (no communication) still produce cooperation? |
| One-way communication | Only agent 0 can send messages | Is receiving messages necessary, or is sending enough? |
| Delayed messages | Messages arrive N ticks late | Does communication latency degrade institution quality? |
| Message cap | Truncate to 20 words | Does less expressive communication impair institutions? |

**Research question:** How much of the full-GABM result depends on communication
vs. reasoning alone? Can agents cooperate without talking?

---

## IX. Recovery and long runs

**Requires minor parameter or code changes.**

| Experiment | Change needed | What to test |
|---|---|---|
| Post-collapse recovery | Run to 300 ticks | Can LLMs coordinate herd removal and wait for regeneration? |
| Forced regeneration | Modify NetLogo grass growth | If regeneration is faster, do LLMs exploit that? |
| Restart after collapse | Trigger new setup mid-run | Can agents rebuild institutions from scratch? |

**Research question:** Is the post-collapse LLM behaviour (holding at zero,
appealing for recovery norms) actually functional — does it enable regeneration
given enough time?

---

## X. Adversarial and mixed-intent

**Requires prompt engineering or small code changes.**

| Experiment | Setup | What to test |
|---|---|---|
| Instructed defector | System prompt tells one LLM to maximise cows | Do the other LLMs detect and adapt to a bad-faith agent? |
| Hidden defector | Defector claims to cooperate in messages but acts otherwise | Can LLMs detect deceptive signalling? |
| Model alignment gradient | Compare Claude Opus (high alignment) vs less-aligned model | Does training alignment correlate with commons cooperation? |

**Research question:** Are LLM cooperative tendencies robust to adversarial
framing? Can an agent be instructed to defect, and does the system detect it?

---

## Priority order for next runs

Given current infrastructure and research value, recommended sequence:

1. **Statistical replication** — 3 runs each of baseline, full-GABM, hybrid-1, hybrid-2 (high priority, needed for any claims)
2. **All-Haiku full-GABM** — cheapest cross-model test; validates whether result is model-specific
3. **LLM-advantaged hybrid-1** — tests economic leverage hypothesis with existing sliders
4. **Cross-provider full-GABM** — Claude + GPT-4o + Gemini in the same run
5. **Memory length sweep** — 1, 3, 5, 10 across full-GABM condition
6. **Scarce commons** — `initial-grassland=50`, full-GABM and hybrid-1
7. **Silent LLM** — requires one bridge change; high theoretical value
