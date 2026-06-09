#!/usr/bin/env python3
"""Auto-grade Lab 01 submissions against the Musterlösung rubric.

Free-text answers (Exercise 0) are graded by a local judge LLM (a bigger model
than the students run). Code TODOs (Exercise 1) are checked deterministically,
no LLM. Only stdlib + the `ollama` package are required.

Submission convention
---------------------
Each free-text answer is tagged with its rubric id anywhere in the notebook
(in a code comment or a markdown cell), e.g.:

    # P1.Q1: Removing <think> drops the reasoning block; the answer comes straight out.
    # P1.Q2: It still runs away. The stop token <|im_end|> is what stops it, ...

The grader extracts the text after each tag up to the next tag.

Usage
-----
    JUDGE_MODEL=nemotron-3-super:latest python grade.py submission_ex0.ipynb [submission_ex1.ipynb ...]
    python grade.py --dry-run submission_ex0.ipynb     # extract answers, no LLM
"""

import json
import os
import re
import sys

JUDGE_MODEL = os.environ.get("JUDGE_MODEL", "nemotron-3-super:latest")  # override with any model pulled on the Spark
RUBRIC_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rubric.json")
TAG_RE = re.compile(r"\bP(\d+)\.Q(\d+)\s*:", re.IGNORECASE)

JUDGE_SYSTEM = (
    "You grade a student's short answer in a course on how LLM agents work. "
    "You are given the question, the rubric (the points a correct answer must make, "
    "plus what is acceptable and what is a typical mistake), and the student's answer. "
    "Decide one label: 'correct', 'partial', or 'incorrect'.\n"
    "Rules:\n"
    "- 'correct' = the student hits the core point(s). Wording may differ; do not require exact phrasing.\n"
    "- 'partial' = right direction but the key reason is missing, vague, or garbled.\n"
    "- 'incorrect' = the core point is missing or wrong, or the answer is empty/off-topic.\n"
    "- When the rubric marks the behavior as variable, do NOT penalize which behavior occurred; "
    "grade only whether the student drew the right conclusion.\n"
    "- Be strict: if you are unsure the core point is present, choose 'partial' or 'incorrect', not 'correct'.\n"
    "Reply ONLY as JSON: {\"label\": \"...\", \"reason\": \"<one short sentence>\"}."
)


def notebook_cells_text(path):
    """Return a list of (cell_type, source_text) for an .ipynb (read as plain JSON)."""
    with open(path, encoding="utf-8") as f:
        nb = json.load(f)
    out = []
    for cell in nb.get("cells", []):
        src = cell.get("source", "")
        if isinstance(src, list):
            src = "".join(src)
        out.append((cell.get("cell_type", ""), src))
    return out


def extract_answers(cells):
    """Find every P<n>.Q<n>: tag, capturing text up to the next tag IN THE SAME CELL.

    Per-cell capture keeps the last tag in an answer cell from sweeping up following
    cells. A non-empty answer is never overwritten by a later empty stub.
    """
    answers = {}
    for _, src in cells:
        matches = list(TAG_RE.finditer(src))
        for i, m in enumerate(matches):
            qid = f"P{m.group(1)}.Q{m.group(2)}".upper()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(src)
            text = src[m.end():end]
            # strip leading comment markers from continuation lines
            text = "\n".join(re.sub(r"^\s*#\s?", "", ln) for ln in text.splitlines()).strip()
            if text or qid not in answers:
                answers[qid] = text
    return answers


def judge(qid, spec, answer):
    if not answer:
        return {"label": "missing", "reason": "no answer tagged for this question"}
    rubric_lines = ["Core points (a correct answer makes these):"]
    rubric_lines += [f"  - {c}" for c in spec.get("core", [])]
    if spec.get("variable"):
        rubric_lines.append("NOTE: the observed behavior is variable/model-dependent; grade the conclusion, not which behavior occurred.")
    if spec.get("accept"):
        rubric_lines += ["Also acceptable:"] + [f"  - {a}" for a in spec["accept"]]
    if spec.get("wrong"):
        rubric_lines += ["Typical mistake (mark down for this):"] + [f"  - {w}" for w in spec["wrong"]]
    user = (
        f"Question: {spec['question']}\n\n"
        + "\n".join(rubric_lines)
        + f"\n\nStudent answer:\n\"\"\"\n{answer}\n\"\"\"\n"
    )
    import ollama
    resp = ollama.chat(
        model=JUDGE_MODEL,
        messages=[{"role": "system", "content": JUDGE_SYSTEM}, {"role": "user", "content": user}],
        format="json",
        options={"temperature": 0, "num_ctx": 8192},
    )
    try:
        out = json.loads(resp["message"]["content"])
        return {"label": str(out.get("label", "error")).lower(), "reason": out.get("reason", "")}
    except (json.JSONDecodeError, KeyError) as exc:
        return {"label": "error", "reason": f"judge returned unparseable output: {exc}"}


def grade_freetext(cells, rubric, dry_run):
    answers = extract_answers(cells)
    results = {}
    for qid, spec in rubric["exercise0"].items():
        ans = answers.get(qid, "")
        if dry_run:
            results[qid] = {"label": "—", "reason": f"extracted {len(ans)} chars" if ans else "MISSING"}
        else:
            results[qid] = judge(qid, spec, ans)
    return results


def _strip_comments(code):
    """Drop everything from the first '#' on each line (no '#' inside strings here)."""
    return "\n".join(ln.split("#", 1)[0] for ln in code.splitlines())


def check_code(cells, rubric):
    """Deterministic check of the run_agent TODOs via anchored regexes on comment-stripped code.

    This is a smoke test, not a substitute for execution. The robust path is to run the
    notebook / pytest against the three test queries; see README.
    """
    blob = "\n".join(src for t, src in cells if t == "code")
    m = re.search(r"def run_agent\(.*?(?=\ndef |\Z)", blob, re.DOTALL)
    run_agent = _strip_comments(m.group(0)) if m else ""
    results = {}
    for tid, spec in rubric["exercise1_code"].items():
        if not run_agent:
            results[tid] = {"label": "missing", "reason": "run_agent() not found"}
            continue
        missing = [p for p in spec["patterns"] if not re.search(p, run_agent)]
        if missing:
            results[tid] = {"label": "incorrect", "reason": f"TODO unfilled / pattern not found: {missing}"}
        else:
            results[tid] = {"label": "correct", "reason": spec["desc"]}
    return results


def is_exercise1(cells):
    return any("def run_agent" in src for _, src in cells)


def print_report(path, results):
    print(f"\n=== {os.path.basename(path)} ===")
    counts = {}
    for qid, r in results.items():
        counts[r["label"]] = counts.get(r["label"], 0) + 1
        print(f"  {qid:8} {r['label']:10} {r['reason']}")
    summary = "  ".join(f"{k}={v}" for k, v in sorted(counts.items()))
    print(f"  ---- {summary}")


def main(argv):
    dry_run = "--dry-run" in argv
    paths = [a for a in argv if not a.startswith("--")]
    if not paths:
        print(__doc__)
        return 1
    with open(RUBRIC_PATH, encoding="utf-8") as f:
        rubric = json.load(f)
    if not dry_run:
        print(f"Judge model: {JUDGE_MODEL}  (override with JUDGE_MODEL=...)")
    for path in paths:
        cells = notebook_cells_text(path)
        if is_exercise1(cells):
            results = check_code(cells, rubric)
        else:
            results = grade_freetext(cells, rubric, dry_run)
        print_report(path, results)
        out_path = os.path.splitext(path)[0] + ".grade.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
