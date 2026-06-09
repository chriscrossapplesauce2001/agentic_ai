from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import create_agent
from langgraph_swarm import create_handoff_tool, create_swarm

model = ChatOllama(model="nemotron-3-super")

def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

alice = create_agent(
    model,
    tools=[
        add,
        create_handoff_tool(
            agent_name="Bob",
            description="Transfer to Bob",
        ),
    ],
    system_prompt="You are Alice, an addition expert.",
    name="Alice",
)

bob = create_agent(
    model,
    tools=[
        create_handoff_tool(
            agent_name="Alice",
            description="Transfer to Alice, she can help with math",
        ),
    ],
    system_prompt="You are Bob, you speak like a pirate.",
    name="Bob",
)

checkpointer = InMemorySaver()
workflow = create_swarm(
    [alice, bob],
    default_active_agent="Alice"
)
app = workflow.compile(checkpointer=checkpointer)

config = {"configurable": {"thread_id": "1"}}

print("Swarm chat (Alice & Bob). Type 'quit' to exit.\n")
msg_count = 0
while True:
    user_input = input("YOU: ").strip()
    if not user_input or user_input.lower() == "quit":
        break
    result = app.invoke(
        {"messages": [{"role": "user", "content": user_input}]},
        config,
    )
    new_msgs = result["messages"][msg_count:]
    for msg in new_msgs:
        if msg.type == "ai" and msg.content:
            print(f"{msg.name}: {msg.content}")
    msg_count = len(result["messages"])
    print()
