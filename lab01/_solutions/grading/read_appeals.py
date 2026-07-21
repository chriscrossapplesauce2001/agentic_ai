#!/usr/bin/env python3
"""Collect the appeals students wrote back into their graded notebook.

Weekly loop, step 4 (after publish_grades.py handed each student a graded_<lab>.ipynb):
a student who disagrees sets `appeal = "their reason"` in that notebook and saves. This
script reads every student's notebook, pulls out any non-empty `appeal`, and lists them
for the instructor to check by hand. That is the only place a human looks.

Usage
-----
    # Read appeals from the real student homes (mode 750 -> needs sudo):
    sudo python3 read_appeals.py

    # Test against a local preview folder instead (e.g. what publish_grades.py --dry-run wrote):
    python3 read_appeals.py --from published_preview

Prints one line per appeal and writes appeals_<lab>.csv (student, appeal). Says so plainly
when there are none.

Env overrides:
    LAB    label in the filename    (default: lab01)
    HOMES  glob for student homes   (default: /home/jupyter-*)
"""
import ast
import csv
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gstate  # noqa: E402  (sibling module: run-state stamps)

LAB = os.environ.get("LAB", "lab01")
HOMES = os.environ.get("HOMES", "/home/jupyter-*")
OUT_NAME = f"graded_{LAB}.ipynb"


def appeal_in(path):
    """Return the stripped `appeal` string in a notebook, or '' if none."""
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


def find_notebooks(argv):
    """(student, notebook_path) for every published notebook to scan."""
    if "--from" in argv:
        base = argv[argv.index("--from") + 1]
        for path in sorted(glob.glob(os.path.join(base, "*", OUT_NAME))):
            yield os.path.basename(os.path.dirname(path)), path
    else:
        for home in sorted(glob.glob(HOMES)):
            path = os.path.join(home, OUT_NAME)
            if os.path.isfile(path):
                yield os.path.basename(home).removeprefix("jupyter-"), path


def main(argv):
    appeals = [(st, appeal_in(p)) for st, p in find_notebooks(argv)]
    appeals = [(st, text) for st, text in appeals if text]
    gstate.stamp("appeals", lab=LAB, count=len(appeals))

    if not appeals:
        print("No appeals. Nothing to review.")
        return 0

    print(f"{len(appeals)} appeal(s) to review:\n")
    for st, text in appeals:
        print(f"  {st}: {text}")

    out = os.path.abspath(f"appeals_{LAB}.csv")
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["student", "appeal"])
        w.writerows(appeals)
    print(f"\n-> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
