import sys
from dotenv import load_dotenv
load_dotenv()

sys.stdout.reconfigure(encoding="utf-8")

from agent import run_agent_streaming


def main():
    print("=" * 60)
    print("  langX_rev02: ReAct Agent with qwen3.5:0.8b")
    print("  Tools: web_search, calculator, read_file")
    print("  Type 'quit' or 'exit' to stop.")
    print("=" * 60)

    # Demo queries — area moment of inertia calculations + web search
    demo_queries = [
        "Read the file sample.txt and tell me what formulas are listed.",
        "Calculate the area moment of inertia of a rectangle with width 0.2 m and height 0.4 m using the formula (0.2 * 0.4**3) / 12",
        "Calculate the area moment of inertia of a circle with diameter 0.3 m using (pi * 0.3**4) / 64",
        "Search the web for the Young's modulus of structural steel S235 in GPa.",
    ]

    for query in demo_queries:
        run_agent_streaming(query)

    # Interactive loop
    while True:
        try:
            user_input = input("\nYou: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("quit", "exit", "q"):
                print("Goodbye!")
                break
            run_agent_streaming(user_input)
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    main()
