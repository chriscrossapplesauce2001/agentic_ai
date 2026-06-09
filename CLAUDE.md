# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository holds lecture and lab material for an academic module on **agentic AI**
(German-language context, engineering domain examples). The active deliverable is a set of
Jupyter-based labs in which students implement agentic concepts (ReAct, tool use, function
calling, MCP) themselves. The LLM backend is a locally running **Ollama** on a DGX Spark —
no cloud API keys are needed for inference.

The repo was restructured so the active lab material is front-and-center; earlier exploratory
work lives under `_superseded/` (see below).

## Layout

| Path | Purpose |
|---|---|
| **lab01/** | Lab 1 — ReAct agents with Ollama. Student-facing notebooks `exercise0`–`exercise2`, setup in `lab01/README.md`. Uses `uv` for env management (`uv sync`). Student model: `qwen3.5:4b`. The internal answer key + auto-grader live in `lab01/_solutions/` (reference solution notebooks + `_solutions/grading/`). |
| **materials/** | Course documents provided by the module lead (Modulbeschreibung, Lehreinheiten, Labor catalog). |
| **infra/** | Deployment runbook: `jupyterhub.md` — TLJH + nbgitpuller + cloudflared serving the lab notebooks to students on the Spark. |
| **literature/** | Curated Agentic AI literature review (sources, navigation table, German summaries). |
| **_superseded/** | Earlier exploratory phase, kept for reference, not part of the current lab. |
| `notizen.md` | Working notes and meeting minutes (German). |
| `README.md` | Top-level orientation (English). |

## Auto-Grading (`lab01/_solutions/grading/`)

Grades a submitted Lab 1 notebook against the solution key. Run from `lab01/` via `uv run python _solutions/grading/grade.py ...` so the `ollama` package from the uv env is available.
- **Exercise 0 (free-text answers)** — graded by a **judge LLM**, one question at a time, against `rubric.json`. Default judge model: `nemotron-3-super:latest` (override via `JUDGE_MODEL` env var). Students tag each answer with its rubric id (`P<part>.Q<n>:`); the grader extracts the text after each tag.
- **Exercise 1 (code TODOs)** — checked **deterministically** with anchored regexes on the `run_agent` code, no LLM.

Each answer is scored **1.0 / 0.5 / 0.0** (correct / partial / incorrect; missing = 0). `grade.py` writes a `<notebook>.grade.json` report per submission with per-question score + label and a total. Routing (code vs. free-text) is automatic based on notebook content. Files: `grade.py` (stdlib + `ollama` only), `rubric.json` (machine-readable rubric), `SOLUTION_KEY.md` (human-readable rubric), `README.md`.

## Superseded sub-projects

Under `_superseded/`, for reference only. Each was self-contained with its own venv/requirements:

| Sub-Project | What it demonstrated | Framework |
|---|---|---|
| `langchain_simple/` | Streaming LLM responses with/without "thinking" mode | LangChain |
| `langchain_react/` | ReAct agent with `create_react_agent`, tool use, interactive REPL | LangGraph |
| `langgraph_basics/` | Notebooks: hand-built ReAct `StateGraph` + multi-agent council debate | LangGraph |
| `ollama_react/` | ReAct agent with the raw Ollama SDK (no LangChain), manual tool-call loop | raw `ollama` |
| `ollama_react_planning/` | PAOR agent (Plan-Act-Observe-Reflect), four-phase reasoning cycle | raw `ollama` |
| `nemotron_voice/`, `voice_chat/` | Voice experiments | — |
| `run_benchmark.py`, `benchmark_*` | ReAct vs. PAOR comparison run + report | — |

## Setup & Running

The active lab uses **`uv`** (not manual venvs):

```bash
ollama pull qwen3.5:4b
cd lab01
uv sync                  # creates .venv/ and installs deps from pyproject.toml
uv run jupyter notebook
```

**Prerequisite:** Ollama running locally with the required models pulled. The grading judge
(`nemotron-3-super:latest`) and student model (`qwen3.5:4b`) must be available on the Spark
(`ollama list`).

## Conventions

- Lab notebook prose: **no em dashes** — use colons, commas, or sentence breaks instead.
- Lab audience are newcomers to LLM internals: define jargon, flag model-specific vs. universal behavior.
- `lab01/_solutions/` (solutions + grading) is internal answer-key material.
