---
name: netlogo
description: "Use this skill whenever working with NetLogo models — reading, writing, or patching .nlogo or .nlogox files; adding or modifying interface widgets (sliders, choosers, inputboxes, switches, monitors, plots); editing BehaviorSpace experiments; wiring up the Python extension (py:); integrating LLMs or external APIs into NetLogo agents; running headless simulations; or debugging 'Dimensions provided don't match' and other NetLogo file-format errors. Trigger this skill any time the user mentions NetLogo, .nlogo/.nlogox files, BehaviorSpace, NetLogo widgets, LLM-powered agents in NetLogo, or asks to modify a model's interface or code section programmatically."
---


# NetLogo Skill

This skill captures hard-won, production-tested knowledge about working with NetLogo 7.x
programmatically — including patching model files, managing widgets, running BehaviorSpace
experiments, and connecting NetLogo agents to external LLM APIs via the Python extension.

NetLogo's file format is deceptively strict — a single wrong field count or an empty line where
NetLogo expects a value will crash the model on load with an unhelpful "Dimensions provided don't
match" error. Read this skill fully before touching a .nlogo file.

---

## CRITICAL: Two file formats coexist in NetLogo 7

**NetLogo 7 introduced `.nlogox` as its primary format.** If a project contains both `.nlogo` and
`.nlogox`, the user is almost certainly opening the `.nlogox`. Always check which file is active
before patching — this is the single most common source of wasted effort.

| Format | Structure | When used |
|--------|-----------|-----------|
| `.nlogo` | 13 plain-text sections separated by `@#$#@#$#@` | Legacy; NetLogo 6 and earlier; still supported in 7 |
| `.nlogox` | XML (`<model>` root with `<code>`, `<widgets>`, `<experiments>` children) | **Default in NetLogo 7** — this is the live file |

**The trap:** it is easy to patch the `.nlogo` file, confirm the change in bash, and have the user
report seeing nothing — because NetLogo is loading the `.nlogox`. Before touching any file, run:

```bash
grep -n "variable-name-here" model.nlogo model.nlogox
```

Patch whichever file contains the current value.

---

## 1. .nlogox file format (NetLogo 7 native)

The `.nlogox` file is XML. The root element is `<model>`. Key children:

- `<code><![CDATA[ ... ]]></code>` — the full NetLogo code (procedures, globals, etc.)
- `<widgets>` — one child element per interface widget
- `<experiments>` — BehaviorSpace experiment definitions

### Patching `.nlogox` interface widgets

Widget elements use **attributes for all properties**, not newline-delimited fields. Elements are
**not self-closing** — they always use `<tag ...></tag>`, never `<tag .../>`.

**SLIDER:**
```xml
<slider x="680" step="1" y="684" max="10" width="208" display="memory-length"
        height="50" min="1" direction="Horizontal" default="5.0"
        variable="memory-length" units="rounds"></slider>
```

**SWITCH** (`on="true"` = ON by default; `on="false"` = OFF):
```xml
<switch x="247" y="753" height="40" on="true" variable="communication?"
        width="208" display="communication?"></switch>
```

**INPUTBOX:**
```xml
<inputBox x="8" y="996" width="208" height="80" variable="agent-prompt-override"
          multiline="true"></inputBox>
```

To patch, use **exact string replacement** — grep the file first to get the exact attribute string
(attribute order varies and must be matched exactly):

```python
import xml.etree.ElementTree as ET, shutil

src = "model.nlogox"
shutil.copy(src, src + ".bak")
with open(src) as f:
    raw = f.read()

# Extend a slider's range
old = '<slider x="680" step="1" y="684" max="10" width="208" display="memory-length" height="50" min="1" direction="Horizontal" default="5.0" variable="memory-length" units="rounds"></slider>'
new = old.replace('min="1"', 'min="0"').replace('max="10"', 'max="15"')
assert raw.count(old) == 1
raw = raw.replace(old, new, 1)

# Insert a new switch after an existing one
anchor = '<switch x="247" y="753" height="40" on="true" variable="detect-institutions" width="208" display="detect-institutions"></switch>'
new_switch = '<switch x="247" y="798" height="40" on="true" variable="communication?" width="208" display="communication?"></switch>'
assert raw.count(anchor) == 1
raw = raw.replace(anchor, anchor + "\n    " + new_switch, 1)

# Always validate XML before writing
ET.fromstring(raw)  # raises ParseError if malformed

with open(src, "w", encoding="utf-8") as f:
    f.write(raw)
```

