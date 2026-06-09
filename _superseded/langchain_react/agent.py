from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from tools import tools

# LLM configured for tool calling (no reasoning mode — conflicts with tool-call JSON)
llm = ChatOllama(
    model="llama3.3:70b",
    temperature=0,
    num_predict=1024,
)

SYSTEM_PROMPT = """You are a helpful engineering assistant with access to tools.

Available tools:
- web_search: Search the internet for information
- calculator: Calculate math expressions (e.g. '(0.2 * 0.4**3) / 12')
- read_file: Read a local text file (e.g. 'sample.txt')

Instructions:
1. For math or engineering calculations, use calculator with a math expression.
2. For factual questions, use web_search.
3. For reading files, use read_file with the filename.
4. Always provide a clear final answer."""

# Create the ReAct agent
agent = create_react_agent(
    model=llm,
    tools=tools,
    prompt=SYSTEM_PROMPT,
)


def run_agent_streaming(user_input: str):
    """Run the agent and stream each step to stdout."""
    print(f"\n{'='*60}")
    print(f"  QUESTION: {user_input}")
    print(f"{'='*60}")

    inputs = {"messages": [{"role": "user", "content": user_input}]}

    step_count = 0
    for chunk in agent.stream(inputs, stream_mode="updates"):
        for node_name, node_output in chunk.items():
            step_count += 1
            messages = node_output.get("messages", [])
            for msg in messages:
                # Agent decides to use a tool
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    for tc in msg.tool_calls:
                        print(f"\n  THINKING: I need to use '{tc['name']}' "
                              f"with input: {tc['args']}")

                # Tool returns its result
                elif hasattr(msg, "type") and msg.type == "tool":
                    content = msg.content
                    if len(content) > 500:
                        content = content[:500] + "... (truncated)"
                    print(f"  RESULT:   {content}")

                # Agent gives its final answer
                elif hasattr(msg, "content") and msg.content:
                    if not (hasattr(msg, "tool_calls") and msg.tool_calls):
                        print(f"\n  ANSWER:   {msg.content}")

    print(f"\n  ({step_count} step(s))")
    print(f"{'='*60}\n")
