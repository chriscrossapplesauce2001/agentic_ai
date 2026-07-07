#!/usr/bin/env python3
"""Generate nbgitpuller magic links for the Lab 1 exercises.

One link per exercise. Each link clones the whole repo into the student's home
directory (~/agentic_ai/) and opens that exercise's notebook. The repo and the
exercise list are read from this checkout, so the links can never point at a
notebook that does not exist.

Usage
-----
    # print a link for every exercise, given the public tunnel host:
    python make_links.py spark.tailXXXX.ts.net
    python make_links.py random123.trycloudflare.com
    python make_links.py https://lab.example.com/      # scheme + slash are tolerated

    # self-test, no host needed (exit 0 = all links valid):
    python make_links.py --check

The host is the only thing that changes between runs (quick-tunnel hostnames
rotate on restart); everything else is derived from the repo.
"""

import sys
from pathlib import Path
from urllib.parse import quote, urlparse, parse_qs

# --- config: the only repo-wide constants --------------------------------------
REPO = "https://github.com/chriscrossapplesauce2001/agentic_ai"
BRANCH = "master"
# nbgitpuller clones into a dir named after the repo's last path segment:
CLONE_DIR = REPO.rstrip("/").split("/")[-1]            # -> "agentic_ai"

# repo root, relative to this file (instructor/infra/make_links.py):
REPO_ROOT = Path(__file__).resolve().parents[2]


def find_exercises():
    """Return sorted (name, repo-relative notebook path) for every exercise."""
    found = []
    for nb in sorted(REPO_ROOT.glob("lab01/exercise*/exercise*.ipynb")):
        rel = nb.relative_to(REPO_ROOT)
        found.append((nb.parent.name, rel.as_posix()))
    return found


def build_link(host, rel_path):
    """Build one URL-encoded nbgitpuller link for a repo-relative notebook path."""
    host = host.strip().rstrip("/")
    # accept "host", "https://host", or "https://host/" all the same:
    if "://" in host:
        host = urlparse(host).netloc
    urlpath = f"lab/tree/{CLONE_DIR}/{rel_path}"
    query = (
        f"repo={quote(REPO, safe='')}"
        f"&branch={quote(BRANCH, safe='')}"
        f"&urlpath={quote(urlpath, safe='')}"
    )
    return f"https://{host}/hub/user-redirect/git-pull?{query}"


def check():
    """Self-test: round-trip every link and confirm its notebook exists on disk."""
    exercises = find_exercises()
    if not exercises:
        print("FAIL: no exercise notebooks found under lab01/", file=sys.stderr)
        return 1

    ok = True
    for name, rel_path in exercises:
        link = build_link("example.test", rel_path)
        params = parse_qs(urlparse(link).query)

        # the encoded params must decode back to exactly what we put in:
        problems = []
        if params.get("repo") != [REPO]:
            problems.append("repo did not round-trip")
        if params.get("branch") != [BRANCH]:
            problems.append("branch did not round-trip")
        expected_urlpath = f"lab/tree/{CLONE_DIR}/{rel_path}"
        if params.get("urlpath") != [expected_urlpath]:
            problems.append("urlpath did not round-trip")
        # the link must point at a notebook that actually exists:
        if not (REPO_ROOT / rel_path).is_file():
            problems.append(f"notebook missing on disk: {rel_path}")

        if problems:
            ok = False
            print(f"FAIL {name}: {'; '.join(problems)}", file=sys.stderr)
        else:
            print(f"ok   {name}: {rel_path}")

    print(f"\n{'PASS' if ok else 'FAIL'}: {len(exercises)} exercise link(s) checked")
    return 0 if ok else 1


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    if argv[1] == "--check":
        return check()

    host = argv[1]
    for name, rel_path in find_exercises():
        print(f"# {name}")
        print(build_link(host, rel_path))
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
