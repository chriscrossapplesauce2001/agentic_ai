# PAOR Agent — Plan, Act, Observe, Reflect

An AI agent that answers questions by **thinking in steps** instead of guessing in one shot. It runs locally using [Ollama](https://ollama.com/) (no cloud API needed).

---

## How it works (for kids)

Imagine you ask a really smart robot: *"What formulas are in this file?"*

A normal robot would try to answer right away — and probably get it wrong, because it never looked at the file.

This robot is smarter. It works like you would in school:

1. **Plan** — "Okay, first I need to read the file, then find the formulas, then write them down." It writes a numbered checklist.
2. **Act** — It does **one step** from the checklist (like step 1: open the file).
3. **Observe** — It looks at what it got back. "Ah, here's the file contents!"
4. **Reflect** — It checks the list: "Step 1 is done, steps 2 and 3 are still pending. I need to keep going." Then it goes back to step 2 for the next item on the list.

That's the PAOR loop: **Plan, Act, Observe, Reflect**. It keeps going around the loop — one checklist item at a time — until every step is done (or it runs out of tries).

### The tools (helper arms)

The robot can't do everything in its head. It has three tools it can reach for:

| Tool | What it does |
|------|-------------|
| `web_search` | Searches the internet (like Googling something) |
| `calculator` | Does math (so it doesn't make arithmetic mistakes) |
| `read_file` | Opens and reads a text file |

Without these tools the robot could only guess. With them, it can **look things up and calculate**.

---

## How it works (technical)

### Architecture

```
main.py          Entry point — runs demo queries, then interactive REPL
agent.py         PAOR loop + Ollama streaming + tool dispatch
tools.py         Tool implementations (web search, calculator, file reader)
config.py        Loads settings from config.yaml
config.yaml      Model, context window, temperature, system prompt, demo queries
sample.txt       Example file the agent can read
```

### The PAOR loop (`agent.py`)

```
           +--------+
           |  PLAN  |  LLM creates a numbered step-by-step plan
           +---+----+
               |
        +------v------+
   +--->|     ACT     |  LLM picks a tool (or answers directly)
   |    +------+------+
   |           |
   |    +------v------+
   |    |   OBSERVE   |  Tool executes, result goes back into context
   |    +------+------+
   |           |
   |    +------v------+
   |    |   REFLECT   |  LLM decides: FINAL ANSWER / NEXT STEP / RE-PLAN
   |    +------+------+
   |        |     |
   |  next  |     | final
   +--------+     +-------> done
```

Each cycle executes exactly **one step** of the plan. The agent tracks a `current_step` index and advances it each cycle. The agent stops when:
- All steps are `[done]` and the LLM says "FINAL ANSWER" in the reflect phase
- All steps have been executed (step counter exceeds plan length)
- `MAX_PAOR_CYCLES` is reached (forced final answer)

A **safety guard** overrides premature "FINAL ANSWER" decisions: if the LLM says it's done but there are still `[pending]` steps, the agent forces a "NEXT STEP" and continues.

### But how does the LLM know which phase it's in?

**It doesn't.** The LLM has no internal state — it's just a text-completion engine. The *Python code* is the state machine, and it steers the LLM by sending a **different prompt for each phase**.

Here's what actually happens under the hood. The message history always starts like this:

```
 messages = [
     { role: "system",  content: "You are a thorough research assistant..." },
     { role: "user",    content: "What formulas are in sample.txt?" },
 ]
```

Now the Python code enters the **PLAN** phase. It doesn't modify `messages`. Instead it creates a **temporary copy** with an extra instruction tacked on:

```
 temporary = messages + [
     { role: "user", content: "Create a brief step-by-step plan (max 5 steps)..." }
 ]
```

It sends `temporary` to the LLM. The LLM sees the system prompt, the user's question, and "create a plan" — so it writes a plan. The Python code saves the LLM's response into the real `messages` **and** parses the numbered steps into a Python list using `_parse_plan()`:

```
 messages = [
     { role: "system",    content: "You are a thorough research assistant..." },
     { role: "user",      content: "What formulas are in sample.txt?" },
     { role: "assistant", content: "1. Read the file\n2. Extract formulas\n3. ..." },
 ]
 steps = ["Read the file", "Extract formulas", "..."]
 current_step = 0
```

Next, the Python code enters the **ACT** phase. Same trick — temporary prompt, not stored. But now it tells the LLM **exactly which step** to execute:

```
 temporary = messages + [
     { role: "user", content: "You are on step 1. The step is:\n  \"Read the file\"\nExecute ONLY this single step..." }
 ]
```

The LLM sees the plan it just wrote plus a specific step instruction, so it calls a tool (e.g. `read_file("sample.txt")`). Python executes the tool and adds both the tool call and its result to `messages`.

Then **REFLECT** — another temporary prompt, now with a **checklist** showing which steps are done:

```
 temporary = messages + [
     { role: "user", content: "Here is the plan with completion status:\n  1. [done] Read the file\n  2. [pending] Extract formulas\n  3. [pending] ...\nYou just completed step 1. Reply FINAL ANSWER, NEXT STEP, or RE-PLAN." }
 ]
```

The LLM sees which steps are `[done]` and which are `[pending]`, so it makes a grounded decision. If steps remain, it says "NEXT STEP". Python reads that text, parses the keyword, and decides the loop continues.

**The key insight:** each phase is just a different question asked to the same LLM with the same growing history. The Python `while` loop decides which question to ask next, and it parses the LLM's text response to decide what phase comes after. The LLM itself has no idea it's in a "state machine" — it just answers whatever it's asked. The step tracking and checklist give the LLM the **context it needs** to make good decisions, without requiring it to have memory.

This is called the **transient prompt** pattern: the steering instructions are used once and thrown away, so the message history stays clean (only real responses and tool results).

### Wait — how does Python know a phase is "done"?

It depends on the phase. Most are trivially simple:

| Phase | How Python knows it's done |
|-------|---------------------------|
| **PLAN** | Python calls the LLM **once**. Whatever text comes back = the plan. Python also parses it with `_parse_plan()` (regex for `1. ...`, `2. ...`) into a list of step strings. Done. Move to ACT. |
| **ACT** | Python calls the LLM once with tools available, telling it which specific step to execute. Ollama's response either contains `tool_calls` (a structured JSON field, not free text) or it doesn't. If yes → move to OBSERVE. If no → the step didn't need a tool. Either way, move to REFLECT. |
| **OBSERVE** | No LLM call at all. Python executes the tool function itself and appends the result. Purely deterministic. |
| **REFLECT** | This is the **only phase where the LLM's words control the next state.** Python builds a `[done]/[pending]` checklist and sends it to the LLM, then does a dumb string search on the response: |

```python
lower = content.lower()
if "final answer" in lower:      # just checking if these words appear in the text
    return "final"
elif "re-plan" in lower:
    return "replan"
return "next"                    # default: keep going
```

The reflect prompt explicitly asks the LLM to reply with one of three keywords ("FINAL ANSWER", "NEXT STEP", "RE-PLAN"). The LLM usually cooperates because it was trained to follow instructions — but it's not guaranteed. If the LLM rambles without saying any keyword, Python defaults to `"next"` and loops again. And if it loops too many times, `MAX_PAOR_CYCLES` forces a stop.

Even if the LLM says "FINAL ANSWER" prematurely, a **safety guard** in `run_agent()` catches it: if `current_step < len(steps)`, the decision is overridden to `"next"`, and the loop continues. This ensures the LLM can't short-circuit the plan.

**Bottom line:** the LLM never sees Python code. It never "knows" about phases. It just receives text messages and writes back text. All the control flow lives in Python — the LLM is just a very fancy text-completion function that Python calls repeatedly with different prompts.

### Does the model think before responding?

Yes. Every call to the LLM uses `think=True`:

```python
ollama.chat(model=model, messages=messages, stream=True, think=True, ...)
```

This tells Ollama to let the model produce **thinking tokens** (internal reasoning) before the actual response. When streaming, each chunk has two separate fields:

```python
msg.get("thinking", "")    # internal chain-of-thought (shown in console as [Thinking])
msg.get("content", "")     # the actual visible response (shown as [PLAN], [REFLECT], etc.)
```

**How do we know thinking is done?** We don't decide — the **model** decides. During training, the model learned to produce thinking tokens first, then switch to content tokens. Ollama separates them into two different fields. The sequence looks like this:

```
chunk 1:  { thinking: "Okay, the user wants me to..." }     ← still thinking
chunk 2:  { thinking: "I should read the file first..." }    ← still thinking
chunk 3:  { content: "1. Read sample.txt\n" }                ← thinking is over, now responding
chunk 4:  { content: "2. Extract formulas\n" }               ← still responding
(stream ends)                                                 ← response is done
```

Python just loops through the chunks and prints them. When `thinking` chunks stop and `content` chunks start, that's the switch. When the stream ends (the `for` loop exits), the full response is captured and the phase is complete. Python never needs to say "stop thinking" — the model handles that on its own.

**`/no_think` optimization:** ACT and REFLECT prompts begin with `/no_think`, a Qwen3 convention that tells the model to skip the internal reasoning phase and jump straight to the answer. These phases don't benefit from long chain-of-thought — ACT just needs to pick the right tool, and REFLECT just needs to pick a keyword. PLAN and FINAL ANSWER still use full thinking.

### Key design decisions

- **Transient prompts**: Phase instructions ("Create a plan...", "You are on step 2...") are passed to the LLM but **not stored** in the message history. Only real assistant responses and tool results stay in context — this keeps the conversation clean.
- **Step tracking**: `_plan()` parses the numbered plan into a Python list. Each cycle advances a `current_step` counter and tells `_act()` exactly which step to execute. `_reflect()` sees a `[done]/[pending]` checklist. This prevents the LLM from collapsing multiple steps into one or declaring "done" prematurely.
- **Safety guard**: If the LLM says "FINAL ANSWER" but `current_step < len(steps)`, Python overrides the decision to "NEXT STEP" and continues the loop.
- **`/no_think`**: ACT and REFLECT prompts start with `/no_think` to reduce verbose chain-of-thought in phases where deep reasoning isn't needed.
- **Streaming**: Plan, reflect, and final answer phases stream tokens live to the console. The act phase uses a non-streaming call because Ollama's streaming + tool-calling is unreliable.
- **Cycle safety**: The counter increments every loop iteration (not just on plan), so act-observe-reflect loops can't run forever.

### Before vs. After: why step tracking matters

The circular ring query — *"Compute the second moment of area for a circular ring with outer radius 5 cm and inner radius 3 cm using I = π/4 × (R⁴ − r⁴)"* — shows the difference clearly.

#### v1 — no step tracking

```
plan  = llm("Create a step-by-step plan")
while cycle < MAX:
    response = llm("Execute the next step of your plan",        # <-- which step??
                    tools=[search, calc, read_file])
    observe(response)
    decision = llm("Do you have enough info to answer?")        # <-- no checklist
    if "final answer" in decision:
        break                                                    # <-- no safety guard
```

```
Circular ring query — execution trace:

  PLAN   "1. Identify values  2. Compute R⁴  3. Compute r⁴  4. Subtract  5. Multiply by π/4"
    |
  ACT    LLM sees "execute the next step" — does ALL steps in its head
         calculator: never called
    |
  REFLECT "Do you have enough info?" — LLM says "yes" (nothing to contradict it)
    |
  FINAL ANSWER   after 1 cycle, wrong result (hallucinated arithmetic)
```

Root causes: ACT didn't say *which* step, so the LLM did everything at once. REFLECT had no checklist, so nothing contradicted a premature "done". No safety guard existed.

#### v2 — with step tracking

```
plan  = llm("Create a step-by-step plan")
steps = parse_plan(plan)                                         # <-- ["Identify values", "Compute R⁴", ...]
current_step = 0
while cycle < MAX and current_step < len(steps):
    response = llm(f"You are on step {current_step + 1}.\n"
                   f"The step is: \"{steps[current_step]}\"\n"
                   f"Execute ONLY this single step.",            # <-- exact step pointer
                    tools=[search, calc, read_file])
    observe(response)
    checklist = format_checklist(steps, current_step)            # <-- [done]/[pending] list
    decision  = llm(f"Plan status:\n{checklist}\n"
                    f"Reply FINAL ANSWER, NEXT STEP, or RE-PLAN.")
    if "final answer" in decision and pending_steps_remain():
        decision = "next"                                        # <-- safety guard override
    current_step += 1
```

```
Circular ring query — execution trace:

  PLAN    "1. Identify values  2. Compute R⁴  3. Compute r⁴  4. Subtract  5. Multiply by π/4"
    |
  ACT     step 1 → "Identify values: R=5cm, r=3cm"           (no tool needed)
  REFLECT [done] 1. Identify  [pending] 2-5                   → NEXT STEP
    |
  ACT     step 2 → calculator("5**4")                         → 625
  REFLECT [done] 1-2  [pending] 3-5                           → NEXT STEP
    |
  ACT     step 3 → calculator("3**4")                         → 81
  REFLECT [done] 1-3  [pending] 4-5                           → NEXT STEP
    |
  ACT     step 4 → calculator("625 - 81")                     → 544
  REFLECT [done] 1-4  [pending] 5                             → NEXT STEP
    |
  ACT     step 5 → calculator("3.14159265 / 4 * 544")         → 427.26...
  REFLECT [done] 1-5                                           → FINAL ANSWER
    |
  FINAL ANSWER   after 5 cycles, correct: I ≈ 427.3 cm⁴ (≈ 2.706 × 10⁻⁴ m⁴)
```

Same LLM, same tools, same model weights — only the prompts and control flow changed.

### Setup

```bash
# Prerequisites: Ollama running locally
ollama pull qwen3:0.6b

# In this directory
python -m venv .venv
source .venv/Scripts/activate   # Windows Git Bash
pip install -r requirements.txt
python main.py
```

### Configuration (`config.yaml`)

| Key | Default | Description |
|-----|---------|-------------|
| `model` | `qwen3:0.6b` | Ollama model name |
| `num_ctx` | `32768` | Context window (tokens) |
| `temperature` | `0.7` | Sampling temperature |
| `max_paor_cycles` | `10` | Max loop iterations before forced answer |
| `max_plan_steps` | `5` | Max steps the LLM should plan |
| `search_max_results` | `10` | DuckDuckGo results per search |
| `demo_queries` | *(list)* | Queries run automatically on startup |

---

## How does this compare to LangGraph?

LangGraph does the same thing conceptually — call an LLM in a loop, execute tools, route based on output. What it adds is production plumbing: a formal graph structure, typed state objects, checkpointing (save/restore mid-run), built-in streaming, and LangSmith tracing. You can get a working ReAct agent in ~3 lines with `create_react_agent()`.

**Why this project exists instead:** LangGraph hides the mechanics. Students call `create_react_agent()`, see it work, and have no idea *why*. When it breaks, they're stuck. With the raw approach, there's nothing to hide behind:

- The LLM is just a function: text in, text out
- Phases are just different prompts sent in a Python `while` loop
- Tools are just Python functions called between LLM calls
- The "agent" is ~50 lines of control flow

**Teaching order:** build it by hand first (this project), then introduce LangGraph to see what it abstracts away and what it gives you for free.

---

## References

1. **Plan-and-Solve Prompting** — Wang et al. (2023). *"Plan-and-Solve Prompting: Improving Zero-Shot Chain-of-Thought Reasoning by Large Language Models."* ACL 2023. Basis for parsing LLM-generated plans into individually executable steps. [[arXiv:2305.04091](https://arxiv.org/abs/2305.04091)]

2. **Inner Monologue** — Huang et al. (2023). *"Inner Monologue: Embodied Reasoning through Planning with Language Models."* CoRL 2023. Basis for grounded feedback — feeding success/failure signals (our `[done]/[pending]` checklist) back into the LLM so it can make informed decisions about what to do next. [[arXiv:2207.05608](https://arxiv.org/abs/2207.05608)]

3. **ReAct** — Yao et al. (2023). *"ReAct: Synergizing Reasoning and Acting in Language Models."* ICLR 2023. Basis for the one-action-per-cycle pattern and interleaving reasoning traces with tool use. [[arXiv:2210.03629](https://arxiv.org/abs/2210.03629)]
