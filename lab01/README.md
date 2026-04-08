# Labor 1: ReAct-Agenten mit Ollama

## Lernziele

- Das ReAct-Pattern (Reason + Act) verstehen und implementieren
- Einen tool-calling Agenten von Hand mit dem Ollama Python SDK bauen
- Den gleichen Agenten mit LangChain/LangGraph bauen
- Beide Ansaetze vergleichen

## Voraussetzungen

- Python 3.10 oder neuer
- [Ollama](https://ollama.com/) installiert

## Setup

### 1. Ollama installieren und Modell herunterladen

```bash
# Ollama installieren (falls noch nicht geschehen)
# Linux:
curl -fsSL https://ollama.com/install.sh | sh

# Windows/macOS: Download von https://ollama.com/

# Modell herunterladen (~2.5 GB)
ollama pull qwen3.5:4b
```

Pruefe ob Ollama laeuft:

```bash
ollama list
```

Dort sollte `qwen3.5:4b` auftauchen.

### 2. Virtual Environment erstellen

```bash
cd lab01

# venv erstellen
python -m venv .venv

# Aktivieren:
# Linux / macOS:
source .venv/bin/activate

# Windows (PowerShell):
.venv\Scripts\Activate.ps1

# Windows (Git Bash):
source .venv/Scripts/activate
```

### 3. Dependencies installieren

```bash
pip install -r requirements.txt
```

### 4. Jupyter Kernel registrieren

```bash
python -m ipykernel install --user --name lab01 --display-name "Lab 01"
```

### 5. Jupyter starten

```bash
jupyter notebook
```

## Aufgaben

| Aufgabe | Beschreibung | Datei |
|---------|-------------|-------|
| **Aufgabe 1** | ReAct-Agent von Hand mit Ollama SDK | `aufgabe1/aufgabe1.ipynb` |
| **Aufgabe 2** | ReAct-Agent mit LangChain/LangGraph | `aufgabe2/aufgabe2.ipynb` |

Oeffne die Notebooks in Jupyter und folge den Anweisungen. Jedes Notebook enthaelt Erklaerungen (Markdown-Zellen) und Code-Zellen mit `# TODO`-Markierungen, die ihr ausfuellen muesst.

**Wichtig:** Waehlt in Jupyter den Kernel **"Lab 01"** aus (oben rechts).

## Testen

Wenn beide Aufgaben fertig sind, koennt ihr den automatischen Test ausfuehren:

```bash
python -m pytest test_agent.py -v
```

Der Test prueft ob eure Agenten:
- Einen String zurueckgeben
- Den Calculator-Tool korrekt nutzen
- Dateien lesen koennen
- Mehrstufige Berechnungen durchfuehren

## Hintergrund: Was ist ein ReAct-Agent?

Ein ReAct-Agent kombiniert **Reasoning** (Nachdenken) mit **Acting** (Handeln) in einer Schleife:

```
Benutzer-Frage
      |
      v
+---> LLM denkt nach (Reasoning)
|     |
|     v
|   Tool-Aufruf noetig?
|     |          |
|    Ja         Nein
|     |          |
|     v          v
|   Tool        Finale Antwort
|   ausfuehren    ausgeben
|     |
|     v
|   Ergebnis zurueck
|   an LLM
+-----+
```

Der Agent entscheidet selbst welches Tool er braucht, ruft es auf, bekommt das Ergebnis, und denkt weiter — bis er eine finale Antwort geben kann.

### Verfuegbare Tools in diesem Lab

| Tool | Beschreibung | Beispiel |
|------|-------------|---------|
| `calculator` | Mathematische Ausdruecke berechnen | `(0.2 * 0.4**3) / 12` |
| `read_file` | Lokale Textdatei lesen | `sample.txt` |
| `web_search` | DuckDuckGo-Websuche | `"Young's modulus steel S235"` |
