# LangChain Simple — Streaming & Thinking Mode Demo

Demonstrates streaming LLM responses via LangChain with Ollama, comparing normal inference against "thinking" (reasoning) mode.

## Stack

- **LLM**: `qwen3.5:4b` running locally via [Ollama](https://ollama.com)
- **Framework**: LangChain (`ChatOllama`, `ChatPromptTemplate`)
- **Tracing**: LangSmith (configured via `.env`)

## What It Does

`main.py` runs three demos using the same prompt streamed token-by-token:

| # | Mode | Description |
|---|------|-------------|
| 1 | **Without thinking** | Direct answer — model responds immediately |
| 2 | **With thinking** | Model reasons internally first, then answers |
| 3 | **Thinking + Chain** | Thinking mode combined with a `ChatPromptTemplate` chain |

## Thinking Mode — How It Works

### Turning It On/Off

Reasoning is controlled by a single parameter on `ChatOllama`:

```python
llm       = ChatOllama(model="qwen3.5:4b", reasoning=False)  # thinking OFF
llm_think = ChatOllama(model="qwen3.5:4b", reasoning=True)   # thinking ON
```

Under the hood, `reasoning=True` causes LangChain to set `think=True` in the Ollama API request. This instructs the model to use its chain-of-thought capability.

### The Full Call Chain

Here's what happens end-to-end when you set `reasoning=True`:

#### 1. LangChain translates the parameter
`ChatOllama` maps `reasoning=True` to `think=True` in the JSON payload sent to Ollama's `POST /api/chat` endpoint. (See `langchain_ollama/chat_models.py:770`.)

#### 2. Ollama applies the model's chat template
This is where the magic happens. Qwen3.5 ships with a **Jinja2 chat template** that checks an `enable_thinking` flag:

```jinja
{%- if enable_thinking is defined and enable_thinking is false %}
    {{- '<think>\n\n</think>\n\n' }}
{%- endif %}
```

- **`think=true`**: The template lets the model freely generate `<think>...</think>` blocks before answering.
- **`think=false`**: The template injects an **empty** `<think>\n\n</think>` block, signaling the model to skip reasoning and answer directly.

#### 3. The model generates two token streams
Qwen3.5 is a **single unified model** — there is no separate "thinking model". During post-training (SFT + reinforcement learning), the model was trained on both thinking and non-thinking examples. It learned to:

1. Generate reasoning inside `<think>...</think>` tags (these are regular tokens in the vocabulary, e.g. token ID 151668 for `</think>`)
2. Generate the final answer after `</think>`

It is **not** a system prompt or a separate architecture. It's a **chat template mechanism** — the template either allows or suppresses the `<think>` tokens, and the model was fine-tuned to understand these markers as "reason here" vs "answer directly".

#### 4. Ollama splits the output
Ollama parses the raw generation and separates it into two fields:
- Text between `<think>` and `</think>` → `message.thinking`
- Everything after `</think>` → `message.content`

#### 5. LangChain surfaces both streams
```python
# langchain_ollama/chat_models.py:1088
if (thinking_content := stream_resp["message"].get("thinking")):
    additional_kwargs["reasoning_content"] = thinking_content
```

The `stream_response()` function in `main.py` then reads `chunk.additional_kwargs["reasoning_content"]` for the `[Thinking]` output and `chunk.content` for the `[Answer]`.

### Without vs With Thinking

**Without thinking** (`reasoning=False`):
The chat template injects an empty `<think></think>` block. The model recognizes this as a "don't think" signal and generates the final answer directly in a single pass.

**With thinking** (`reasoning=True`):
The model produces two distinct token streams. **Reasoning tokens** come first — the model "thinks out loud", breaking the problem into steps and self-correcting. Then **answer tokens** follow, informed by everything worked out during thinking. The reasoning tokens consume output tokens (and thus time/compute) but are not part of the final answer.

### Why It Matters

Thinking mode trades speed for quality. The internal reasoning step lets the model:
- Decompose complex questions before answering
- Self-correct mistakes mid-generation
- Produce more accurate, structured responses

For simple factual questions the difference is minimal. For multi-step reasoning, math, or nuanced explanations, thinking mode significantly improves output quality.

## Setup

```bash
# Requires Ollama running locally with the model pulled
ollama pull qwen3.5:4b

# Install dependencies and run
python -m venv .venv
source .venv/Scripts/activate   # Windows Git Bash
pip install -r requirements.txt
python main.py
```
