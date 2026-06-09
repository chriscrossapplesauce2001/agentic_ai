# Agentic AI — Laborunterlagen

Lehrmaterial zum Modul **Agentic AI**: Jupyter-basierte Labore, in denen Studierende
agentische KI-Konzepte (ReAct, Tool-Use, Function Calling, MCP) Schritt für Schritt
selbst implementieren. LLM-Backend ist ein lokal laufendes **Ollama** auf dem DGX Spark,
es werden keine Cloud-API-Schlüssel benötigt.

## Struktur

| Ordner | Inhalt |
|---|---|
| **lab01/** | Lab 1 — ReAct-Agenten mit Ollama. Die studierendenseitigen Notebooks (`exercise0`–`exercise2`) inklusive Setup-Anleitung in [`lab01/README.md`](lab01/README.md). |
| **lab01_sol/** | Musterlösungen zu Lab 1 **plus** das automatische Bewertungssystem in `lab01_sol/grading/`. *Intern — nicht an Studierende verteilen.* |
| **materials/** | Vom Modulverantwortlichen bereitgestellte Unterlagen (Modulbeschreibung, Lehreinheiten, Labor-Katalog). |
| **infra/** | Deployment-Runbook: JupyterHub auf dem Spark, das die Notebooks an die Studierenden ausliefert ([`infra/jupyterhub.md`](infra/jupyterhub.md)). |
| **literature/** | Kuratierter Literaturüberblick zu Agentic AI (Quellen, Tabellen, Zusammenfassungen). |
| **_superseded/** | Frühere Experimentierphase (eigenständige LangChain-/LangGraph-/Ollama-Teilprojekte, Voice-Experimente, Benchmarks). Für das aktuelle Lab nicht mehr benötigt, zur Nachvollziehbarkeit aufbewahrt. |
| `notizen.md` | Laufende Arbeitsnotizen und Besprechungsprotokolle. |

## Schnellstart (Lab 1)

```bash
ollama pull qwen3.5:4b      # Modell, das die Studierenden nutzen
cd lab01
uv sync                     # erstellt .venv/ und installiert Abhängigkeiten
uv run jupyter notebook     # Notebooks öffnen
```

Die vollständige Anleitung (uv-Installation, Jupyter-Kernel, Übungsübersicht) steht in
[`lab01/README.md`](lab01/README.md).

## Bewertung

Das automatische Grading (`lab01_sol/grading/`) prüft abgegebene Notebooks gegen eine
Musterlösung: Freitext-Antworten werden von einem lokalen Judge-LLM bewertet, Code-TODOs
deterministisch per Regex. Details in [`lab01_sol/grading/README.md`](lab01_sol/grading/README.md).
