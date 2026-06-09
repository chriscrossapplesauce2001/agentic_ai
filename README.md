# Agentic AI — Lab Material

Teaching material for the **Agentic AI** module: Jupyter-based labs in which students
implement agentic AI concepts (ReAct, tool use, function calling, MCP) themselves, step by
step. The LLM backend is a locally running **Ollama** on the DGX Spark, so no cloud API keys
are needed for inference.

## Structure

| Folder | Contents |
|---|---|
| **lab01/** | Lab 1 — ReAct agents with Ollama. The student-facing notebooks (`exercise0` = LLM basics on-ramp, through `exercise3` = LangChain) and setup instructions in [`lab01/README.md`](lab01/README.md). The internal answer key and auto-grader live in `lab01/_solutions/` (see below). |
| **materials/** | Documents provided by the module lead (module description, teaching units, lab catalog). |
| **infra/** | Deployment runbook: JupyterHub on the Spark, which delivers the notebooks to students ([`infra/jupyterhub.md`](infra/jupyterhub.md)). |
| **literature/** | Curated literature review on Agentic AI (sources, tables, summaries). |
| **_superseded/** | Earlier exploratory phase (standalone LangChain / LangGraph / Ollama sub-projects, voice experiments, benchmarks). No longer needed for the current lab, kept for reference. |
| `notizen.md` | Working notes and meeting minutes (German). |

## Quick start (Lab 1)

```bash
ollama pull qwen3.5:4b      # model the students use
cd lab01
uv sync                     # creates .venv/ and installs dependencies
uv run jupyter notebook     # open the notebooks
```

Full instructions (uv installation, Jupyter kernel, exercise overview) are in
[`lab01/README.md`](lab01/README.md).

## Solutions & grading (internal)

`lab01/_solutions/` holds the reference solution notebooks and the auto-grading system
(`lab01/_solutions/grading/`). The grader checks submitted notebooks against a solution key:
free-text answers are scored by a local judge LLM, code TODOs deterministically via regex.
Details in [`lab01/_solutions/grading/README.md`](lab01/_solutions/grading/README.md).

> **Note:** this material is internal. While the repo is public and nbgitpuller clones the
> whole repo to students, `_solutions/` is reachable by them; serve a student branch without
> it (or keep it private) before the lab goes live.
