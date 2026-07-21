#!/usr/bin/env python3
"""Local web GUI for the grading pipeline: the same buttons as grading_console.ipynb, but in a
browser instead of a notebook. Stdlib only (http.server), no new dependencies.

Run on the Spark, from lab01/ so the uv env's `ollama` is on the path:

    cd lab01
    uv run python _solutions/grading/grading_web.py        # -> http://127.0.0.1:8765

Then open the URL. It binds to 127.0.0.1 ONLY (the buttons can run grading with sudo, so it
must not be exposed). If you are remote, reach it with an SSH tunnel:

    ssh -L 8765:127.0.0.1:8765 <you>@<spark>

Buttons just call the same scripts as the notebook, streaming their output live (Server-Sent
Events). LAB / JUDGE_MODEL are injected via an `env VAR=val` prefix so they survive sudo.
"""
import json
import os
import re
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

HOST = "127.0.0.1"
PORT = int(os.environ.get("GRADING_PORT", "8765"))
HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.abspath(os.path.join(HERE, "..", ".."))          # lab01/
G = os.path.join("_solutions", "grading")                       # relative to LAB
PY = sys.executable
STATUS_FILE = os.path.join(LAB, "submissions", "status.json")
GRADEBOOK = os.path.join(LAB, "gradebook_lab01.html")
PROG = re.compile(r"@PROGRESS (\d+)/(\d+)")

SCRIPTS = {"collect_and_grade.py", "publish_grades.py", "build_gradebook.py", "read_appeals.py"}
SUDO_SCRIPTS = {"collect_and_grade.py", "read_appeals.py"}       # these read/write student homes


def local_models():
    try:
        out = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=10).stdout
        return [ln.split()[0] for ln in out.splitlines()[1:] if ln.strip()]
    except Exception:
        return []


def load_status():
    try:
        return json.load(open(STATUS_FILE, encoding="utf-8"))
    except Exception:
        return {}


def build_cmd(script, extra, lab, model):
    sudo = script in SUDO_SCRIPTS or (script == "publish_grades.py" and "--dry-run" not in extra)
    envargs = [f"LAB={lab or 'lab01'}"]
    if model and not model.startswith("(default"):
        envargs.append(f"JUDGE_MODEL={model}")
    return (["sudo", "-n"] if sudo else []) + ["env"] + envargs + \
        [PY, os.path.join(G, script)] + extra


PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Lab grading</title>
<style>
:root{color-scheme:light dark}
body{font:15px/1.5 system-ui,sans-serif;margin:0;padding:22px;max-width:920px}
h1{font-size:20px;margin:0 0 2px}.sub{color:#888;font-size:13px;margin-bottom:14px}
.panel{border:1px solid #8884;border-radius:10px;padding:10px 14px;margin:8px 0;background:#8881;font-size:13px}
.panel td{padding:2px 14px 2px 0}.panel .k{color:#888}.never{color:#c0392b}
.row{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin:8px 0}
label{color:#888;font-size:13px}
input,select{padding:6px 8px;font-size:14px;border:1px solid #999;border-radius:6px;background:transparent;color:inherit}
.grp{font-size:12px;color:#888;margin:10px 0 4px}
button{border:0;border-radius:8px;padding:9px 14px;font-size:14px;font-weight:600;cursor:pointer;color:#fff}
button:disabled{opacity:.5;cursor:default}
.b-primary{background:#2d6cdf}.b-plain{background:#6b7280}.b-ok{background:#2f9e44}
.b-warn{background:#e8890c}.b-ghost{background:#6b7280}
progress{width:320px;height:16px;vertical-align:middle}
#st{font-weight:600;margin-left:8px}
#log{background:#0f141b;color:#cdd9e5;border:1px solid #223;border-radius:10px;padding:10px 12px;
  height:340px;overflow:auto;white-space:pre-wrap;
  font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12px;line-height:1.45;margin-top:8px}
</style></head><body>
<h1>Lab grading</h1>
<div class="sub">weekly loop: collect+grade &rarr; preview &rarr; gradebook &rarr; publish &rarr; appeals</div>
<div class="panel" id="panel">loading status&hellip;</div>
<div class="row">
  <label>LAB <input id="lab" value="lab01" size="8"></label>
  <label>JUDGE_MODEL <select id="model"></select></label>
</div>
<div class="grp">grade &amp; review</div>
<div class="row">
  <button class="b-primary" onclick="go('collect_and_grade.py')">1 · Collect + grade</button>
  <button class="b-plain" onclick="go('publish_grades.py','--dry-run')">2 · Preview (safe)</button>
  <button class="b-ok" onclick="gradebook()">View gradebook</button>
</div>
<div class="grp">release</div>
<div class="row">
  <button class="b-warn" onclick="go('publish_grades.py')">3 · Publish to students</button>
  <button class="b-ghost" onclick="go('read_appeals.py')">4 · Read appeals</button>
</div>
<div class="row">
  <progress id="bar" max="1" value="0"></progress><span id="st"></span>
  <button class="b-ghost" style="margin-left:auto" onclick="log.textContent=''">clear log</button>
</div>
<div id="log"></div>
<script>
const log=document.getElementById('log'), bar=document.getElementById('bar'),
      st=document.getElementById('st'), panel=document.getElementById('panel');
let busy=false;
function esc(s){return s.replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]))}
async function models(){
  const m=await (await fetch('models')).json();
  document.getElementById('model').innerHTML=
    ['(default: nemotron-3-super:latest)'].concat(m).map(x=>`<option>${esc(x)}</option>`).join('');
}
async function status(){
  const s=await (await fetch('status')).json();
  const row=(k,label,f)=>{const d=s[k];return d
    ?`<tr><td class=k>${label}</td><td><b>${d.time}</b> &nbsp;<span class=k>${f(d)}</span></td></tr>`
    :`<tr><td class=k>${label}</td><td class=never>never</td></tr>`};
  panel.innerHTML='<b>Status</b><table>'
    +row('graded','last collect + grade',d=>`${d.model||'?'} · ${d.students||0} students, ${d.graded||0} notebooks`)
    +row('published','last publish',d=>`${d.published||0} students`)
    +row('appeals','last read appeals',d=>`${d.count||0} appeal(s)`)+'</table>';
}
function setBusy(b){busy=b;document.querySelectorAll('button').forEach(x=>x.disabled=b)}
function go(script,extra,onDone){
  if(busy)return; setBusy(true); log.textContent=''; st.textContent='running…';
  bar.value=0; bar.max=1; bar.removeAttribute('value');   // indeterminate until first progress
  const q=new URLSearchParams({script,lab:document.getElementById('lab').value,
    model:document.getElementById('model').value}); if(extra)q.append('extra',extra);
  const es=new EventSource('run?'+q.toString());
  es.addEventListener('log',e=>{log.textContent+=JSON.parse(e.data).line;log.scrollTop=log.scrollHeight});
  es.addEventListener('progress',e=>{const d=JSON.parse(e.data);bar.max=d.total||1;bar.value=d.done});
  es.addEventListener('done',e=>{const rc=JSON.parse(e.data).rc;
    st.textContent=rc===0?'done ✓':'exit '+rc; if(bar.value==0){bar.max=1;bar.value=1}
    es.close(); setBusy(false); status(); if(onDone&&rc===0)onDone();});
  es.onerror=()=>{st.textContent='connection lost';es.close();setBusy(false)};
}
function gradebook(){go('build_gradebook.py',null,()=>window.open('gradebook','_blank'))}
models(); status();
</script></body></html>"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass  # quiet

    def _headers(self, code, ctype):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.end_headers()

    def _json(self, obj):
        self._headers(200, "application/json")
        self.wfile.write(json.dumps(obj).encode())

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/":
            self._headers(200, "text/html; charset=utf-8")
            self.wfile.write(PAGE.encode())
        elif path == "/models":
            self._json(local_models())
        elif path == "/status":
            self._json(load_status())
        elif path == "/gradebook":
            if os.path.isfile(GRADEBOOK):
                self._headers(200, "text/html; charset=utf-8")
                self.wfile.write(open(GRADEBOOK, "rb").read())
            else:
                self._headers(404, "text/plain")
                self.wfile.write(b"No gradebook yet. Click 'View gradebook' first.")
        elif path == "/run":
            self._run(parse_qs(urlparse(self.path).query))
        else:
            self._headers(404, "text/plain")
            self.wfile.write(b"not found")

    def _event(self, kind, obj):
        self.wfile.write(f"event: {kind}\ndata: {json.dumps(obj)}\n\n".encode())
        self.wfile.flush()

    def _run(self, q):
        script = q.get("script", [""])[0]
        if script not in SCRIPTS:
            self._headers(400, "text/plain")
            self.wfile.write(b"unknown script")
            return
        extra = q.get("extra", [])
        cmd = build_cmd(script, extra, q.get("lab", ["lab01"])[0], q.get("model", [""])[0])
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        try:
            self._event("log", {"line": "$ " + " ".join(cmd) + "\n\n"})
            p = subprocess.Popen(cmd, cwd=LAB, text=True, bufsize=1,
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for ln in p.stdout:
                m = PROG.match(ln.strip())
                if m:
                    self._event("progress", {"done": int(m.group(1)), "total": int(m.group(2))})
                else:
                    self._event("log", {"line": ln})
            rc = p.wait()
            self._event("log", {"line": "\n" + "-" * 60 + f"  [exit {rc}]\n"})
            self._event("done", {"rc": rc})
        except (BrokenPipeError, ConnectionResetError):
            pass  # client navigated away mid-stream


def main():
    srv = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Grading web GUI on http://{HOST}:{PORT}  (Ctrl-C to stop)")
    print(f"Remote? tunnel first:  ssh -L {PORT}:127.0.0.1:{PORT} <you>@<spark>")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")


if __name__ == "__main__":
    main()
