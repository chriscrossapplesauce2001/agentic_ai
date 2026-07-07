#!/usr/bin/env python3
"""Harvest every student's lab01 exercise notebooks from their JupyterHub home dir.

Students never submit: nbgitpuller clones the repo into /home/jupyter-<name>/agentic_ai/
and they work in place. This script snapshots those notebooks. Run it with sudo (student
home dirs are mode 750):

    sudo python3 instructor/infra/collect_submissions.py [OUT_DIR]

Default OUT_DIR: ~<you>/lab01_submissions/<timestamp>/ (a new snapshot per run).
Copies exercise0-3 into OUT_DIR/<student>/ and writes OUT_DIR/manifest.csv.

Per-notebook status in the manifest (anything but "ok" needs instructor attention):
    ok           collected, valid JSON, differs from every committed template version
    unchanged    collected, but byte-identical to a committed template: the student
                 never saved anything in this file (worked elsewhere, or not at all)
    invalid      collected, but not parseable JSON (corrupted, e.g. bad merge)
    MISSING      file not found in the student's clone
    symlink      path is a symlink; skipped (never follow student-controlled links as root)
The "extra_notebooks" column lists stray *.ipynb files in the student's lab01 tree
(e.g. "exercise1-Copy1.ipynb" or renamed files) so misplaced work is spotted, not lost.

Grading is separate and postponed; see lab01/_solutions/grading/.
Env override: HOMES (default /home/jupyter-*).
"""
import csv
import datetime
import glob
import json
import os
import pwd
import shutil
import subprocess
import sys

HOMES = os.environ.get("HOMES", "/home/jupyter-*")
EXERCISES = ["exercise0", "exercise1", "exercise2", "exercise3"]
REL = "agentic_ai/lab01/{ex}/{ex}.ipynb"
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def default_out():
    caller = os.environ.get("SUDO_USER") or os.environ.get("USER") or "root"
    home = pwd.getpwnam(caller).pw_dir
    stamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    return os.path.join(home, "lab01_submissions", stamp)


def template_blobs():
    """Blob ids of every committed version of every lab01 notebook (all branches,
    all historical paths, so renamed/renumbered exercises are covered too)."""
    out = subprocess.run(
        ["git", "-C", REPO, "rev-list", "--all", "--objects", "--", "lab01"],
        capture_output=True, text=True, check=True,
    ).stdout
    return {line.split()[0] for line in out.splitlines()
            if line.rstrip().endswith(".ipynb")}


def blob_id(path):
    return subprocess.run(["git", "hash-object", path],
                          capture_output=True, text=True, check=True).stdout.strip()


def collect_one(home, student, out, templates):
    row = {"student": student}
    for ex in EXERCISES:
        src = os.path.join(home, REL.format(ex=ex))
        if os.path.islink(src):
            row[ex] = "symlink"
            continue
        if not os.path.isfile(src):
            row[ex] = "MISSING"
            continue
        dst_dir = os.path.join(out, student)
        os.makedirs(dst_dir, exist_ok=True)
        shutil.copy2(src, os.path.join(dst_dir, f"{ex}.ipynb"))
        if blob_id(src) in templates:
            row[ex] = "unchanged"
        else:
            try:
                json.load(open(src, encoding="utf-8"))
                row[ex] = "ok"
            except (json.JSONDecodeError, UnicodeDecodeError):
                row[ex] = "invalid"

    expected = {REL.format(ex=ex) for ex in EXERCISES}
    lab = os.path.join(home, "agentic_ai", "lab01")
    extra = []
    for dirpath, dirnames, filenames in os.walk(lab):
        dirnames[:] = [d for d in dirnames if d != ".ipynb_checkpoints"]
        for name in filenames:
            p = os.path.join(dirpath, name)
            if (name.endswith(".ipynb") and not os.path.islink(p)
                    and os.path.relpath(p, home) not in expected
                    and blob_id(p) not in templates):  # unmodified repo-shipped files are noise
                extra.append(os.path.relpath(p, lab))
    row["extra_notebooks"] = " ".join(sorted(extra))
    return row


def main(argv):
    out = os.path.abspath(argv[0]) if argv else default_out()
    homes = sorted(p for p in glob.glob(HOMES) if os.path.isdir(p))
    if not homes:
        sys.exit(f"No student homes matched {HOMES!r}")

    unreadable = [h for h in homes if not os.access(h, os.R_OK | os.X_OK)]
    if unreadable:
        sys.exit(f"Cannot read {unreadable[0]} (student homes are mode 750). Run with sudo.")

    templates = template_blobs()
    rows = []
    for home in homes:
        student = os.path.basename(home).removeprefix("jupyter-")
        row = collect_one(home, student, out, templates)
        rows.append(row)
        line = "  ".join(f"{ex}:{row[ex]}" for ex in EXERCISES)
        if row["extra_notebooks"]:
            line += f"  extra:[{row['extra_notebooks']}]"
        print(f"  {student:18} {line}")

    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "manifest.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["student"] + EXERCISES + ["extra_notebooks"])
        w.writeheader()
        w.writerows(rows)

    # hand the snapshot back to the sudo caller so it isn't root-owned
    if os.environ.get("SUDO_UID"):
        uid, gid = int(os.environ["SUDO_UID"]), int(os.environ["SUDO_GID"])
        for dirpath, dirnames, filenames in os.walk(out):
            for name in [""] + dirnames + filenames:
                os.chown(os.path.join(dirpath, name), uid, gid)
        os.chown(os.path.dirname(out), uid, gid)

    n_attn = sum(1 for r in rows for ex in EXERCISES if r[ex] != "ok")
    print(f"\nSnapshot -> {out}  ({len(rows)} students, "
          f"{n_attn} notebook slot(s) need attention, see manifest.csv)")


if __name__ == "__main__":
    main(sys.argv[1:])
