#!/usr/bin/env python3
"""Return each student's grade to them as a notebook in their JupyterHub home.

Weekly loop, step 3 (after collect_and_grade.py has produced the .grade.json files):

    collect_and_grade.py  ->  submissions/<student>/exercise1.grade.json  (AI grades)
    publish_grades.py     ->  ~<student>/graded_<lab>.ipynb               (this script)
    read_appeals.py       ->  reads the appeal the student wrote back      (next step)

The published notebook has two cells:
  1. a markdown table with the grade (total + per-question score, verdict, and why),
  2. one `appeal` cell. If the student disagrees they write their reason between the
     quotes and Save. That is the whole complaint channel: no email, no upload.

It lands in the student's HOME ROOT (~/graded_<lab>.ipynb), NOT inside their repo clone,
so nbgitpuller never touches it and it is the first file they see.

Usage
-----
    # Preview into ./published_preview/ WITHOUT touching any student home (safe, no sudo):
    python3 publish_grades.py --dry-run

    # Really write into each student's home (student homes are mode 750 -> needs sudo):
    sudo python3 publish_grades.py

    # Re-publish after you changed a grade (see manual override below):
    sudo python3 publish_grades.py --force

Safety (see also read_appeals.py):
  * A student's appeal is NEVER overwritten. If ~/graded_<lab>.ipynb already contains a
    non-empty `appeal`, this script skips it even with --force.
  * Without --force, an already-published file is left alone (skipped), so re-running is safe.
  * --dry-run writes to ./published_preview/ only, so you can eyeball the exact notebook
    students will get before publishing for real.

Manual grading / overriding the AI
----------------------------------
To hand-grade or correct one grade, put a `<key>.manual.json` next to the AI's
`<key>.grade.json` (same shape) in submissions/<student>/. This script prefers the
manual file. Re-running collect_and_grade.py rewrites only `.grade.json`, so your
`.manual.json` overrides are never clobbered.

Env overrides:
    LAB          label used in the filename + heading   (default: lab01)
    SUBMISSIONS  where the .grade.json files live        (default: ./submissions)
    HOMES        glob for student home dirs              (default: /home/jupyter-*)
"""
import ast
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gstate  # noqa: E402  (sibling module: run-state stamps)

LAB = os.environ.get("LAB", "lab01")
SUBMISSIONS = os.environ.get("SUBMISSIONS", os.path.abspath("submissions"))
HOMES = os.environ.get("HOMES", "/home/jupyter-*")
PREVIEW = os.path.abspath("published_preview")
OUT_NAME = f"graded_{LAB}.ipynb"


def load_grades(student_dir):
    """key -> (payload, source). Prefer <key>.manual.json over <key>.grade.json.
    Only keeps graded payloads (those with a 'questions' block)."""
    grades = {}
    for kind in ("grade", "manual"):  # manual is read second, so it wins
        for path in sorted(glob.glob(os.path.join(student_dir, f"*.{kind}.json"))):
            key = os.path.basename(path)[: -len(f".{kind}.json")]
            try:
                payload = json.load(open(path, encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            if isinstance(payload, dict) and "questions" in payload:
                grades[key] = (payload, "instructor" if kind == "manual" else "AI")
    return grades


def md_cell(text):
    return {"cell_type": "markdown", "id": "grade-table", "metadata": {}, "source": text}


def appeal_cell():
    src = (
        'appeal = ""   # Unhappy with a grade? Put your reason between the quotes, then Save (Ctrl+S).\n'
        '              # Example: appeal = "P2.Q1: my answer was correct because ..."\n'
        '              # An instructor then reviews it by hand. Leave it as "" if the grade is fine.'
    )
    return {"cell_type": "code", "id": "appeal", "metadata": {},
            "execution_count": None, "outputs": [], "source": src}


def clean(text):
    """Make a rubric reason safe for one Markdown table cell."""
    return str(text).replace("|", "\\|").replace("\n", " ").strip()


def build_notebook(student, grades):
    lines = [f"# Your grade — {LAB}\n", "\n"]
    for key in sorted(grades):
        payload, source = grades[key]
        total, mx = payload.get("total", 0), payload.get("max", 0)
        note = "  _(reviewed by an instructor)_" if source == "instructor" else ""
        lines.append(f"## {key}: **{total} / {mx}**{note}\n\n")
        lines.append("| Question | Score | Verdict | Why |\n")
        lines.append("|---|---|---|---|\n")
        for qid, r in payload["questions"].items():
            lines.append(f"| {qid} | {r.get('score', 0)} | {r.get('label', '')} | {clean(r.get('reason', ''))} |\n")
        lines.append("\n")
    lines.append("---\n\nDisagree with something? Use the `appeal` cell below.\n")
    nb = {"cells": [md_cell("".join(lines)), appeal_cell()],
          "metadata": {}, "nbformat": 4, "nbformat_minor": 5}
    return nb


def existing_appeal(path):
    """Return the appeal string already in a published notebook, or '' if none/unreadable."""
    try:
        nb = json.load(open(path, encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return ""
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        src = cell["source"]
        src = "".join(src) if isinstance(src, list) else src
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if (isinstance(node, ast.Assign) and len(node.targets) == 1
                    and isinstance(node.targets[0], ast.Name)
                    and node.targets[0].id == "appeal"):
                try:
                    val = ast.literal_eval(node.value)
                except (ValueError, SyntaxError):
                    val = ""
                if isinstance(val, str) and val.strip():
                    return val.strip()
    return ""


def write_notebook(path, nb, owner=None):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
    if owner:  # hand the file to the student so JupyterHub (running as them) can edit it
        os.chown(path, *owner)
        os.chmod(path, 0o644)


def main(argv):
    dry = "--dry-run" in argv
    force = "--force" in argv

    students = sorted(os.path.basename(p) for p in glob.glob(os.path.join(SUBMISSIONS, "*"))
                      if os.path.isdir(p))
    if not students:
        sys.exit(f"No student folders in {SUBMISSIONS!r}. Run collect_and_grade.py first.")

    homes = {os.path.basename(h).removeprefix("jupyter-"): h
             for h in glob.glob(HOMES) if os.path.isdir(h)}

    published = skipped = 0
    for student in students:
        grades = load_grades(os.path.join(SUBMISSIONS, student))
        if not grades:
            print(f"  {student:18} - not graded yet, skipped")
            continue
        nb = build_notebook(student, grades)

        if dry:
            dst = os.path.join(PREVIEW, student, OUT_NAME)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            write_notebook(dst, nb)
            print(f"  {student:18} - preview -> {dst}")
            published += 1
            continue

        home = homes.get(student)
        if not home:
            print(f"  {student:18} - no home dir (left the course?), skipped")
            skipped += 1
            continue
        dst = os.path.join(home, OUT_NAME)
        if os.path.isfile(dst):
            if existing_appeal(dst):
                print(f"  {student:18} - APPEAL present, left untouched")
                skipped += 1
                continue
            if not force:
                print(f"  {student:18} - already published (use --force to update)")
                skipped += 1
                continue
        owner = (os.stat(home).st_uid, os.stat(home).st_gid)
        write_notebook(dst, nb, owner)
        print(f"  {student:18} - published -> {dst}")
        published += 1

    where = PREVIEW if dry else "student homes"
    print(f"\n{published} published to {where}, {skipped} skipped.")
    if dry:
        print("Dry run: no student home was touched. Re-run with sudo (no --dry-run) to publish.")
    else:
        gstate.stamp("published", lab=LAB, published=published, skipped=skipped)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
