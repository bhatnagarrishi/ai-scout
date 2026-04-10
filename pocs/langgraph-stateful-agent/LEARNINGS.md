# Key Learnings: The Bedrock-to-LangGraph Pivot

This POC provided two sets of learnings: why managed cloud agents can be difficult, and why graph-based state management is a powerful alternative.

### 1. The Bedrock Friction (The "Pivot" Story)
While Amazon Bedrock's "Stateful Runtime" sounds promising (managed memory, no history handling code), it carries significant **Cloud Overhead**:
- **Entitlement Blocks**: Even with `AdministratorAccess`, third-party models (Anthropic, Meta) or newer first-party models (Nova) often fail with `Operation not allowed` until specific "Marketplace" or "Model Access" hurdles are cleared.
- **Black Box State**: You cannot easily "see" or "edit" the history stored in Bedrock's managed session without calling specific APIs.
- **Regional Latency**: Newer models are often limited to specific regions (like `us-west-2`), causing friction for existing `us-east-1` setups.

### 2. LangGraph: Explicit State control
Pivoting to LangGraph revealed several advantages for the **AI Scout** pipeline:
- **`SqliteSaver` is Transparent**: The state is stored in a local `.db` file. We can open this file with any SQLite browser and literally see the agent's memory.
- **`add_messages` Reducer**: LangGraph uses "reducers" to handle state updates. The `Annotated[list, add_messages]` pattern is a genius way to manage conversation history without manually appending lists.
- **Threads are Configuration, not URLs**: In Bedrock, a session is a URL/Context. In LangGraph, it's just a key in a dictionary (`thread_id`). This makes it trivial to swap between "User A" and "User B" in the same script.

### 3. Model Agnosticism
By using LangChain's abstraction, we were able to switch from Bedrock's `InvokeAgent` logic back to **Google Gemini** in minutes. This resilience is critical for an automated scout that needs to be reliable regardless of cloud provider outages or permission shifts.

### 4. Persistence vs. Memory
We learned the difference between **Short-term Memory** (in-memory lists) and **Persistence** (saved checkpoints). LangGraph's checkpointer mechanism ensures that if the script crashes, the agent can resume exactly where it left off by just using the same `thread_id`.
