#!/usr/bin/env python3
"""Collect each student's lab01 notebooks from their JupyterHub home dir and grade them.

Simple + robust: students do nothing but leave their saved notebook in place. Because every
student's home dir lives on this one Spark box, the instructor just harvests the files at the
deadline. No submit step, no upload, no exchange server to fail.

Run on the Spark, from lab01/ so the uv env's `ollama` is importable:

    cd lab01
    uv run python _solutions/grading/collect_and_grade.py            # collect + grade + CSV
    uv run python _solutions/grading/collect_and_grade.py --dry-run  # collect + extract, no LLM
                                                                     # (code exercise still scored)

Env overrides (also used by the test):
    HOMES   glob for student home dirs            (default: /home/jupyter-*)
    OUT     where to copy the collected notebooks (default: ./submissions)

Each notebook is graded in its own subprocess, so one corrupt/odd submission cannot sink the
batch. A per-student summary is printed and written to OUT/summary.csv.
"""
import csv
import glob
import json
import os
import shutil
import subprocess
import sys

HOMES = os.environ.get("HOMES", "/home/jupyter-*")
OUT = os.environ.get("OUT", os.path.abspath("submissions"))
HERE = os.path.dirname(os.path.abspath(__file__))
GRADER = os.path.join(HERE, "grade.py")
sys.path.insert(0, HERE)
import gstate  # noqa: E402  (sibling module: run-state stamps)

# grade.py's default judge, mirrored here only so the status panel can show what was used.
JUDGE_MODEL = os.environ.get("JUDGE_MODEL", "nemotron-3-super:latest")

# Graded notebooks, relative to each student's repo clone. exercise0 (LLM basics) is ungraded.
TARGETS = {
    "exercise1": "agentic_ai/lab01/exercise1/exercise1.ipynb",
    "exercise2": "agentic_ai/lab01/exercise2/exercise2.ipynb",
}


def student_name(home):
    base = os.path.basename(home.rstrip("/"))
    return base[len("jupyter-"):] if base.startswith("jupyter-") else base


def grade_one(path, dry_run):
    """Grade a single notebook in its own process; return (total, max) or None."""
    cmd = [sys.executable, GRADER] + (["--dry-run"] if dry_run else []) + [path]
    try:
        subprocess.run(cmd, check=False)
    except Exception as exc:  # never let one submission kill the run
        print(f"  ! grading failed for {path}: {exc}", file=sys.stderr)
        return None
    gj = os.path.splitext(path)[0] + ".grade.json"
    if not os.path.isfile(gj):
        return None
    try:
        d = json.load(open(gj, encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    if isinstance(d, dict) and "total" in d:
        return (d["total"], d["max"])
    return None  # dry-run report has no total


def main(argv):
    dry = "--dry-run" in argv
    homes = sorted(p for p in glob.glob(HOMES) if os.path.isdir(p))
    if not homes:
        print(f"No student homes matched {HOMES!r}", file=sys.stderr)
        return 1

    print(f"Found {len(homes)} student home(s). Collecting into {OUT}\n")
    roster = []  # (student, {key: dest_path or None})
    for home in homes:
        st = student_name(home)
        found = {}
        for key, rel in TARGETS.items():
            src = os.path.join(home, rel)
            if os.path.isfile(src):
                dst_dir = os.path.join(OUT, st)
                os.makedirs(dst_dir, exist_ok=True)
                dst = os.path.join(dst_dir, f"{key}.ipynb")
                shutil.copy2(src, dst)
                found[key] = dst
            else:
                found[key] = None
        roster.append((st, found))
        print(f"  {st:18} " + "  ".join(f"{k}:{'ok' if v else 'MISSING'}" for k, v in found.items()))

    print("\nGrading...\n")
    todo = [(st, key, dst) for st, found in roster for key, dst in found.items() if dst]
    total = len(todo)
    scores = {}  # (student, key) -> (total, max) or None
    # '@PROGRESS done/total' lines let the console draw a progress bar; harmless in a plain run.
    print(f"@PROGRESS 0/{total}", flush=True)
    for i, (st, key, dst) in enumerate(todo, 1):
        scores[(st, key)] = grade_one(dst, dry)
        print(f"@PROGRESS {i}/{total}", flush=True)

    os.makedirs(OUT, exist_ok=True)
    csv_path = os.path.join(OUT, "summary.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["student", "exercise1", "exercise1_max", "exercise2", "exercise2_max"])
        for st, found in roster:
            row = [st]
            for key in ("exercise1", "exercise2"):
                if found[key] is None:
                    row += ["MISSING", ""]
                elif scores.get((st, key)):
                    row += [scores[(st, key)][0], scores[(st, key)][1]]
                else:
                    row += ["collected (not graded)", ""]
            w.writerow(row)

    print(f"\nSummary -> {csv_path}\n")
    print(open(csv_path, encoding="utf-8").read())

    n_graded = sum(1 for v in scores.values() if v)
    gstate.stamp("graded", model=("dry-run" if dry else JUDGE_MODEL),
                 students=len(roster), graded=n_graded)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
