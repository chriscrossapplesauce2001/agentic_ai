#!/usr/bin/env python3
"""Generate 3 fake Exercise-1 student submissions of varying quality, for a grading demo.

Each is a minimal .ipynb whose answer cells carry `P<part>.Q<n>:` tags, exactly the format
the grader extracts. An empty value (e.g. "P2.Q3:") models a student who left a stub blank
(scored `missing`). Run: python3 _make_submissions.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

# qid -> answer text. "" = stub left blank (missing). Quality is intentional, see comments.
STUDENT_A = {  # strong: hits the core points
    "P1.Q1": "The <think>...</think> reasoning block disappears and the output starts directly with the answer. The <think> prefill is what triggers thinking mode.",
    "P1.Q2": "It keeps generating. A text instruction stops nothing; generation only stops when a stop token like <|im_end|> from the chat template is emitted.",
    "P1.Q3": "thinking is empty and content holds the entire answer, because both are parsed from one text stream and without a <think> block everything ends up in content.",
    "P2.Q1": "Yes, because the name is still in the first user message. The model only knows what is in messages; the assistant echo is not needed.",
    "P2.Q2": "It says Anna. The model has no memory of its own and trusts the history we pass in, even if it is fabricated. This is prompt injection in miniature.",
    "P2.Q3": "Yes, it answers Max. System content is part of the context. System is the convention for instructions and stable facts (standing, higher authority); what is said during the dialogue goes in user turns. All roles are ultimately just text.",
    "P3.Q1": "Model dependent, but for this obvious task it usually still calls the tool since name and schema are enough. The description is the main signal for when to use a tool, so emptying it makes it less reliable on ambiguous tasks.",
    "P3.Q2": "It answers directly without the tool: content is filled and tool_calls is empty. The model decides for itself whether a tool is worth it.",
    "P3.Q3": "KeyError: 'math_thing' at func = tool_map[tc.function.name], because the tool name in the definition must match the key in tool_map.",
    "P4.Q1": "The history becomes inconsistent: a tool message with no preceding assistant tool_calls. The result is wrong or the tool gets called again. Both messages must be appended, in order.",
    "P4.Q2": "Could be one call (17*23)/2 or two sequential calls. The while loop is needed so the model can chain tool calls over iterations, and the cap prevents an infinite loop.",
    "P4.Q3": "No, it just tells a joke. content has the joke and tool_calls is empty. Providing tools does not force their use.",
}
STUDENT_B = {  # mixed: some correct, some partial, some wrong, a couple blank
    "P1.Q1": "The thinking part is gone and it answers directly. The prefill starts the thinking.",
    "P1.Q2": "The model ignores the instruction and just keeps talking because it does not really understand the sentence.",
    "P1.Q3": "thinking is empty and content has everything.",
    "P2.Q1": "Yes it still knows it.",
    "P2.Q2": "Probably Anna, because that is what we wrote in.",
    "P2.Q3": "",
    "P3.Q1": "No, without a description it will not call the tool anymore.",
    "P3.Q2": "It uses the calculator tool to compute 2 + 2.",
    "P3.Q3": "It throws a KeyError.",
    "P4.Q1": "",
    "P4.Q2": "Two calls.",
    "P4.Q3": "It tells a joke and does not use any tool.",
}
STUDENT_C = {  # weak: mostly wrong or blank
    "P1.Q1": "It removes the thinking block.",
    "P1.Q2": "",
    "P1.Q3": "I am not sure.",
    "P2.Q1": "No, it forgets the name.",
    "P2.Q2": "",
    "P2.Q3": "Yes.",
    "P3.Q1": "",
    "P3.Q2": "It calls the tool.",
    "P3.Q3": "Some error happens.",
    "P4.Q1": "",
    "P4.Q2": "One call.",
    "P4.Q3": "It uses the calculator.",
}


def make_notebook(answers):
    cells = [{
        "cell_type": "markdown", "metadata": {},
        "source": ["# Exercise 1 — Submission\n", "\n", "(Answers tagged per question below.)"],
    }]
    for part in (1, 2, 3, 4):
        lines = [f"# Part {part} answers\n"]
        for q in (1, 2, 3):
            qid = f"P{part}.Q{q}"
            lines.append(f"# {qid}: {answers.get(qid, '')}\n")
        cells.append({
            "cell_type": "code", "execution_count": None, "metadata": {},
            "outputs": [], "source": lines,
        })
    return {"cells": cells, "metadata": {}, "nbformat": 4, "nbformat_minor": 5}


for name, answers in [("student_a", STUDENT_A), ("student_b", STUDENT_B), ("student_c", STUDENT_C)]:
    path = os.path.join(HERE, f"{name}_ex1.ipynb")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(make_notebook(answers), f, indent=1, ensure_ascii=False)
    print(f"wrote {path}")