**Widget y-placement:** set `y = existing_y + existing_height + gap` (gap ≈ 5px).
Typical heights: SWITCH=40, SLIDER=50, INPUTBOX=varies, CHOOSER=45.

**SWITCH variables are auto-declared as NetLogo globals** — no explicit `globals []` entry needed.
But the `py:set` bridge wiring is entirely manual (see section 6 below).

### Patching `.nlogox` code section

NetLogo code lives in `<code><![CDATA[ ... ]]></code>`. Use plain string replacement on the raw
text — the CDATA wrapper means the code is just text:

```python
old_code = '  py:set "cfg_verbose" verbose-mode\n  let status...'
new_code = '  py:set "cfg_verbose" verbose-mode\n  py:set "cfg_communication" communication?\n  let status...'
assert raw.count(old_code) == 1
raw = raw.replace(old_code, new_code, 1)
```

**After adding any new widget that needs to pass a value to Python**, you must do all three:
1. Add `py:set "cfg_varname" variable-name` in the code's setup procedure
2. Add `varname=cfg_varname` to the `bridge.configure(...)` call string
3. Add the parameter to the Python bridge's `configure()` function

Forgetting steps 1–2 in the `.nlogox` (while correctly adding them to `.nlogo`) is the most
common cause of new flags silently having no effect.

---

## 2. .nlogo file format (legacy, NetLogo 6)

A `.nlogo` file is **13 plain-text sections** separated by the sentinel `@#$#@#$#@` (alone on its
own line). Section indices:

| # | Contents |
|---|---|
| 0 | NetLogo code (procedures) |
| 1 | Interface (widget definitions, one per block) |
| 2 | Info tab (markdown) |
| 3 | Turtle shapes |
| 4 | Model metadata (version, etc.) |
| 5 | NetLogo Web settings |
| 6 | Link shapes |
| 7 | BehaviorSpace XML |
| 8 | System Dynamics Modeler |
| 9 | HubNet client |
| 10 | Delta tick |
| 11 | Preview commands |
| 12 | Empty (trailing newline) |

### Splitting and reassembling

```python
SENTINEL = "@#$#@#$#@"

with open("model.nlogo", "r", encoding="utf-8") as f:
    raw = f.read()

raw = raw.replace("\x00", "")  # strip null bytes (OneDrive corruption defence)

sections = raw.split(SENTINEL)
# sections[0] = code, sections[1] = interface, sections[7] = BehaviorSpace

new_content = SENTINEL.join(sections)
with open("model.nlogo", "w", encoding="utf-8", newline="\n") as f:
    f.write(new_content)
```

Always use `newline="\n"` on write — Windows line endings corrupt the file.

---

## 3. Interface section widget formats (.nlogo only)

Each widget is a **newline-delimited block** followed by a **blank line**. The field count must be
exact — NetLogo counts newlines to find field boundaries.

### SLIDER — 14 lines

```
SLIDER
x1
y1
x2
y2
display-name
variable-name
minimum
maximum
default-value
increment
decimal-places
units
HORIZONTAL
```

### CHOOSER — 9 lines

```
CHOOSER
x1
y1
x2
y2
display-name
variable-name
"option1" "option2" "option3"
selected-index
```

### INPUTBOX — 9 lines

```
INPUTBOX
x1
y1
x2
y2
variable-name
default-value
multiline-flag
hidden-flag
String
```

**CRITICAL:** `default-value` must not be a blank line — use a single space `" "` instead.

### SWITCH — 10 lines

```
SWITCH
x1
y1
x2
y2
variable-name
variable-name
on-value
1
-1000
```

Variable name appears **twice**. `on-value`: `0` = ON, `1` = OFF (inverted!).

### BUTTON — 14 lines | MONITOR — 10 lines | OUTPUT — 6 lines

See NetLogo documentation for less-common widget formats.

---

## 4. Coordinate system

- Origin (0, 0) is **top-left** of the interface canvas.
- x increases rightward, y increases downward.
- Leave ~5–10 px gap between rows.

---

## 5. BehaviorSpace XML

In `.nlogo`: section 7. In `.nlogox`: `<experiments>` element.

String values in `enumeratedValueSet` must use `&quot;` not raw `"`:

✓ Correct: `<value value="&quot;baseline&quot;"/>`

---

## 6. Python extension (py:)

```netlogo
extensions [py]

to setup-python
  py:setup py:python3
  py:run "import sys, os"
  py:run "sys.path.insert(0, os.getcwd())"
  py:run "import mymodule"
end
```

