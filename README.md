# Agentic AI — Lab Material

Teaching material for the **Agentic AI** module: Jupyter-based labs in which students
implement agentic AI concepts (ReAct, tool use, function calling, MCP) themselves, step by
step. The LLM backend is a locally running **Ollama** on the DGX Spark, so no cloud API keys
are needed for inference.

## 👉 Students start here: [`lab01/`](lab01/)

Everything you need is in **`lab01/`**. Open [`lab01/README.md`](lab01/README.md) and work
through the four notebooks in order (`exercise0` → `exercise3`).

```bash
ollama pull qwen3.5:4b      # the model the notebooks use
cd lab01
uv sync                     # creates .venv/ and installs dependencies
uv run jupyter notebook     # open the notebooks
```

## Repository layout

| Folder | For whom | Contents |
|---|---|---|
| [`lab01/`](lab01/) | **students** | The lab: notebooks `exercise0`–`exercise3` + setup. **This is the only folder students touch.** |
| `lab01/_solutions/` | instructors | Internal answer key, auto-grader, and a grading demo (see below). |
| [`instructor/`](instructor/) | instructors | Everything not student-facing: course `materials/`, deployment `infra/`, and the `literature/` review. |
| `_superseded/` | nobody | Earlier exploratory phase (standalone LangChain / LangGraph / Ollama / voice experiments, benchmarks). Kept for reference only. |
| `notizen.md` | maintainer | Working notes and meeting minutes (German). |

## Solutions & grading (internal)

`lab01/_solutions/` holds the reference solutions and the auto-grading system
(`lab01/_solutions/grading/`). The grader checks submitted notebooks against a solution key:
free-text answers are scored by a local judge LLM, code TODOs deterministically via regex. A
worked end-to-end example lives in `lab01/_solutions/grading/demo/`. Details in
[`lab01/_solutions/grading/README.md`](lab01/_solutions/grading/README.md).

> **Note:** this material is internal. While the repo is public and nbgitpuller clones the
> whole repo to students, `_solutions/` is reachable by them; serve a student branch without
> it (or keep it private) before the lab goes live.
