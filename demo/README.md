# Grading demo

A self-contained demonstration of the Exercise 1 auto-grader on three fake submissions of
deliberately different quality. Internal — shows that the grading pipeline works end to end.

| File | What it is |
|---|---|
| `_make_submissions.py` | Generates the three submissions (answers + quality are hard-coded) |
| `student_a_ex1.ipynb` | Strong submission (answers hit the rubric core points) |
| `student_b_ex1.ipynb` | Mixed (some correct, some partial/wrong, a couple left blank) |
| `student_c_ex1.ipynb` | Weak (mostly wrong or blank) |
| `student_*_ex1.grade.json` | The grader's output for each (per-question score + label, and a total) |

## Reproduce

```bash
python3 demo/_make_submissions.py          # (re)generate the three notebooks
cd lab01
uv run python _solutions/grading/grade.py \
    ../demo/student_a_ex1.ipynb ../demo/student_b_ex1.ipynb ../demo/student_c_ex1.ipynb
```

## Last run (judge: `nemotron-3-super:latest`, 11-point scale)

| Submission | Score |
|---|---|
| student_a (strong) | 10.0 / 11 |
| student_b (mixed)  | 5.5 / 11 |
| student_c (weak)   | 1.5 / 11 |

The three separate cleanly by quality. The judge is reliable on clearly-correct, clearly-wrong,
and blank answers; borderline `partial` calls deserve a human glance before final grades.
