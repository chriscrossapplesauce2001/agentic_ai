#!/usr/bin/env python3
"""Generate dummy student home dirs for testing the whole grading pipeline safely.

Creates three fake students under demo/homes/ (owned by you, NOT real /home/jupyter-*),
each with an Exercise 1 (free-text) and Exercise 2 (code) notebook:

    jupyter-perfect  all answers correct   + all 4 code TODOs solved   -> should score high
    jupyter-half     ~half the answers     + 2 of 4 code TODOs solved  -> should score ~50%
    jupyter-weak     mostly wrong/missing  + 0 code TODOs solved        -> should score low

Run it once:  python3 demo/make_demo_homes.py
Then in the grading console tick "Demo mode" and use the normal buttons: it grades these
instead of real students, with no sudo and no risk. (Free-text scores depend on the judge
model; the code exercise is deterministic, so 4/4, 2/4, 0/4 are guaranteed.)
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
HOMES = os.path.join(HERE, "homes")

# ---- Exercise 1 correct answers (core points from SOLUTION_KEY.md) ----
CORRECT = {
    "P1.Q1": "The reasoning block (<think>...</think>) disappears and the output starts directly "
             "with the answer. The <think> prefill is what triggers thinking mode in the first place.",
    "P1.Q2": "Yes, it keeps generating. A text instruction stops nothing; generation is stopped by a "
             "stop token (<|im_end|>/EOS) from the chat template. With raw=True and no template there "
             "is no stop token.",
    "P2.Q1": "Yes, it still knows the name. The fact is in the first user message, which is still "
             "present; the assistant echo is not needed. The model only knows what is in messages.",
    "P2.Q2": "Anna. The model has no memory of its own and trusts the supplied history even when it is "
             "fabricated. This is the seed of prompt injection.",
    "P2.Q3": "Yes, it answers Max; system content is part of the context. Instructions and stable "
             "facts go in the system message (first, standing/higher weight), while mid-conversation "
             "facts belong in user turns. All roles are just text; the role is a durability convention.",
    "P3.Q1": "For this obvious task it usually still calls the tool because the name and schema are "
             "enough, but the description is the main signal for when a tool is used, so emptying it "
             "makes tool use less reliable, especially for ambiguous tasks.",
    "P3.Q2": "For trivial math it often answers directly (content filled, tool_calls empty). The model "
             "decides for itself whether a tool is worth using.",
    "P3.Q3": "KeyError: 'math_thing' at func = tool_map[tc.function.name]. The tool name in the "
             "definition must match the key in tool_map; they are linked only via the string name.",
    "P4.Q1": "The history becomes inconsistent: a tool message with no preceding assistant tool_calls, "
             "so the result is wrong/confused or the tool gets called again. Both messages must be "
             "appended in order: first the assistant with tool_calls, then the tool result.",
    "P4.Q2": "Both are valid (one combined (17*23)/2 or two sequential calls). The while loop is needed "
             "because the model can chain several tool calls across iterations; the cap prevents an "
             "infinite loop.",
    "P4.Q3": "No, the calculator is not touched. content is the joke and tool_calls is empty. Providing "
             "tools does not force their use; the model chooses per request.",
}
WRONG = {
    "P1.Q1": "Nothing really changes, the answer looks the same.",
    "P2.Q1": "No, it forgets the name completely because the assistant message is gone.",
}

# ---- Exercise 2 run_agent code, with a controllable number of TODOs solved ----
def run_agent_code(todos_done):
    lines = ["def run_agent(query):", "    messages = [{'role':'user','content':query}]", "    while True:"]
    if todos_done >= 1:
        lines.append("        response = ollama.chat(model='m', messages=messages, tools=tools)")
        lines.append("        msg = response.message")
    else:
        lines.append("        # TODO1: call the model")
        lines.append("        msg = None")
    if todos_done >= 2:
        lines.append("        if msg.tool_calls:")
    else:
        lines.append("        if False:  # TODO2: detect tool calls")
    if todos_done >= 3:
        lines += ["            for call in msg.tool_calls:",
                  "                func = tool_map[call.function.name]",
                  "                result = func(**call.function.arguments)",
                  "                messages.append({'role':'tool','content':str(result)})",
                  "            continue"]
    else:
        lines.append("            pass  # TODO3: run the tool and append the result")
    if todos_done >= 4:
        lines.append("        final_answer = msg.content")
        lines.append("        return final_answer")
    else:
        lines.append("        return None  # TODO4: read the final answer")
    return "\n".join(lines)


def nb(cells):
    return {"cells": cells, "metadata": {}, "nbformat": 4, "nbformat_minor": 5}

def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": text}

def code(src):
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": src}

def ex1(answers):
    body = "\n\n".join(f"{qid}: {txt}" for qid, txt in answers.items())
    return nb([md("# Exercise 1 - Answers\n"), md(body)])

def ex2(todos_done):
    return nb([md("# Exercise 2 - ReAct loop\n"), code(run_agent_code(todos_done))])

def write(user, ex1_nb, ex2_nb):
    base = os.path.join(HOMES, f"jupyter-{user}", "agentic_ai", "lab01")
    for ex, data in (("exercise1", ex1_nb), ("exercise2", ex2_nb)):
        os.makedirs(os.path.join(base, ex), exist_ok=True)
        json.dump(data, open(os.path.join(base, ex, f"{ex}.ipynb"), "w"), indent=1)
    print(f"  wrote jupyter-{user}")


def main():
    print(f"Generating demo homes under {HOMES}")
    write("perfect", ex1(CORRECT), ex2(4))
    half = {k: v for k, v in CORRECT.items() if k in ("P1.Q1", "P2.Q1", "P2.Q3", "P3.Q3", "P4.Q1", "P4.Q3")}
    write("half", ex1(half), ex2(2))
    write("weak", ex1(WRONG), ex2(0))
    print("Done. In the console tick 'Demo mode' and click the buttons.")


if __name__ == "__main__":
    main()
