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
| `collect_and_grade.py` | Harvest every student's notebooks + grade them (writes `submissions/<student>/*.grade.json`) |
| `build_gradebook.py` | Build one self-contained `gradebook_<lab>.html` (sortable table, click a row for the per-question reasons) |
| `publish_grades.py` | Hand each student their grade back as `~/graded_<lab>.ipynb` (+ an appeal cell) |
| `read_appeals.py` | Collect the appeals students wrote back, for a human to review |
| `grading_console.ipynb` | Buttons for all of the above, with live streaming output (no terminal) |

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

## Weekly loop (one lab per week)

Four commands, run on the Spark from `lab01/`. Nothing writes to a student's home until
step 3, and even then it never overwrites an appeal.

```bash
cd lab01

# 1. COLLECT + GRADE  -> submissions/<student>/*.grade.json + submissions/summary.csv
uv run python _solutions/grading/collect_and_grade.py

# 2. PREVIEW what students will get, touching NO home dir (safe, no sudo):
uv run python _solutions/grading/publish_grades.py --dry-run   # writes ./published_preview/

# 2b. VIEW the whole class at a glance -> gradebook_<lab>.html (sortable, no sudo):
uv run python _solutions/grading/build_gradebook.py            # open the .html in a browser

# 3. PUBLISH each grade into ~<student>/graded_<lab>.ipynb (homes are mode 750 -> sudo):
sudo python3 _solutions/grading/publish_grades.py

# 4. Next week, COLLECT APPEALS students wrote back:
sudo python3 _solutions/grading/read_appeals.py        # -> appeals_<lab>.csv
```

The student opens `graded_<lab>.ipynb` in their file browser, sees the grade table, and if
they disagree writes their reason in the `appeal` cell and saves. That is the whole complaint
channel: no email, no upload. `read_appeals.py` is the only place a human looks.

### Prefer a browser? Use the web GUI

Same buttons as the notebook, as a small local web app (stdlib only, no extra deps):

```bash
cd lab01
uv run python _solutions/grading/grading_web.py     # -> http://127.0.0.1:8765
```

It binds to **127.0.0.1 only** (the buttons can run grading with sudo, so it must not be
exposed). If you are remote, tunnel first: `ssh -L 8765:127.0.0.1:8765 <you>@<spark>`.
Streams each script's output live, has the judge-model dropdown, progress bar, status panel,
and a "View gradebook" button that opens the HTML gradebook. Behaviour is identical to the
console (it calls the same scripts).

### Prefer buttons? Use the console notebook

`grading_console.ipynb` gives you the same four steps as **buttons**, and streams each script's
output **live** into a log so you can watch every student/question as it is graded (look under
the hood, no terminal):

```bash
cd lab01
uv run jupyter notebook _solutions/grading/grading_console.ipynb   # run the one cell -> buttons
```

The buttons just call the scripts below, so behaviour (dry-run safety, appeal protection,
manual overrides) is identical. Steps 1/3/4 touch student homes and so use `sudo -n`
(non-interactive: it never hangs on a prompt). If a button prints *"sudo: a password is
required"*, either launch the notebook from a session where `sudo` is already authorized, or
add a one-time NOPASSWD rule (`sudo visudo -f /etc/sudoers.d/grading`), e.g.:

```
<you> ALL=(root) NOPASSWD: /path/to/lab01/.venv/bin/python3 /path/to/lab01/_solutions/grading/*.py
```

### Dummy students for dev testing

To try the whole pipeline with real-looking data, seed three fake students into the live
home layout (dev only, needs root because it writes under `/home`):

```bash
sudo python3 _solutions/grading/demo/make_demo_homes.py
```

| student | Exercise 1 | Exercise 2 (code) | expected |
|---|---|---|---|
| `jupyter-dummy-perfect` | all answers correct | 4/4 TODOs | ~15/15 |
| `jupyter-dummy-half` | ~half the answers | 2/4 TODOs | ~8/15 |
| `jupyter-dummy-weak` | wrong / missing | 0/4 TODOs | 0/15 |

They then show up like real students under the normal buttons (code exercise is
deterministic: 4/4, 2/4, 0/4; free-text scores depend on the judge model). Remove them with
`sudo rm -rf /home/jupyter-dummy-*`.

### Testing / manual grading (won't get overwritten)

- **Test the whole thing safely:** `publish_grades.py --dry-run` writes to `./published_preview/`
  instead of student homes; then `read_appeals.py --from published_preview` reads from there.
  No student home is ever touched.
- **Override an AI grade by hand:** put a `<key>.manual.json` (same shape as `<key>.grade.json`)
  next to it in `submissions/<student>/`. `publish_grades.py` prefers it and labels the row
  *"reviewed by an instructor."* Re-running `collect_and_grade.py` rewrites only `.grade.json`,
  so your manual overrides survive.
- **No accidental clobbering:** re-running `publish_grades.py` skips already-published files
  (use `--force` to update after a manual fix), and it **never** overwrites a notebook in which
  the student has filed an appeal, even with `--force`.

A different lab? Set `LAB=lab02` (env var) on steps 2–4 so the filename and heading match.

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
