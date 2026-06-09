# Solution Key Lab 01 — Scoring Rubric

**Internal, do not distribute to students.** Reference for the automatic scoring. Per question: `✓` core point (must be present), `±` also acceptable / model-dependent, `✗` typical mistake. The grader labels each question **correct / partial / incorrect** based on the core point, not the exact wording.

---

## Exercise 0 — How an LLM API Call Works (free text, LLM-graded)

### Part 1: A Single LLM Call

**Q1 — Remove `<think>\n`: what disappears?**
- ✓ The reasoning/thinking block (`<think>...</think>`) disappears; output starts directly with the answer.
- ✓ The `<think>` prefill is what triggers thinking mode.

**Q2 — Prompt "Answer once, then stop ...": does it keep going? What actually stops generation?**
- ✓ Yes, it keeps going. A text instruction stops nothing.
- ✓ Generation is stopped by a stop token (`<|im_end|>` / EOS) from the chat template, not by the prompt content. `raw=True` with no template = no stop token.
- ✗ "The model ignored the instruction / does not understand it" without the stop-token point.

### Part 2: Statelessness

**Q1 — Remove the `assistant` entry: does the model still know the name? Why?**
- ✓ Yes. The fact is in the first user message, which is still there. The assistant echo is not needed.
- ✓ Core: the model only knows what is in `messages`; the history just has to *contain* the fact.

**Q2 — Replace `r1.message.content` with "Nice to meet you, Anna!": which name?**
- ✓ Anna. The model has no memory of its own; it trusts the supplied history even when it is fabricated.
- ✓ Bonus: this is the seed of prompt injection.

**Q3 — Move the fact into the `system` message: does it work? Which role for instructions / stable facts, and why different from mid-conversation facts?**
- ✓ Yes, the model answers "Max"; system content is part of the context.
- ✓ Instructions + stable facts conventionally go in `system` (first, weighted higher / standing); what the user says during the dialogue belongs in `user` turns.
- ✓ Core: all roles are just text; the role is a (training-reinforced) convention for durability/authority.

### Part 3: Tool Calling

**Q1 — Empty the `description`: does the model still call the tool?**
- ± Model-dependent; for this obvious task usually yes (name + schema are enough).
- ✓ Core: the description is the main signal for *when* a tool is used; empty = less reliable, especially for ambiguous tasks.
- Grading: both observed outcomes are fine as long as "description = routing signal" is recognized.

**Q2 — Prompt "What is 2 + 2?": tool or direct answer? `content` vs `tool_calls`?**
- ± Model-dependent; for trivial math often a direct answer (`content` filled, `tool_calls` empty/None).
- ✓ Core: the model decides for itself whether a tool is worth it.

**Q3 — Rename the tool to `"math_thing"` in the definition, leave `tool_map` unchanged: error + line?**
- ✓ `KeyError: 'math_thing'` at `func = tool_map[tc.function.name]`.
- ✓ Core: the tool name in the definition must match the key in `tool_map`; they are linked only via the string name.

### Part 4: Tool-Use Loop

**Q1 — Remove `messages.append(response.message.model_dump())` (tool result stays): final answer?**
- ✓ The history becomes inconsistent: a `tool` message with no preceding assistant `tool_calls`. Result is wrong/confused, or the tool gets called again.
- ✓ Core: both messages must go in, in order: first the assistant with `tool_calls`, then the `tool` result.

**Q2 — "... then divide the result by 2." with a `while` loop (cap 5): one combined or two sequential calls?**
- ± Both valid: one call `(17*23)/2` OR two calls (`17*23` → 391 → `391/2`).
- ✓ Core: the `while` loop is needed because the model can chain several tool calls across iterations; the cap prevents an infinite loop.

**Q3 — Prompt "Tell me a short joke." (tools still provided): calculator touched?**
- ✓ No. `content` = joke, `tool_calls` empty/None.
- ✓ Core: providing tools does not force their use; the model chooses per request whether a tool is relevant.

---

## Exercise 1 — ReAct loop (code, deterministically graded, no LLM needed)

**TODO 1** `response = ollama.chat(model=MODEL, messages=messages, tools=TOOLS, options={"num_ctx": NUM_CTX, "temperature": TEMPERATURE})`

**TODO 2** `if msg.get("tool_calls"):` (also: `is not None`, or a truthiness check)

**TODO 3**
```python
func = tool_map[name]
result = func(**args)
messages.append({"role": "tool", "content": result})
```

**TODO 4** `final_answer = msg["content"]` (also: `msg.get("content", "")`)

**Expected test behavior** (sanity check):
- Test 1 `(0.2 * 0.4**3) / 12`: one `calculator` call, ≈ `0.0010667` m⁴.
- Test 2 `sample.txt`: one `read_file` call, answer names the formulas.
- Test 3 `Young's modulus S235`: one `web_search` call, answer names ~210 GPa.

---

## Exercise 2 — LangChain

**Open:** `exercise2.ipynb` does not exist yet. Rubric follows once it is built. Core: the same agent via `create_react_agent()` + `@tool` functions, functionally identical to Exercise 1, with noticeably less code.
