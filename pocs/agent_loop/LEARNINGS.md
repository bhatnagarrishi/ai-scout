# LEARNINGS: Autonomous Agent Execution Loop

## 🛠️ Technical Insights

### 1. Robust Tool Parsing
*   **The Problem**: LLMs sometimes wrap tool calls in conversational text or markdown code blocks (e.g., ` ```json ... ``` `).
*   **The Learning**: A dedicated parser is required to strip formatting and handle partial JSON. In this POC, the `orchestrator.py` uses a combination of regex and JSON loading to ensure reliable extraction.

### 2. State Management & Token Limits
*   **The Problem**: Each turn in the loop appends the previous tool output to the history. Long-running tasks will eventually hit context window limits.
*   **The Learning**: For AI Scout, we must implement a "sliding window" or summary-based history management to keep the loop functioning over long sessions.

### 3. Termination Logic
*   **The Learning**: Strictly define what constitutes an "answer." In this POC, the model must explicitly provide a message with a specific structure to break out of the `while` loop, preventing expensive infinite loops.

### 4. Deterministic Tools vs. Probabilistic LLM
*   **The Learning**: Writing tools that return structured error messages (e.g., `{"error": "File not found"}`) allows the LLM to "self-correct." When the model fails to find a file, it uses its next turn to list the directory again, mimicking human troubleshooting.

## 🚀 Recommendation for AI Scout
The AI Scout "Worker" should use this recursive loop pattern but with **checkpointing**. If the loop runs for more than 5 iterations, it should pause and request human validation before continuing, ensuring the agent hasn't gone "down a rabbit hole."
