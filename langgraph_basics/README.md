# LangGraph Multi-Agent Demos

Minimal multi-agent demos using LangGraph and Ollama.

## Setup

```bash
source .venv/bin/activate
pip install -r requirements.txt
ollama pull nemotron-3-super
```

## Demos

### 1. Swarm Tutorial (`swarm_tutorial.py`)

Two agents (**Alice** and **Bob**) collaborate via handoff tools. Alice can add numbers and hand off to Bob. Bob speaks like a pirate and can hand off to Alice for math. Runs two scripted turns to demonstrate autonomous agent-to-agent handoff.

```bash
python swarm_tutorial.py
```

### 2. Swarm Chat (`swarm_chat.py`)

Interactive version of the swarm tutorial. You chat with Alice and Bob in a loop — agents decide autonomously when to hand off to each other.

```bash
python swarm_chat.py
```

Type messages to chat, `quit` to exit.

### 3. A2A Debate (`a2a_debate.py`)

Two agents (**Engineer** and **Philosopher**) debate a topic autonomously — no human input after the initial topic. Uses a LangGraph `StateGraph` with alternating turns. The Engineer (temperature 0.3) argues from data and measurements; the Philosopher (temperature 0.9) argues from logic and thought experiments.

```bash
python a2a_debate.py "Should AI replace human engineers?"
```

Or without an argument to get prompted for a topic:

```bash
python a2a_debate.py
```

Runs 6 turns (3 exchanges) by default.
