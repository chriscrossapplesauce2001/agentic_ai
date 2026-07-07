# Lab 01 Auto-Grading

**Internal. Do not distribute to students, and do not push to a public repo** (see warning below).

Grades a submitted Lab 01 notebook against the reference solution:
- **Exercise 1** (free-text "Your Turn" answers): graded by a **judge LLM**, one question at a time, against the rubric in `rubric.json`. (Exercise 0 is ungraded LLM-basics onboarding.)
- **Exercise 2** (code TODOs): checked **deterministically** (anchored regex on the `run_agent` code), no LLM.

## Files

| File | Purpose |
|---|---|
| `SOLUTION_KEY.md` | Human-readable rubric (`✓ / ± / ✗`) |
| `rubric.json` | Machine-readable rubric that `grade.py` reads |
| `grade.py` | The grader (stdlib + `ollama` only) |

## Submission convention

Students tag each answer with its question id, anywhere in the notebook (code comment or markdown cell):

```python
# P1.Q1: Without <think> the reasoning block disappears; the answer comes straight out.
# P1.Q2: It keeps running. The stop token <|im_end|> stops it, not the text instruction.
```

The grader takes the text after each tag up to the next tag. A missing tag means the question is scored `missing` (no LLM call).

> **Note:** `lab01/exercise1/exercise1.ipynb` is patched so each "Your Turn" cell points at the tagging convention and has an **Answers** cell below it with pre-filled `P{part}.Q{n}:` stubs. Students only write after the colon. (Exercise 2 is code and needs no tags.)

## Usage

```bash
# Run from the lab01/ directory so the ollama package from the uv env is on the path
# (grade.py needs `ollama`):
cd lab01

# Default judge is nemotron-3-super:latest (pulled on the Spark, max quality).
# Optionally override with another pulled model:
# export JUDGE_MODEL=llama3.3:70b

uv run python _solutions/grading/grade.py student_submission_ex1.ipynb student_submission_ex2.ipynb
uv run python _solutions/grading/grade.py --dry-run submission.ipynb   # extract answers only, no LLM
```

Each notebook gets a `*.grade.json` with the labels (`correct / partial / incorrect / missing`). Routing (code vs. free-text) is automatic based on content.

## Collecting all submissions

> **Moved.** Harvesting is now separate from grading: use
> `sudo python3 instructor/infra/collect_submissions.py` (see the section in
> `instructor/infra/jupyterhub.md`). It snapshots every student's notebooks plus a
> `manifest.csv`. Grading the harvested notebooks with `grade.py` /
> `collect_and_grade.py` is **postponed** and not part of the current workflow.

Students only have to **save** their notebook (Jupyter autosaves) and not rename/move it. The
answer-tagging stubs keep their answers in a predictable place.

## Deliberate design choices

- **Judge = a larger model than the students run.** Grading is offline/batch over ≤15 submissions, so latency does not matter. `temperature=0`, `format=json` for 100% parseable output.
- **One question per LLM call**, with the rubric for that question only: small context, one decision. More reliable than the whole notebook at once.
- **3-level label instead of a 0–100 score.** Small/mid-size models do not calibrate a fine scale, but they can match answers against explicit core points.
- **Code is not graded by the LLM.** The TODOs have deterministic solutions.

## Limits

- The code check is a **smoke test** (regex), not execution. More robust: run the notebook / run `pytest` against the three test queries (needs a running Ollama + network for `web_search`). Add that path for a real grade.
- For borderline cases (`partial`), a human second pass is worthwhile: a few minutes for 15 submissions.

## ⚠️ Warning: public repo

The lab notebooks are delivered to students via nbgitpuller from a **public GitHub repo** (`github.com/chriscrossapplesauce2001/agentic_ai`), and nbgitpuller clones the **whole repo** into each student's home dir. Everything in this repo is therefore reachable by students, including `lab01/_solutions/`. This `grading/` folder (reference solution + rubric) must **not** be exposed to students once the lab goes live: exclude it via `.gitignore`, serve students a separate branch without it, or keep it in a separate private repo.
