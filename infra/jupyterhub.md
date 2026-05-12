# JupyterHub on the DGX Spark — instructor runbook

Browser-based JupyterLab for up to 15 concurrent students, reachable from any network. Each student gets their own user account, their own home directory, and a one-click link that pulls the latest lab notebooks. All notebooks share the Spark's existing Ollama daemon.

If you're a TA picking this up next semester: follow the steps top-to-bottom. ~30 min total, mostly waiting.

## Architecture

```
Student browser
     │ HTTPS
     ▼
*.trycloudflare.com   (Cloudflare quick tunnel — free, ephemeral hostname)
     │ tunnel
     ▼
Spark :80             (TLJH + traefik → JupyterHub)
     │
     ├── per-user JupyterLab (1 per logged-in student)
     │        │
     │        ▼
     └── shared Ollama on :11434 (qwen3.5:4b kept resident)
```

## Stack

| Layer | Tool |
|---|---|
| Multi-user notebooks | [The Littlest JupyterHub (TLJH)](https://tljh.jupyter.org/) |
| Notebook distribution | [`nbgitpuller`](https://nbgitpuller.readthedocs.io/) — pulls the repo into each student's home dir via a magic link, merges instructor updates without clobbering edits |
| Auth | [`jupyterhub-firstuseauthenticator`](https://github.com/jupyterhub/firstuseauthenticator) — student picks their own password on first login |
| Public URL | [`cloudflared`](https://github.com/cloudflare/cloudflared) quick tunnel |
| LLM backend | Existing Ollama on `:11434` with `qwen3.5:4b` |

## Downloads (≈ 2 GB)

| What | Source | Size |
|---|---|---|
| TLJH bootstrap + JupyterHub/JupyterLab + traefik | `tljh.jupyter.org` → PyPI | ~1 GB |
| `jupyterhub-firstuseauthenticator` | PyPI | < 1 MB |
| `nbgitpuller` | PyPI | < 1 MB |
| Lab Python deps (langchain, langgraph, ollama, numexpr, ddgs, jupyter, …) | PyPI via `uv export` → `pip install` | ~800 MB |
| `cloudflared` (linux-arm64 .deb) | `github.com/cloudflare/cloudflared/releases/latest` | ~30 MB |

No model pulls needed — the existing Ollama daemon already has `qwen3.5:4b`.

## Prereqs

- DGX Spark with the existing Ollama daemon running on `:11434` (`systemctl status ollama` should be `active`).
- A user with passwordless sudo (the install uses `agentsmith` as the admin name — adjust if running as someone else).
- Public internet access from the Spark (for PyPI + the Cloudflare tunnel).

## Step 1 — Install TLJH

```bash
sudo apt-get update -qq && sudo apt-get install -y -qq python3 curl

curl -fsSL https://tljh.jupyter.org/bootstrap.py -o /tmp/tljh-bootstrap.py
sudo -E python3 /tmp/tljh-bootstrap.py --admin agentsmith 2>&1 | tee /tmp/tljh-install.log
```

Takes ~5–10 min. Installs JupyterHub + JupyterLab + traefik into `/opt/tljh/`, sets up systemd units (`jupyterhub.service`, `traefik.service`), binds traefik on port 80.

Verify:
```bash
sudo systemctl status jupyterhub traefik --no-pager
curl -sI http://localhost/hub/ | head -1   # expect: HTTP/1.1 200 OK (or 302 redirect to /hub/login)
```

## Step 2 — Configure auth + install nbgitpuller

`FirstUseAuthenticator` lets each student set their own password on first login. `nbgitpuller` lives in the per-student JupyterLab env, not the hub env.

```bash
sudo /opt/tljh/hub/bin/pip install jupyterhub-firstuseauthenticator
sudo tljh-config set auth.type firstuseauthenticator.FirstUseAuthenticator
sudo tljh-config set auth.FirstUseAuthenticator.create_users true
sudo tljh-config reload

sudo -E /opt/tljh/user/bin/pip install nbgitpuller
```

## Step 3 — Install the lab's Python deps into the shared user env

Mirror `lab01_sol/pyproject.toml` into TLJH's shared user env so `import ollama`, `import langchain`, etc. all just work — no per-student `uv sync`.

```bash
cd /home/agentsmith/cwilsch/agentic_ai/lab01_sol
uv export --format requirements-txt --no-hashes -o /tmp/lab01_reqs.txt
sudo -E /opt/tljh/user/bin/pip install -r /tmp/lab01_reqs.txt
```

The TLJH user env is shared across all students — install once, everyone gets it.

## Step 4 — Tune Ollama for shared use

Keep the model resident, allow concurrent inferences:

```bash
sudo mkdir -p /etc/systemd/system/ollama.service.d
sudo tee /etc/systemd/system/ollama.service.d/override.conf >/dev/null <<'EOF'
[Service]
Environment="OLLAMA_NUM_PARALLEL=4"
Environment="OLLAMA_KEEP_ALIVE=24h"
Environment="OLLAMA_MAX_LOADED_MODELS=2"
EOF

sudo systemctl daemon-reload
sudo systemctl restart ollama
ollama ps   # qwen3.5:4b should be listed once warmed up
```

`OLLAMA_NUM_PARALLEL=4` is sized for ~15 students who only intermittently hit `ollama.chat()`. Bump to 6–8 if you see queuing during a lab session.

## Step 5 — Cloudflare tunnel

The Spark doesn't need a public IP — `cloudflared` opens an outbound tunnel to Cloudflare's edge, which gives you a `*.trycloudflare.com` URL.

```bash
curl -L --output /tmp/cloudflared.deb \
  https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64.deb
sudo dpkg -i /tmp/cloudflared.deb

sudo tee /etc/systemd/system/cloudflared-lab.service >/dev/null <<'EOF'
[Unit]
Description=Cloudflare tunnel for JupyterHub lab
After=network.target

[Service]
ExecStart=/usr/local/bin/cloudflared tunnel --url http://localhost:80 --no-autoupdate
Restart=on-failure
User=nobody

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now cloudflared-lab
sudo journalctl -u cloudflared-lab -n 30 --no-pager   # extract the trycloudflare.com URL
```

> ⚠️ The hostname **changes every time `cloudflared-lab` restarts**. For a stable semester-long URL, upgrade to a named tunnel + DNS later (`cloudflared tunnel create lab`). The rest of this setup stays unchanged.

## Step 6 — Build and share the student link

Replace `<random>` with the hostname from `journalctl`. Hand students this single URL:

```
https://<random>.trycloudflare.com/hub/user-redirect/git-pull?repo=https://github.com/chriscrossapplesauce2001/agentic_ai&branch=master&urlpath=lab/tree/agentic_ai/lab01_sol/exercise0/exercise0.ipynb
```

First click per student:
1. TLJH login page → they pick a username + password (FirstUseAuthenticator records both).
2. nbgitpuller clones the repo into `~/agentic_ai/`.
3. JupyterLab opens directly on `exercise0.ipynb`.

Subsequent clicks merge upstream notebook changes into their working copy without overwriting their edits — push to `master` mid-semester and the next click pulls the update.

## Verification

Before sharing the link with students:

1. `curl -I http://localhost/hub` → `200` or `302`.
2. Open `http://localhost` on the Spark, log in as `agentsmith`, set a password.
3. Visit the local git-pull URL: `http://localhost/hub/user-redirect/git-pull?repo=https://github.com/chriscrossapplesauce2001/agentic_ai&branch=master&urlpath=lab/tree/agentic_ai/lab01_sol/exercise0/exercise0.ipynb` → notebook opens, repo at `~/agentic_ai/`.
4. Run cell 0 of `exercise0.ipynb` → prints `OK`. Run cell 5 → completes without errors.
5. Open the public trycloudflare URL on a device off the Spark's network (phone on cellular is easiest). Repeat step 3 against the public URL.
6. Open a second browser / incognito, sign up as a different username, run the notebook in parallel. Both should respond; `ollama ps` should still show one loaded model.

## User management

**Default behavior:** anyone with the magic link picks a username + password on the login page and gets an account on the spot (`FirstUseAuthenticator` + `create_users: true`). No pre-provisioning needed — just share the link.

To **restrict signups to a roster**, set an allow-list. Anyone outside the list is rejected at login; existing users are unaffected:

```bash
sudo tljh-config add-item auth.FirstUseAuthenticator.allowed_users alice
sudo tljh-config add-item auth.FirstUseAuthenticator.allowed_users bob
sudo tljh-config add-item auth.FirstUseAuthenticator.allowed_users carol
sudo tljh-config reload
```

Each semester: edit the list, `tljh-config reload`, share the same link. Old students keep their accounts unless you delete them explicitly.

Other common operations:

| What | Command |
|---|---|
| Make someone an admin (sudoers + hub-admin UI) | `sudo tljh-config add-item users.admin alice && sudo tljh-config reload` |
| List who has signed up so far | `ls /home/ \| grep ^jupyter-` |
| Reset a forgotten password | `sudo /opt/tljh/hub/bin/jupyterhub-firstuseauthenticator-reset alice` — they pick a new one on next login |
| Remove a user completely | `sudo userdel -r jupyter-alice` then remove the row from `/opt/tljh/state/jupyterhub.sqlite` (or `sudo /opt/tljh/hub/bin/jupyterhub --remove-user alice` depending on version) |
| See current config | `sudo tljh-config show` |

## Day-to-day ops

- **Pushing notebook updates:** push to `master` on GitHub. Students' next click of the magic link auto-merges; their answers in modified cells are preserved (three-way merge).
- **Disk usage per student:** each home dir is `/home/jupyter-<username>/`. The repo clone is ~50 MB; growth comes from any data files students download. Check with `sudo du -sh /home/jupyter-*`.
- **Rotating the tunnel URL:** `sudo systemctl restart cloudflared-lab && sudo journalctl -u cloudflared-lab -n 30 --no-pager | grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' | head -1`.
- **Disabling the tunnel after the semester:** `sudo systemctl disable --now cloudflared-lab`.
- **Hitting the GB10:** lower `OLLAMA_NUM_PARALLEL` (or `pull qwen3.5:0.8b` and have students switch the model string — other sub-projects in this repo already use it).

## Conflicts / things to know

- **Port 7860** is auto-forwarded from the Spark by NVIDIA Sync. Doesn't collide with this stack (TLJH = 80, Ollama = 11434, cloudflared = outbound). It *will* collide with manual SSH tunnels or future Gradio demos on 7860.
- **TLJH on aarch64:** TLJH is pure Python and works on ARM64. PyPI wheels for most lab deps are available for `aarch64`; a few (rare) packages may build from source on first install.
- **Concurrent Ollama users:** the single GB10 serves all students from one loaded model via `OLLAMA_NUM_PARALLEL`. Don't pull additional 4B+ models without raising VRAM headroom — `OLLAMA_MAX_LOADED_MODELS=2` is a soft cap.

## Out of scope

- **nbgrader** for auto-grading — easy to add on top of TLJH later, not needed for exploratory exercises like `exercise0`.
- **Named Cloudflare tunnel + custom domain** — defer until quick tunnel proves the concept.
- **Per-user GPU quota** — TLJH has memory limits but no native GPU partitioning; with ≤15 students and Ollama batching, not needed.
