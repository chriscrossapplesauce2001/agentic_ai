import json
import ollama
from tools import tool_map, web_search, calculator, read_file
from config import MODEL, NUM_CTX, TEMPERATURE, MAX_ITERATIONS, SYSTEM_PROMPT

# Ollama tool definitions — manual schemas matching the Python functions
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for current information. Returns snippets with source URLs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query string",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": (
                "Calculate a math expression. Input must be a valid math expression "
                "like '2 + 2' or '(3.14 * 0.2 * 0.4**3) / 12'. "
                "Supports +, -, *, /, **, sqrt, sin, cos, log, pi, e."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "The math expression to evaluate",
                    }
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": (
                "Read a local text file. Only files in the project directory can be read."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "The filename to read, e.g. 'sample.txt'",
                    }
                },
                "required": ["filename"],
            },
        },
    },
]


def stream_ollama_response(model, messages, tools=None):
    """Stream an ollama.chat response, printing [Thinking] and [Answer] live.

    Returns (full_thinking, full_content, tool_calls_list) for history.
    When tools=None, Ollama streams true token-by-token output.
    When tools are passed, streaming is blocked (Ollama #463) and arrives as a burst.
    """
    kwargs = dict(model=model, messages=messages, stream=True, think=True,
                  options={"num_ctx": NUM_CTX, "temperature": TEMPERATURE})
    if tools:
        kwargs["tools"] = tools

    full_thinking = ""
    full_content = ""
    tool_calls = []
    in_thinking = False
    in_answer = False

    for chunk in ollama.chat(**kwargs):
        msg = chunk.get("message", {})

        thinking = msg.get("thinking", "")
        if thinking:
            if not in_thinking:
                print("\n  [Thinking]", flush=True)
                in_thinking = True
            print(thinking, end="", flush=True)
            full_thinking += thinking

        content = msg.get("content", "")
        if content:
            if not in_answer:
                if in_thinking:
                    print()  # newline after thinking
                print("\n  [Answer]", flush=True)
                in_answer = True
            print(content, end="", flush=True)
            full_content += content

        tc = msg.get("tool_calls")
        if tc:
            tool_calls.extend(tc)

    if in_thinking or in_answer:
        print()  # final newline

    return full_thinking, full_content, tool_calls


def run_agent(user_input: str):
    """Run the ReAct agent loop with live streaming output."""
    print(f"\n{'='*60}")
    print(f"  QUESTION: {user_input}")
    print(f"{'='*60}")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_input},
    ]

    step_count = 0
    for _ in range(MAX_ITERATIONS):
        # Check for tool calls (non-streaming, since Ollama #463 blocks
        # streaming when tools= is passed anyway)
        response = ollama.chat(model=MODEL, messages=messages, tools=TOOLS, think=True,
                              options={"num_ctx": NUM_CTX, "temperature": TEMPERATURE})
        msg = response["message"]

        if msg.get("tool_calls"):
            # Show real model thinking from this step
            thinking = msg.get("thinking", "")
            if thinking:
                print(f"\n  [Thinking]\n  {thinking}")

            # Append assistant message (with tool_calls) to history
            messages.append(msg)

            for tc in msg["tool_calls"]:
                name = tc["function"]["name"]
                args = tc["function"]["arguments"]
                print(f"\n  [Tool Call] {name}({json.dumps(args)})")

                func = tool_map.get(name)
                if func is None:
                    result = f"Error: Unknown tool '{name}'"
                else:
                    try:
                        result = func(**args)
                    except Exception as exc:
                        result = f"Error calling '{name}': {exc}"

                if len(result) > 500:
                    print(f"  [Tool Result] {result[:500]}... (truncated)")
                else:
                    print(f"  [Tool Result] {result}")

                messages.append({"role": "tool", "content": result})
                step_count += 1
        else:
            # Final answer — stream without tools for true token-by-token output
            stream_ollama_response(MODEL, messages, tools=None)
            step_count += 1
            break

    print(f"\n  ({step_count} step(s))")
    print(f"{'='*60}\n")
