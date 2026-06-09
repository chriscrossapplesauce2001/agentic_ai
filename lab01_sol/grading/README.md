# Lab 01 Auto-Grading

**Intern. Nicht an Studierende verteilen, und nicht in das öffentliche Repo pushen** (siehe Warnung unten).

Gradet eine abgegebene Lab-01-Submission gegen die Musterlösung:
- **Exercise 0** (Freitext "Your Turn"-Antworten): von einem **Judge-LLM** bewertet, einer Frage nach der anderen, gegen die Rubrik in `rubric.json`.
- **Exercise 1** (Code-TODOs): **deterministisch** geprüft (anchored Regex auf den `run_agent`-Code), kein LLM.

## Dateien

| Datei | Zweck |
|---|---|
| `MUSTERLOESUNG.md` | Menschenlesbare Rubrik (`✓ / ± / ✗`) |
| `rubric.json` | Maschinenlesbare Rubrik, die `grade.py` einliest |
| `grade.py` | Der Grader (nur stdlib + `ollama`) |

## Abgabe-Konvention

Studierende taggen jede Antwort mit ihrer Frage-ID, irgendwo im Notebook (Code-Kommentar oder Markdown-Zelle):

```python
# P1.Q1: Ohne <think> verschwindet der Reasoning-Block, die Antwort kommt direkt.
# P1.Q2: Läuft weiter. Das Stop-Token <|im_end|> stoppt, nicht die Text-Anweisung.
```

Der Grader zieht den Text nach jedem Tag bis zum nächsten Tag. Fehlt ein Tag, wird die Frage als `missing` gewertet (kein LLM-Call).

> **Stand:** `lab01/exercise0/exercise0.ipynb` ist gepatcht: jede "Your Turn"-Zelle weist auf das Tagging hin und hat darunter eine **Answers**-Zelle mit vorausgefüllten `P{part}.Q{n}:`-Stubs. Studierende schreiben nur hinter den Doppelpunkt. (Exercise 1 ist Code und braucht keine Tags.)

## Benutzung

```bash
# Judge-Modell setzen (irgendein 8B+ Modell, das auf dem Spark gepullt ist):
ollama pull qwen3.5:14b
export JUDGE_MODEL=qwen3.5:14b

python3 grade.py abgabe_student_ex0.ipynb abgabe_student_ex1.ipynb
python3 grade.py --dry-run abgabe.ipynb   # nur Antworten extrahieren, kein LLM
```

Pro Notebook wird ein `*.grade.json` mit den Labels (`correct / partial / incorrect / missing`) geschrieben. Routing (Code vs. Freitext) passiert automatisch anhand des Inhalts.

## Bewusste Designentscheidungen

- **Judge = größeres Modell als die Studierenden.** Grading läuft offline/batch über ≤15 Abgaben, Latenz egal. `temperature=0`, `format=json` für 100% parsebaren Output.
- **Eine Frage pro LLM-Call**, mit der Rubrik nur für diese Frage: kleiner Kontext, eine Entscheidung. Zuverlässiger als das ganze Notebook auf einmal.
- **3-Stufen-Label statt 0–100-Score.** Kleine/mittlere Modelle kalibrieren keine feine Skala, aber matchen Antworten gegen explizite Kernpunkte.
- **Code wird nicht vom LLM gegradet.** Die TODOs haben deterministische Lösungen.

## Grenzen

- Der Code-Check ist ein **Smoke-Test** (Regex), keine Ausführung. Robuster wäre: das Notebook ausführen / `pytest` gegen die drei Test-Queries laufen lassen (braucht laufendes Ollama + Netz für `web_search`). Für eine echte Note diesen Pfad ergänzen.
- Für Grenzfälle (`partial`) empfiehlt sich menschliche Nachkontrolle: bei 15 Abgaben wenige Minuten.

## ⚠️ Warnung: öffentliches Repo

Die Lab-Notebooks werden den Studierenden per nbgitpuller aus einem **öffentlichen GitHub-Repo** ausgeliefert (`github.com/chriscrossapplesauce2001/agentic_ai`). Alles in diesem Repo ist für Studierende über die GitHub-URL erreichbar, auch `lab01_sol/`. Dieser `grading/`-Ordner (Musterlösung + Rubrik) darf **nicht** in das öffentliche Remote gepusht werden: per `.gitignore` ausschließen oder in einem separaten privaten Repo halten.
