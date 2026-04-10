# POC: Long-Term Memory & Multi-Turn Persistence

> **Mission**: Prove that an AI Agent can maintain a continuous "thread" of memory across multiple interactions, even if the script is terminated and restarted.

---

## 🎯 The Goal: Multi-Turn Persistence
In most AI workflows, the "memory" vanishes the moment the script stops. This POC tests **LangGraph's Persistence Engine**, which offloads the conversation state to a local SQLite database.

We are testing two things:
1. **Context Retention**: Does it remember my name from 3 messages ago?
2. **Session Survival**: If I quit the script and come back 5 minutes later, is that memory still there?

## 🧪 The Demonstration (Try This)
To see the POC in action, follow this specific test routine:

1. **Establish Context**: Run the script and tell it something personal:
   - *User: "Hi, I'm Rishi. I love Python workflows."*
2. **The "Memory Gap"**: Exit the script completely (`exit`).
3. **The Proof**: Restart the script. Without re-introducing yourself, ask:
   - *User: "What's my name and what do I like?"*
4. **Verification**: If the agent responds with "Rishi" and "Python," the POC is successful. It successfully recovered the state from `checkpoints.db`.

## 🛠️ How it Works
- **Orchestrator**: LangGraph (manages the conversation as a state machine).
- **Storage**: SQLite (`checkpoints.db`). Every time the agent speaks, its "Brain State" is snapshotted to this file.
- **Model**: Gemini 3.1 Flash Lite (Configured centrally).

## 🏃 Setup
1. Ensure your root `.env` has a `GEMINI_API_KEY`.
2. Install dependencies: `pip install -r requirements.txt`.
3. Run the interactive agent: `python agent.py`.

## 🧠 Why this matters for AI Scout
A robust AI Scout needs a "Smart Memory." When it's scanning 100 RSS feeds, it needs to remember what it flagged yesterday or what specifically you told it to ignore in a previous session. This POC proves we can build that "Local Brain" without relying on expensive or restrictive cloud-managed agent runtimes.
