import sys
import re
from typing import TypedDict, Annotated
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

# --- Configuration ---
MODEL_NAME = "nemotron-3-super"
MAX_TURNS = 6  # 6 turns = 3 exchanges

ENGINEER_PROMPT = (
    "/no_think You ARE a pragmatic engineer and NOTHING else. "
    "You argue ONLY from data, measurements, and real-world engineering experience. "
    "NEVER use philosophical language like 'epistemology', 'axioms', 'coherence theory', or 'Hume'. "
    "Stick to numbers, experiments, and physical evidence. "
    "Directly rebut the other speaker's last point before making your own. "
    "Keep responses under 150 words."
)

PHILOSOPHER_PROMPT = (
    "/no_think You ARE a theoretical philosopher and NOTHING else. "
    "You argue ONLY from logic, ethics, and thought experiments. "
    "NEVER use engineering language like 'GPS', 'theodolite', 'surveying', or cite specific measurements. "
    "Challenge assumptions, question definitions, and propose counterexamples. "
    "Directly rebut the other speaker's last point before making your own. "
    "Keep responses under 150 words."
)

# --- ANSI colors ---
CYAN = "\033[96m"
YELLOW = "\033[93m"
BOLD = "\033[1m"
RESET = "\033[0m"
COLORS = {"Engineer": CYAN, "Philosopher": YELLOW}


# --- State ---
class DebateState(TypedDict):
    messages: Annotated[list, add_messages]
    turn: int
    next_speaker: str


# --- Agent node factory ---
def make_agent_node(name: str, system_prompt: str, model, other_name: str):
    def node(state: DebateState) -> dict:
        sys_msg = SystemMessage(content=system_prompt)
        response = model.invoke([sys_msg] + state["messages"])
        response.content = re.sub(r".*?</think>\s*", "", response.content, count=1, flags=re.DOTALL)
        response.name = name
        return {
            "messages": [response],
            "turn": state["turn"] + 1,
            "next_speaker": other_name,
        }
    return node


# --- Router ---
def router(state: DebateState) -> str:
    if state["turn"] >= MAX_TURNS:
        return END
    return state["next_speaker"]


# --- Build graph ---
def build_graph():
    engineer_model = ChatOllama(model=MODEL_NAME, temperature=0.3)
    philosopher_model = ChatOllama(model=MODEL_NAME, temperature=0.9)

    graph = StateGraph(DebateState)
    graph.add_node("Engineer", make_agent_node("Engineer", ENGINEER_PROMPT, engineer_model, "Philosopher"))
    graph.add_node("Philosopher", make_agent_node("Philosopher", PHILOSOPHER_PROMPT, philosopher_model, "Engineer"))

    graph.set_entry_point("Engineer")
    graph.add_conditional_edges("Engineer", router)
    graph.add_conditional_edges("Philosopher", router)

    return graph.compile()


# --- Main ---
def main():
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
        topic = input("Debate topic: ").strip()
        if not topic:
            print("No topic provided.")
            return

    print(f"\n{BOLD}Debate: \"{topic}\"{RESET}\n")

    app = build_graph()
    initial_state = {
        "messages": [HumanMessage(content=f"Debate topic: {topic}")],
        "turn": 0,
        "next_speaker": "Engineer",
    }

    turn = 0
    for event in app.stream(initial_state, stream_mode="updates"):
        for node_name, delta in event.items():
            if "messages" in delta:
                turn += 1
                msg = delta["messages"][-1]
                color = COLORS.get(node_name, "")
                print(f"{color}{'=' * 60}")
                print(f"{msg.name} (Turn {turn}):")
                print(f"{'=' * 60}{RESET}")
                print(msg.content)
                print()

    print(f"{BOLD}Debate ended after {turn} turns.{RESET}")


if __name__ == "__main__":
    main()