```netlogo
py:set "varname" some-netlogo-variable
let result py:runresult "mymodule.get_value()"
```

**Missing packages:** `pip install X` in the Python environment NetLogo uses. Find it with:
`show py:runresult "import sys\nsys.executable"`

---

## 7. Integrating LLMs into NetLogo agents

This section covers the general architecture for replacing or augmenting rule-based NetLogo agents
with LLM-powered decision-making. The pattern works with any LLM API (Anthropic, OpenAI, Google
Gemini, Ollama, etc.) and any ABM that produces per-agent observations each tick.

### Architecture overview

```
NetLogo (model tick)
        │  per-agent context (state variables, neighbours, history)
        ▼
Python bridge (imported via py: extension)
        │  prompt construction + rolling memory + API call
        ▼
LLM API  ←  Anthropic | OpenAI | Google | Ollama (local)
        │  structured JSON response: { action, reasoning, message }
        ▼
NetLogo  ←  action applied; optional message passed to neighbours
```

### Minimal NetLogo side

In your model's `go` procedure, for each LLM agent:

```netlogo
; Pass current state to Python and get an action back
let obs (list pool-pct my-herd neighbour-herds payoff-estimates)
py:set "agent_obs" obs
py:set "agent_id" who
let decision py:runresult "bridge.decide(agent_id, agent_obs)"
; decision is a list: [action reasoning message]
let action item 0 decision
```

Keep the NetLogo side thin — it passes observations and receives actions. All prompt construction,
memory management, and API calls live in the Python bridge.

### Python bridge structure

A minimal bridge module (`bridge.py`):

```python
import json, os
from collections import deque

# Rolling memory per agent
_memory: dict[int, deque] = {}
_cfg: dict = {}

def configure(**kwargs):
    """Called once from NetLogo setup to pass slider values."""
    global _cfg
    _cfg = kwargs
    memory_len = int(kwargs.get("memory_length", 5))
    for aid in range(int(kwargs.get("n_agents", 3))):
        _memory[aid] = deque(maxlen=memory_len)

def decide(agent_id: int, obs: list) -> list:
    """Main entry point — called each tick per agent."""
    aid = int(agent_id)
    _memory[aid].append(obs)
    prompt = _build_prompt(aid, obs)
    response = _call_llm(prompt)
    return [response["action"], response.get("reasoning", ""), response.get("message", "")]

def _build_prompt(aid: int, obs: list) -> str:
    memory_text = "\n".join(str(m) for m in _memory[aid])
    return f"""You are agent {aid}. Current state: {obs}.
Your recent history:
{memory_text}
Respond with JSON: {{"action": <your_action>, "reasoning": "<why>", "message": "<60-word msg to neighbours>"}}"""

def _call_llm(prompt: str) -> dict:
    backend = _cfg.get("backend", "anthropic")
    if backend == "anthropic":
        import anthropic
        client = anthropic.Anthropic()
        resp = client.messages.create(
            model=_cfg.get("model", "claude-sonnet-4-6"),
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}]
        )
        return json.loads(resp.content[0].text)
    elif backend == "openai":
        from openai import OpenAI
        client = OpenAI()
        resp = client.chat.completions.create(
            model=_cfg.get("model", "gpt-4o-mini"),
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(resp.choices[0].message.content)
    elif backend == "ollama":
        import requests
        resp = requests.post("http://localhost:11434/api/generate", json={
            "model": _cfg.get("model", "llama3"),
            "prompt": prompt + "\nRespond with valid JSON only.",
            "stream": False
        })
        return json.loads(resp.json()["response"])
    else:
        raise ValueError(f"Unknown backend: {backend}")
```

### Wiring configure() from NetLogo

In the NetLogo setup procedure, pass all relevant slider values to `bridge.configure()`:

```netlogo
to setup-python
  py:setup py:python3
  py:run "import sys, os"
  py:run "sys.path.insert(0, os.getcwd())"
  py:run "import bridge"
  ; Pass slider values as keyword arguments
  let cfg_str (word
    "bridge.configure("
    "backend='" backend "', "
    "model='" model-name "', "
    "memory_length=" memory-length ", "
    "n_agents=" count turtles
    ")")
  py:run cfg_str
end
```

### Key design decisions

**What to put in the prompt.** Include only what an agent would plausibly know: its own state,
observable neighbour state, and its own history. Giving all agents full global information removes
the interesting emergent dynamics. Decide deliberately what each agent can observe.

