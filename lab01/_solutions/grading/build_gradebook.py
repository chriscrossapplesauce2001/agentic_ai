#!/usr/bin/env python3
"""Build one self-contained HTML gradebook from the graded submissions.

Reads submissions/<student>/*.grade.json (preferring *.manual.json, same rule as
publish_grades.py) and writes a single gradebook_<lab>.html: one sortable, colour-coded
row per student; click a row to expand the AI's per-question score + verdict + reason.

It is a plain file: no server, opens in any browser, and can sit in JupyterHub. Re-run it
whenever you re-grade; it just overwrites the HTML.

Usage
-----
    cd lab01
    uv run python _solutions/grading/build_gradebook.py          # -> gradebook_lab01.html
    # open the file from the Jupyter file browser (or any browser)

Env overrides:
    LAB          label in the title + filename       (default: lab01)
    SUBMISSIONS  where the .grade.json files live     (default: ./submissions)
"""
import datetime
import glob
import html
import json
import os
import sys

LAB = os.environ.get("LAB", "lab01")
SUBMISSIONS = os.environ.get("SUBMISSIONS", os.path.abspath("submissions"))
OUT = os.path.abspath(f"gradebook_{LAB}.html")


def load_grades(student_dir):
    """key -> (payload, source). Manual override wins. Only graded payloads kept."""
    grades = {}
    for kind in ("grade", "manual"):  # manual read second -> wins
        for path in sorted(glob.glob(os.path.join(student_dir, f"*.{kind}.json"))):
            key = os.path.basename(path)[: -len(f".{kind}.json")]
            try:
                payload = json.load(open(path, encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            if isinstance(payload, dict) and "questions" in payload:
                grades[key] = (payload, "manual" if kind == "manual" else "ai")
    return grades


def pct_class(total, mx):
    if not mx:
        return "na"
    p = total / mx
    return "good" if p >= 0.8 else "mid" if p >= 0.5 else "low"


def label_class(label):
    return {"correct": "good", "partial": "mid", "incorrect": "low",
            "missing": "na"}.get(str(label).lower(), "na")


def esc(x):
    return html.escape(str(x))


def main():
    dirs = sorted(p for p in glob.glob(os.path.join(SUBMISSIONS, "*")) if os.path.isdir(p))
    if not dirs:
        sys.exit(f"No student folders in {SUBMISSIONS!r}. Run collect_and_grade.py first.")

    students = []          # (name, {key: (payload, source)})
    keys = []              # ordered exercise keys seen across everyone
    for d in dirs:
        grades = load_grades(d)
        students.append((os.path.basename(d), grades))
        for k in grades:
            if k not in keys:
                keys.append(k)
    keys.sort()

    # --- table rows ---
    body, totals = [], []
    for name, grades in students:
        cells, s_total, s_max, detail = [], 0.0, 0, []
        for k in keys:
            if k in grades:
                payload, source = grades[k]
                t, m = payload.get("total", 0), payload.get("max", 0)
                s_total += t
                s_max += m
                tag = " *" if source == "manual" else ""
                cells.append(f'<td class="{pct_class(t, m)}">{t:g} / {m}{tag}</td>')
                detail.append(f'<div class="ex"><b>{esc(k)}</b>{" (instructor-reviewed)" if source=="manual" else ""}</div>')
                for qid, r in payload["questions"].items():
                    detail.append(
                        f'<div class="q"><span class="pill {label_class(r.get("label"))}">'
                        f'{esc(r.get("label",""))}</span> <b>{esc(qid)}</b> '
                        f'<span class="sc">{r.get("score",0):g}</span>'
                        f'<div class="why">{esc(r.get("reason",""))}</div></div>')
            else:
                cells.append('<td class="na">-</td>')
        totals.append(s_total)
        pctc = pct_class(s_total, s_max)
        body.append(
            f'<tr class="row" data-student="{esc(name)}" data-total="{s_total}" '
            f'onclick="t(this)"><td class="name">{esc(name)}</td>'
            f'{"".join(cells)}<td class="{pctc} tot"><b>{s_total:g} / {s_max}</b></td></tr>')
        body.append(f'<tr class="detail" hidden><td colspan="{len(keys)+2}">'
                    f'{"".join(detail) or "no grade"}</td></tr>')

    graded = [t for t in totals]
    avg = sum(graded) / len(graded) if graded else 0
    head_ex = "".join(f'<th onclick="s(\'{k}\',0)">{esc(k)}</th>' for k in keys)
    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Gradebook {esc(LAB)}</title><style>
:root{{color-scheme:light dark}}
body{{font:15px/1.5 system-ui,sans-serif;margin:0;padding:24px;max-width:1000px}}
h1{{font-size:20px;margin:0 0 4px}}.sub{{color:#888;font-size:13px;margin-bottom:16px}}
input{{padding:6px 10px;font-size:14px;width:220px;margin-bottom:12px;
  border:1px solid #bbb;border-radius:6px}}
table{{border-collapse:collapse;width:100%}}
th,td{{padding:8px 10px;text-align:left;border-bottom:1px solid #8883}}
th{{cursor:pointer;user-select:none;font-size:13px;color:#888;white-space:nowrap}}
th:hover{{color:inherit}}
.row{{cursor:pointer}}.row:hover{{background:#8881}}
.name{{font-weight:600}}.tot{{text-align:right}}
td.good{{background:#3ca35520}}td.mid{{background:#d99a2620}}td.low{{background:#d0454520}}
td.na{{color:#999}}
.pill{{display:inline-block;padding:1px 8px;border-radius:10px;font-size:12px;font-weight:600}}
.pill.good{{background:#3ca355;color:#fff}}.pill.mid{{background:#d99a26;color:#fff}}
.pill.low{{background:#d04545;color:#fff}}.pill.na{{background:#999;color:#fff}}
.detail td{{background:#8880;padding:12px 16px}}
.ex{{margin:10px 0 4px;color:#888;font-size:13px}}.ex:first-child{{margin-top:0}}
.q{{padding:6px 0;border-top:1px solid #8882}}
.q .sc{{float:right;color:#888}}.why{{color:#aaa;font-size:13px;margin-top:2px}}
</style></head><body>
<h1>Gradebook &middot; {esc(LAB)}</h1>
<div class="sub">{len(students)} students &middot; average {avg:.1f} &middot; generated {stamp}
 &middot; <b>*</b> = instructor-reviewed &middot; click a row for details</div>
<input id="f" placeholder="filter by name&hellip;" oninput="flt()">
<table><thead><tr>
<th onclick="s('student',1)">student</th>{head_ex}<th onclick="s('total',0)">total</th>
</tr></thead><tbody id="tb" data-sc="" data-dir="">
{chr(10).join(body)}
</tbody></table>
<script>
function t(r){{r.nextElementSibling.hidden=!r.nextElementSibling.hidden;}}
function s(col,txt){{
  var tb=document.getElementById('tb');
  var rows=[].slice.call(tb.querySelectorAll('tr.row'));
  var dir=(tb.dataset.sc==col&&tb.dataset.dir=='asc')?'desc':'asc';
  rows.sort(function(a,b){{
    var x=a.dataset[col==='student'?'student':'total'],y=b.dataset[col==='student'?'student':'total'];
    if(!txt){{x=parseFloat(x);y=parseFloat(y);}}else{{x=x.toLowerCase();y=y.toLowerCase();}}
    return (x<y?-1:x>y?1:0)*(dir=='asc'?1:-1);
  }});
  tb.dataset.sc=col;tb.dataset.dir=dir;
  rows.forEach(function(r){{tb.appendChild(r);tb.appendChild(r.nextElementSibling);}});
}}
function flt(){{
  var v=document.getElementById('f').value.toLowerCase();
  [].forEach.call(document.querySelectorAll('tr.row'),function(r){{
    var show=r.dataset.student.toLowerCase().indexOf(v)>-1;
    r.style.display=show?'':'none';r.nextElementSibling.hidden=true;
    r.nextElementSibling.style.display=show?'':'none';
  }});
}}
</script></body></html>"""

    with open(OUT, "w", encoding="utf-8") as f:
        f.write(doc)
    print(f"Wrote {OUT}  ({len(students)} students, average {avg:.1f})")
    print("Open it from the Jupyter file browser or any web browser.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
