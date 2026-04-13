# LEARNINGS: Reasoning Chain Monitor

## 🛠️ Technical Insights

### 1. Deterministic Auditing is Mandatory
*   **The Problem**: If one LLM monitors another, you get "Hallucination inception." The monitor might hallucinate that the strategist is doing a good job.
*   **The Learning**: The auditor should be as deterministic as possible. In this POC, the `monitor.py` uses keyword matching and rule-based logic against JSON data, which is 100% reliable compared to a secondary LLM check.

### 2. Regex for Thought Extraction
*   **The Learning**: Enforcing a structure like `Thought: [reasoning] \n Final Strategy: [output]` in the system prompt allows for clean separation. This simple regex approach is more robust than trying to parse a single block of mixed text.

### 3. Segregation of Data
*   **The Learning**: Keep the "Ground Truth" research files in a separate directory (`research/`). This ensures that the Auditor always has a single source of truth to check against, regardless of what the LLM claims to "know."

## 🚀 Recommendation for AI Scout
We should implement a "Thought Auditor" in the main Scout pipeline. For example, before an issue is created, a deterministic monitor should check the agent's internal reasoning to ensure it hasn't missed any core requirements from the user's `config.json`.
