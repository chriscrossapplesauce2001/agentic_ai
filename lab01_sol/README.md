# Lab 1: ReAct Agents with Ollama

## LLM vs. Agent

**LLM**: Stateless API call. Messages in, message out.

**Agent**: Loop around an LLM. Calls the LLM, executes tool calls, feeds results back as new messages — repeats until the LLM no longer returns a tool call.

```
LLM:    messages → response
Agent:  messages → [LLM → Tool Call → Tool Result]* → response
```

## Learning Goals

- Understand and implement the ReAct pattern (Reason + Act)
- Build a tool-calling agent by hand with the Ollama SDK
- Build the same agent with LangChain/LangGraph

## Setup

### 1. Ollama + Model

```bash
# Install Ollama: https://ollama.com/
ollama pull qwen3.5:4b
ollama list   # qwen3.5:4b should appear
```

### 2. Install `uv` (one-time)

`uv` is a fast Python package manager that handles venv + dependencies in a single step.

```bash
# Linux / macOS:
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell):
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Details: https://docs.astral.sh/uv/getting-started/installation/

### 3. Create the Python environment

```bash
cd lab01
uv sync
```

That's it. `uv sync` reads `pyproject.toml`, creates `.venv/`, and installs all dependencies.

### 4. Register the Jupyter kernel

```bash
uv run python -m ipykernel install --user --name lab01 --display-name "lab01"
```

Then open the `.ipynb` files with:
- **VS Code / PyCharm**: open the file directly and select the **"lab01"** kernel (or point the interpreter at `lab01/.venv/bin/python`)
- **Browser**: `uv run jupyter notebook`

## Exercises

| Exercise | File | Description |
|----------|------|-------------|
| Getting to know Ollama | `exercise0/exercise0.ipynb` | Understand raw `ollama.chat()`: without tools, with history, with tools, manual tool roundtrip |
| ReAct agent by hand (Ollama SDK) | `exercise1/exercise1.ipynb` | Implement the ReAct loop as a `run_agent()` function (4 TODOs) |
| ReAct agent with LangChain | `exercise2/exercise2.ipynb` | Build the same agent with LangChain/LangGraph |

## Test

```bash
uv run pytest test_agent.py -v
```
