import sys
import json
import ollama

sys.stdout.reconfigure(encoding="utf-8")
from tools import tool_map
from config import MODEL, NUM_CTX, TEMPERATURE, MAX_PAOR_CYCLES, MAX_PLAN_STEPS, SYSTEM_PROMPT

# Ollama tool definitions -- manual schemas matching the Python functions
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for current information. Returns snippets with source URLs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query string",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": (
                "Calculate a math expression. Input must be a valid math expression "
                "like '2 + 2' or '(3.14 * 0.2 * 0.4**3) / 12'. "
                "Supports +, -, *, /, **, sqrt, sin, cos, log, pi, e."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "The math expression to evaluate",
                    }
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": (
                "Read a local text file. Only files in the project directory can be read."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "The filename to read, e.g. 'sample.txt'",
                    }
                },
                "required": ["filename"],
            },
        },
    },
]

_OLLAMA_OPTS = {"num_ctx": NUM_CTX, "temperature": TEMPERATURE}


def stream_ollama_response(model, messages, tools=None, label="Answer"):
    """Stream an ollama.chat response, printing [Thinking] and [label] live.

    Returns (full_thinking, full_content, tool_calls_list) for history.
    """
    kwargs = dict(model=model, messages=messages, stream=True, think=True,
                  options=_OLLAMA_OPTS)
    if tools:
        kwargs["tools"] = tools

    full_thinking = ""
    full_content = ""
    tool_calls = []
    in_thinking = False
    in_content = False

    for chunk in ollama.chat(**kwargs):
        msg = chunk.get("message", {})

        thinking = msg.get("thinking", "")
        if thinking:
            if not in_thinking:
                print("\n  [Thinking]", flush=True)
                in_thinking = True
            print(thinking, end="", flush=True)
            full_thinking += thinking

        content = msg.get("content", "")
        if content:
            if not in_content:
                if in_thinking:
                    print()
                print(f"\n  [{label}]", flush=True)
                in_content = True
            print(content, end="", flush=True)
            full_content += content

        tc = msg.get("tool_calls")
        if tc:
            tool_calls.extend(tc)

    if in_thinking or in_content:
        print()

    return full_thinking, full_content, tool_calls


# ---------------------------------------------------------------------------
# Phase helpers — each receives the shared `messages` list.
# Orchestration prompts are passed transiently (not stored in history).
# Only real LLM responses and tool results are appended to `messages`.
# ---------------------------------------------------------------------------

def _transient(messages, prompt):
    """Return messages + a transient user prompt (original list unchanged)."""
    return messages + [{"role": "user", "content": prompt}]


def _parse_plan(plan_text: str) -> list[str]:
    import re
    steps = re.findall(r'^\s*\d+[\.\)]\s*(.+)', plan_text, re.MULTILINE)
    return steps if steps else [plan_text.strip()]


def _plan(messages):
    """PLAN phase: ask the LLM for a step-by-step plan. Returns parsed steps."""
    prompt = (
        "Create a brief step-by-step plan to answer the user's question. "
        "Use as few steps as necessary — simple questions may need only 1-2 steps. "
        "Number each step as '1. ...', '2. ...' etc. "
        "Do NOT execute any steps yet — only list them."
    )
    _, content, _ = stream_ollama_response(
        MODEL, _transient(messages, prompt), label="PLAN"
    )
    messages.append({"role": "assistant", "content": content})
    return _parse_plan(content)


def _act(messages, step_number: int, step_text: str):
    """ACT phase: execute a specific step, possibly calling a tool.

    Returns True if a tool was called (proceed to observe), False otherwise.
    """
    prompt = (
        f"/no_think\n"
        f"You are on step {step_number}. The step is:\n"
        f"  \"{step_text}\"\n"
        f"Execute ONLY this single step. Use a tool if a computation or lookup is needed. "
        f"Do NOT skip ahead to later steps."
    )
    # Non-streaming call with tools (streaming + tools unreliable in Ollama)
    response = ollama.chat(
        model=MODEL, messages=_transient(messages, prompt),
        tools=TOOLS, think=True, options=_OLLAMA_OPTS
    )
    msg = response["message"]

    if msg.get("tool_calls"):
        thinking = msg.get("thinking", "")
        if thinking:
            print(f"\n  [Thinking]\n  {thinking}")
        print(f"\n  [ACT]")
        messages.append(msg)
        for tc in msg["tool_calls"]:
            name = tc["function"]["name"]
            args = tc["function"]["arguments"]
            print(f"  Tool call: {name}({json.dumps(args)})")
        return True
    else:
        content = msg.get("content", "")
        messages.append({"role": "assistant", "content": content})
        return False


