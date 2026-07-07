#!/usr/bin/env python3
"""Run the submission harvest on the Spark and download the snapshot to this machine.

Works on Linux, macOS, and Windows 10+ (OpenSSH client is preinstalled on all three;
`ssh` and `scp` must be on PATH). Requires Tailscale up and SSH access to the Spark.

    python3 instructor/infra/harvest_remote.py            # harvest + download
    python3 instructor/infra/harvest_remote.py --no-run   # only download the latest snapshot

Env overrides:
    SPARK   ssh target                  (default: agentsmith@gx10-489a)
    DEST    local download directory    (default: ./lab01_submissions)
"""
import os
import re
import subprocess
import sys

SPARK = os.environ.get("SPARK", "agentsmith@gx10-489a")
DEST = os.environ.get("DEST", os.path.join(os.getcwd(), "lab01_submissions"))
COLLECT = "sudo python3 cwilsch/agentic_ai/instructor/infra/collect_submissions.py"
LATEST = "ls -1d lab01_submissions/*/ | sort | tail -1"


def run(cmd, **kw):
    print("+", " ".join(cmd))
    return subprocess.run(cmd, check=True, **kw)


def main():
    if "--no-run" in sys.argv[1:]:
        out = run(["ssh", SPARK, LATEST], capture_output=True, text=True).stdout
        snapshot = out.strip().rstrip("/")
        if not snapshot:
            sys.exit("No snapshots found on the Spark.")
    else:
        proc = run(["ssh", SPARK, COLLECT], capture_output=True, text=True)
        print(proc.stdout)
        m = re.search(r"Snapshot -> (\S+)", proc.stdout)
        if not m:
            sys.exit("Harvest ran but no snapshot path found in its output.")
        snapshot = m.group(1)

    local = os.path.join(DEST, os.path.basename(snapshot))
    os.makedirs(DEST, exist_ok=True)
    run(["scp", "-r", "-q", f"{SPARK}:{snapshot}", local])
    print(f"\nDownloaded -> {local}")
    manifest = os.path.join(local, "manifest.csv")
    if os.path.isfile(manifest):
        print(open(manifest, encoding="utf-8").read())


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        if exc.stderr:
            print(exc.stderr, file=sys.stderr)
        sys.exit(f"Command failed ({exc.returncode}). Is Tailscale up and your SSH key on the Spark?")
