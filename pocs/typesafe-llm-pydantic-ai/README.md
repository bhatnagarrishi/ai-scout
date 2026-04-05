# POC: Typesafe LLM with Pydantic AI

This POC demonstrates how to use the `pydantic-ai` framework to enforce strict, validated structured output (JSON Schema) from Google Gemini.

## 🚀 Overview
Ensuring that an LLM returns data in a predictable format is critical for building reliable agentic workflows. This POC uses **Pydantic AI** (v0.0.18+) to:
1. **Schema Enforcement**: Define a strict Python schema (`BaseModel`) that Gemini MUST follow.
2. **Auto-Validation**: Automatically transform LLM text into a validated Python object with zero manual parsing.
3. **Agentic Tools**: Demonstrates how an agent can call local tools (`@agent.tool_plain`) to augment its knowledge before generating a report.
4. **Gemini 2.0/2.5 Support**: Confirms compatibility with the latest experimental Google models via the `GoogleModel` adapter.

## 🛠️ Tech Stack
- **Framework**: [Pydantic AI](https://pydantic_ai.dev/)
- **Model**: `gemini-2.5-flash` (experimental)
- **Runtime**: Python 3.10+
- **Environment**: Managed via `.env` in the root directory

## 🏃 How to Run
1. Ensure your root `.env` file has a valid `GEMINI_API_KEY`.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the agent:
   ```bash
   python agent.py
   ```

## 📝 Actual Output (Validated)
When running `agent.py`, the agent converts unstructured text into this structured object:

```python
[Structured Output Data Validated by Pydantic]
Project Name: Pydantic AI
Relevance Score: 95/100
Is MCP Related: False
Features:
  - Type safety
  - Schema enforcement
  - Agentic decorators
Recommendation: Highly recommended for future LLM integrations requiring strict reliability.
```

## 🧠 Key Learnings
- **The `.output` Attribute**: In Pydantic AI, the validated model instance is accessed via `result.output`, not `result.data`.
- **Model Aliasing**: The `GoogleModel` adapter handles the `models/` prefix automatically.
- **Environment Parity**: Pydantic AI's Google adapter looks for `GOOGLE_API_KEY`, so mapping `GEMINI_API_KEY` in the script is necessary for repo-wide consistency.
- **Tool Logic**: Use `@agent.tool` for tools that need agent context and `@agent.tool_plain` for standalone utility functions.