def _observe(messages):
    """OBSERVE phase: execute tool calls and append results."""
    last_msg = messages[-1]
    tool_calls = last_msg.get("tool_calls", [])

    for tc in tool_calls:
        name = tc["function"]["name"]
        args = tc["function"]["arguments"]

        func = tool_map.get(name)
        if func is None:
            result = f"Error: Unknown tool '{name}'"
        else:
            try:
                result = func(**args)
            except Exception as exc:
                result = f"Error calling '{name}': {exc}"

        print(f"\n  [OBSERVE]")
        if len(result) > 500:
            print(f"  Tool: {name} -> {result[:500]}... (truncated)")
        else:
            print(f"  Tool: {name} -> {result}")

        messages.append({"role": "tool", "content": result})


def _reflect(messages, steps: list[str], current_step: int):
    """REFLECT phase: decide next action. Returns 'final', 'replan', or 'next'."""
    checklist = ""
    for i, step in enumerate(steps, 1):
        marker = "[done]" if i <= current_step else "[pending]"
        checklist += f"  {i}. {marker} {step}\n"

    prompt = (
        f"/no_think\n"
        f"Here is the plan with completion status:\n{checklist}\n"
        f"You just completed step {current_step}. "
        f"Review the tool result above. Did step {current_step} succeed?\n"
        f"Reply with EXACTLY one keyword on the FIRST line:\n"
        f"- NEXT STEP — if there are pending steps remaining\n"
        f"- FINAL ANSWER — ONLY if ALL steps are [done] and results are sufficient\n"
        f"- RE-PLAN — if the approach needs to change\n"
        f"Then one sentence explaining why."
    )
    _, content, _ = stream_ollama_response(
        MODEL, _transient(messages, prompt), label="REFLECT"
    )
    messages.append({"role": "assistant", "content": content})

    lower = content.lower()
    if "final answer" in lower:
        return "final"
    elif "re-plan" in lower or "replan" in lower:
        return "replan"
    return "next"


def _final_answer(messages, forced=False):
    """Generate and stream the final answer."""
    if forced:
        prompt = (
            "You have reached the maximum number of cycles. "
            "Provide your best answer now with whatever information you have."
        )
    else:
        prompt = "Provide your complete final answer to the user's question."
    stream_ollama_response(
        MODEL, _transient(messages, prompt), label="FINAL ANSWER"
    )


# ---------------------------------------------------------------------------
# Main agent loop
# ---------------------------------------------------------------------------

def run_agent(user_input: str):
    """Run the PAOR agent loop with live streaming output."""
    print(f"\n{'='*60}")
    print(f"  QUESTION: {user_input}")
    print(f"{'='*60}")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_input},
    ]

    cycle = 0
    steps = []
    current_step = 0
    need_plan = True

    while cycle < MAX_PAOR_CYCLES:
        cycle += 1
        print(f"\n  --- CYCLE {cycle} ---")

        if need_plan:
            steps = _plan(messages)
            current_step = 0
            need_plan = False

        current_step += 1
        if current_step > len(steps):
            _final_answer(messages)
            break

        used_tool = _act(messages, current_step, steps[current_step - 1])

        if used_tool:
            _observe(messages)

        decision = _reflect(messages, steps, current_step)

        # Safety guard: override premature FINAL ANSWER
        if decision == "final" and current_step < len(steps):
            print(f"  (Override: {current_step}/{len(steps)} steps done — continuing)")
            decision = "next"

        if decision == "final":
            _final_answer(messages)
            break
        elif decision == "replan":
            need_plan = True
        # "next" -> loop continues with next cycle
    else:
        # Max cycles exceeded — force a final answer
        print(f"\n  (max cycles reached, forcing final answer)")
        _final_answer(messages, forced=True)

    print(f"\n  ({cycle} cycle(s))")
    print(f"{'='*60}\n")
