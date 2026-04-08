# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a collection of Python projects exploring agentic AI concepts using LangChain, LangGraph, and Ollama. The repository serves an academic/research purpose — preparing lecture material on agentic AI (German-language context, engineering domain examples). Each sub-project is self-contained with its own venv, requirements, and configuration. The projects are ordered by increasing complexity to build understanding incrementally.

## Sub-Projects

| Sub-Project | What It Demonstrates | Framework | Model |
|---|---|---|---|
| **langchain_simple/** | Streaming LLM responses with/without "thinking" mode (`ChatOllama`, `ChatPromptTemplate`) | LangChain | `qwen3.5:4b` |
| **langchain_react/** | ReAct agent with `create_react_agent`, tool use (web search, calculator, file reader), interactive REPL | LangGraph | `qwen3.5:0.8b` |
| **langgraph_basics/** | Two Jupyter notebooks: (1) `tutorial.ipynb` — hand-built ReAct agent with `StateGraph`, exposing state, nodes, conditional edges; (2) `council.ipynb` — multi-agent council debate | LangGraph | `qwen3.5:0.8b` |
| **ollama_react/** | ReAct agent built with raw Ollama Python SDK (no LangChain). Manual tool-call loop with streaming thinking/answer output | raw `ollama` SDK | `qwen3.5:4b` |
| **ollama_react_planning/** | PAOR agent (Plan-Act-Observe-Reflect). Extends ReAct with an explicit four-phase reasoning cycle. Transient prompts, step tracking, safety guards | raw `ollama` SDK | `qwen3.5:4b` |

## Top-Level Files

| File | Purpose |
|---|---|
| `run_benchmark.py` | Runs the same complex query through both ollama_react (ReAct) and ollama_react_planning (PAOR) agents, saves outputs |
| `benchmark_report.md` | Detailed comparison of ReAct vs PAOR results with scorecard and analysis |
| `benchmark_react_output.txt` | Raw ReAct agent output from benchmark run |
| `benchmark_paor_output.txt` | Raw PAOR agent output from benchmark run |
| `Agentic_AI_Literatur_Feb2026.md` | Curated literature review — 8 core sources + 31 total sources with summaries (German) |
| `Agentic_AI_Literature_Table.md` | Full 31-source navigation table with categories, keywords, and relevance ratings |
| `Quellen_7_Agentic_AI.md` | Meeting protocol template for discussing the 7 core sources with summaries (German) |
| `notizen.txt` | Working notes and meeting minutes |

## Setup & Running

Each sub-project uses its own virtual environment. From within a sub-project directory:

```bash
python -m venv .venv
source .venv/Scripts/activate   # Windows Git Bash
pip install -r requirements.txt
python main.py
```

**Prerequisite:** Ollama must be running locally with the required models pulled:
- `ollama pull qwen3.5:0.8b` (used by langchain_react, langgraph_basics)
- `ollama pull qwen3.5:4b` (used by langchain_simple, ollama_react, ollama_react_planning)

**Configuration:**
- **langchain_simple/** and **langchain_react/** use `.env` files with LangSmith tracing config (`LANGCHAIN_TRACING_V2`, `LANGCHAIN_API_KEY`, `LANGCHAIN_PROJECT`), loaded via `python-dotenv`.
- **ollama_react/** and **ollama_react_planning/** use `config.yaml` (model name, context window, temperature, system prompt, demo queries) loaded via `config.py` + PyYAML. No `.env` needed.

**Running the benchmark:**
```bash
python run_benchmark.py
```
This runs both agents with the same multi-step engineering query (moment of inertia calculations + web search) and saves outputs for comparison.

## Architecture Notes

- **LLM backend**: All projects use Ollama running locally — no cloud API keys needed for inference.
- **langchain_react** follows a modular pattern: `tools.py` defines LangChain `@tool`-decorated functions, `agent.py` creates the ReAct agent and streaming logic, `main.py` is the entry point with demo queries and interactive loop.
- **langgraph_basics** contains two notebooks: `tutorial.ipynb` builds a single-agent ReAct loop from scratch, then extends it to a multi-agent supervisor pattern with specialized workers. `council.ipynb` implements a multi-agent council debate.
- **ollama_react** and **ollama_react_planning** share a similar modular layout (`tools.py`, `agent.py`, `config.py`, `main.py`) but use the raw `ollama` Python SDK with manual JSON tool schemas instead of LangChain.
- The PAOR agent in **ollama_react_planning** uses transient prompts (not stored in message history) to orchestrate the four phases, keeping the context window clean. Key mechanisms: step tracking with `[done]/[pending]` checklists, safety guard against premature "FINAL ANSWER", `/no_think` optimization for ACT/REFLECT phases.
- Tool definitions in the ollama_react projects use plain functions with a `tool_map` dict for dispatch. The `read_file` tool restricts access to the project directory for safety.

## Key Dependencies

- **langchain_simple/langchain_react/langgraph_basics**: `langchain`, `langchain-ollama`, `langchain-community`, `langgraph`, `python-dotenv`, `jupyter`
- **ollama_react/ollama_react_planning**: `ollama`, `pyyaml`
- **Shared across tool-using projects**: `numexpr` (safe math evaluation), `ddgs` (DuckDuckGo search)
