import sys
from dotenv import load_dotenv
load_dotenv()

sys.stdout.reconfigure(encoding="utf-8")

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

# Create two model instances: one normal, one with thinking enabled
llm = ChatOllama(model="qwen3.5:4b", reasoning=False)
llm_think = ChatOllama(model="qwen3.5:4b", reasoning=True)


def stream_response(llm_instance, input_data):
    """Stream the response token by token, showing thinking and answer live."""
    in_thinking = False
    in_answer = False
    total_input_tokens = 0
    total_output_tokens = 0

    for chunk in llm_instance.stream(input_data):
        # Accumulate token counts from usage_metadata if present
        usage = getattr(chunk, "usage_metadata", None)
        if usage:
            total_input_tokens += usage.get("input_tokens", 0)
            total_output_tokens += usage.get("output_tokens", 0)

        # Check if this chunk contains thinking/reasoning content
        reasoning = chunk.additional_kwargs.get("reasoning_content")
        if reasoning:
            if not in_thinking:
                print("\n[Thinking]", flush=True)
                in_thinking = True
            print(reasoning, end="", flush=True)

        # Regular content = the final answer
        if chunk.content:
            if not in_answer:
                if in_thinking:
                    print()  # newline after thinking
                print("\n[Answer]", flush=True)
                in_answer = True
            print(chunk.content, end="", flush=True)

    print()  # final newline
    print(f"  Tokens — input: {total_input_tokens}, output (incl. thinking): {total_output_tokens}")


# 1) Normal mode — no thinking, streamed live
print("=" * 60)
print("=== Without Thinking (streamed) ===")
print("=" * 60)
stream_response(llm, "What is Python in one sentence?")

# 2) Thinking mode — see the reasoning process live
print("\n" + "=" * 60)
print("=== With Thinking Enabled (streamed) ===")
print("=" * 60)
stream_response(llm_think, "What is Python in one sentence?")

# 3) Thinking mode with a chain
print("\n" + "=" * 60)
print("=== Thinking with a Chain ===")
print("=" * 60)
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert in {topic}. Reason step by step."),
    ("human", "{question}"),
])
chain = prompt | llm_think
stream_response(chain, {"topic": "physics", "question": "Why is the sky blue?"})