**Structured output.** Always request a specific JSON schema. LLMs reliably produce structured
output when the schema is explicit. Use `json.loads()` with a try/except to catch malformed
responses and retry or fall back to a default action.

**Rolling memory.** A `deque(maxlen=N)` gives agents an N-tick window of history — a key
experimental lever. `maxlen=0` produces amnesiac agents; larger values enable trend detection.

**Per-agent configuration.** If you want different agents to use different models or backends,
store configuration per agent-id in the bridge and pass `agent_id` in each `py:set` call.

**Ollama (local models).** Ollama requires no API key. Run `ollama serve` and `ollama pull
modelname` before launching NetLogo. Useful for cost-free pilot runs and offline experiments.

**Cost estimation.** Before a long BehaviorSpace sweep, estimate API cost:
```python
# Rough estimate: (ticks × agents × avg_tokens_per_call) × price_per_token
ticks, agents, tokens = 120, 3, 800
cost = ticks * agents * tokens * 3e-6  # ~$3/M tokens for mid-tier models
print(f"Estimated cost: ${cost:.2f}")
```

---

## 8. Common errors and fixes

### Widget changes not visible after patching

**Cause:** Patches went to `.nlogo` but the user has `.nlogox` open (or vice versa).

**Fix:** Grep both files for the widget variable name. Patch the right file, then ask the user
to close and reopen it in NetLogo — interface changes are not hot-reloaded from disk.

### New switch variable has no effect on Python bridge

**Cause:** `py:set "cfg_varname" variable-name` was added to `.nlogo` but not to the `.nlogox`
code section (the active file). Bridge defaults to its own default value silently.

**Fix:** Grep the `.nlogox` `<code>` block for the `py:set` line. If missing, add it to the
CDATA section and also add the parameter to the `bridge.configure()` call string.

### "Dimensions provided don't match" (`.nlogo` only)

**Cause:** Field count mismatch. Most often INPUTBOX with blank default value.

**Fix:** Replace empty default with a single space `" "`. Rewrite with `newline="\n"`.

### "WITH expected true/false, got 0"

**Cause:** Boolean variable set from numeric context.

**Fix:** Use `set flag false` / `set flag true` explicitly.

### Null bytes in file (OneDrive corruption)

**Fix:** `raw = raw.replace("\x00", "")`

### pynetlogo incompatible with NetLogo 7.x

**Workaround:** Run BehaviorSpace via GUI, or use headless.jar via subprocess.

### LLM returns malformed JSON

**Fix:** Wrap `json.loads()` in a try/except. On failure, log the raw response and return a safe
default action. For Ollama models, add `"Respond with valid JSON only."` at the end of the prompt.

### Linux mount sync lag (cloud-synced folders)

Bash may cache a stale version of a file for seconds or minutes after a write from file tools.
Symptoms: `wc -l` or `ast.parse` in bash report an old/truncated file even after a successful write.

**The file tool (Windows/Mac path) is always authoritative.** If bash and the file tool disagree,
trust the file tool.

Workarounds:
- Apply patches via `python3 -c` in bash (opens a fresh handle each call).
- Use `dd if=<file> of=/tmp/copy` to attempt a page-cache bypass.

---

## 9. Quick reference

| Widget (.nlogo) | Lines before blank |
|-----------------|-------------------|
| SLIDER | 14 |
| CHOOSER | 9 |
| INPUTBOX | 9 (default must NOT be empty!) |
| SWITCH | 10 |
| BUTTON | 14 |
| MONITOR | 10 |
| OUTPUT | 6 |

| Widget (.nlogox) | Key attributes |
|-----------------|----------------|
| `<slider>` | `variable`, `min`, `max`, `default`, `step`, `direction`, `units`, `x`, `y`, `width`, `height` |
| `<switch>` | `variable`, `display`, `on` (`"true"`/`"false"`), `x`, `y`, `width`, `height` |
| `<inputBox>` | `variable`, `multiline`, `x`, `y`, `width`, `height` |
| `<chooser>` | `variable`, `display`, `value` (current choice), `x`, `y`, `width`, `height`; choices as `<choice>` children |

| LLM backend | Import | Key call |
|-------------|--------|----------|
| Anthropic | `anthropic.Anthropic()` | `.messages.create(model=..., messages=[...])` |
| OpenAI | `openai.OpenAI()` | `.chat.completions.create(model=..., messages=[...], response_format={"type":"json_object"})` |
| Google Gemini | `google.generativeai` | `genai.GenerativeModel(model).generate_content(prompt)` |
| Ollama (local) | `requests` | `POST http://localhost:11434/api/generate` |
