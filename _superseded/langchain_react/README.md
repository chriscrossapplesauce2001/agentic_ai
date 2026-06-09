# langchain_react

ReAct agent built with LangGraph's `create_react_agent` and Ollama (`qwen3:0.6b`). Streams step-by-step reasoning (tool calls, results, final answer) to stdout.

## Tools

- **web_search** — DuckDuckGo search via `langchain-community`
- **calculator** — Safe math evaluation via `numexpr` (supports `pi`, `e`, trig, etc.)
- **read_file** — Reads local text files, sandboxed to the project directory

## Setup

Requires Ollama running locally with `qwen3:0.6b` pulled.

```bash
python -m venv .venv
source .venv/Scripts/activate  # Windows Git Bash
pip install -r requirements.txt
python main.py
```

A `.env` file configures LangSmith tracing (`LANGCHAIN_TRACING_V2`, `LANGCHAIN_API_KEY`, `LANGCHAIN_PROJECT`).

## Workflow

1. `main.py` loads `.env` and runs three demo queries (area moment of inertia calculations), then enters an interactive REPL
2. Each query is passed to the ReAct agent (`agent.py`), which reasons in a loop: decide tool → call tool → observe result → repeat or answer
3. The agent streams each step (tool call, tool result, final answer) to stdout

## Structure

| File | Purpose |
|------|---------|
| `tools.py` | Tool definitions (`@tool` decorator + DuckDuckGoSearchRun) |
| `agent.py` | Agent creation and streaming output logic |
| `main.py` | Entry point — runs demo queries then interactive REPL |
| `sample.txt` | Example data: area moment of inertia formulas |
