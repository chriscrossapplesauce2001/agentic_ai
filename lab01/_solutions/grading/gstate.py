#!/usr/bin/env python3
"""Tiny shared run-state for the grading pipeline: who did what, when, with which model.

Every step (collect+grade, publish, appeals, gradebook) stamps a line here when it finishes,
so the console can show a status panel and you never have to guess whether you already graded
or published, or which judge model you used. Stored as <submissions>/status.json so both the
console and plain CLI runs share it.
"""
import datetime
import json
import os


def _dir():
    return (os.environ.get("SUBMISSIONS") or os.environ.get("OUT")
            or os.path.abspath("submissions"))


def _path():
    return os.path.join(_dir(), "status.json")


def stamp(action, **info):
    """Record that `action` just happened, with the current time + any extra info."""
    p = _path()
    os.makedirs(os.path.dirname(p), exist_ok=True)
    try:
        state = json.load(open(p, encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        state = {}
    state[action] = {"time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), **info}
    with open(p, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def load():
    try:
        return json.load(open(_path(), encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
