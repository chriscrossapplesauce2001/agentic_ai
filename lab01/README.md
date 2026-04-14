# Labor 1: ReAct-Agenten mit Ollama

## LLM vs. Agent

**LLM**: Stateless API Call. Messages rein, Message raus.

**Agent**: Loop um ein LLM. Ruft das LLM auf, fuehrt Tool Calls aus, fuettert Ergebnisse als neue Messages zurueck — wiederholt bis das LLM keinen Tool Call mehr zurueckgibt.

```
LLM:    messages → response
Agent:  messages → [LLM → Tool Call → Tool Result]* → response
```

## Lernziele

- Das ReAct-Pattern (Reason + Act) verstehen und implementieren
- Einen tool-calling Agenten von Hand mit dem Ollama SDK bauen
- Den gleichen Agenten mit LangChain/LangGraph bauen

## Setup

### 1. Ollama + Modell

```bash
# Ollama installieren: https://ollama.com/
ollama pull qwen3.5:4b
ollama list   # qwen3.5:4b sollte auftauchen
```

### 2. Python-Umgebung

```bash
cd lab01

# Linux / macOS:
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt

# Windows (PowerShell):
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Jupyter Kernel registrieren

```bash
# Linux / macOS:
python3 -m ipykernel install --user --name lab01 --display-name "Lab 01"

# Windows:
python -m ipykernel install --user --name lab01 --display-name "Lab 01"
```

Dann die `.ipynb` Dateien oeffnen mit:
- **VS Code / PyCharm**: Datei direkt oeffnen, Kernel **"Lab 01"** auswaehlen
- **Browser**: `jupyter notebook` ausfuehren

## Aufgaben

| Aufgabe | Datei | Beschreibung |
|---------|-------|-------------|
| Ollama kennenlernen | `aufgabe0/aufgabe0.ipynb` | Rohes `ollama.chat()` verstehen: ohne Tools, mit History, mit Tools, manueller Tool-Roundtrip |
| ReAct-Agent von Hand (Ollama SDK) | `aufgabe1/aufgabe1.ipynb` | Den ReAct-Loop als `run_agent()` Funktion implementieren (4 TODOs) |
| ReAct-Agent mit LangChain | `aufgabe2/aufgabe2.ipynb` | Den gleichen Agenten mit LangChain/LangGraph bauen |

## Test

```bash
python3 -m pytest test_agent.py -v
```
