import sys
sys.stdout.reconfigure(encoding="utf-8")

from agent import run_agent
from config import MODEL, DEMO_QUERIES


def main():
    print("=" * 60)
    print(f"  ollama_react_planning: PAOR Agent with {MODEL} (raw Ollama)")
    print("  Agent loop: Plan -> Act -> Observe -> Reflect")
    print("  Tools: web_search, calculator, read_file")
    print("  Type 'quit' or 'exit' to stop.")
    print("=" * 60)

    for query in DEMO_QUERIES:
        run_agent(query)

    # Interactive loop
    while True:
        try:
            user_input = input("\nYou: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("quit", "exit", "q"):
                print("Goodbye!")
                break
            run_agent(user_input)
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    main()
