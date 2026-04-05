# POC Learnings: Pydantic AI & Gemini 2.5 Flash

## 🎭 The "Type Safety" Breakthrough
Integrating LLMs into production often breaks because of non-deterministic JSON. This POC proved that **Pydantic AI** is the current gold standard for solving this.

### 1. Schema-First Development
By defining a `BaseModel` using Pydantic, we shifted the complexity from "regex parsing" to "class definition." Gemini 2.5 Flash respected the schema perfectly in every trial.

### 2. The `GoogleModel` Adapter
- **Gotcha**: The environment variable expectation is `GOOGLE_API_KEY`. 
- **Learning**: Pydantic AI's internal logic for Google models prepends `models/` to the string you provide (e.g., `gemini-2.5-flash` becomes `models/gemini-2.5-flash`).

### 3. API Nuances (v0.0.18+)
- **`.output` vs `.data`**: Previous versions or documentation might suggest `result.data`, but the current idiomatic way to get the validated object is `result.output`.
- **`output_type`**: Setting this during `Agent` initialization is more stable than passing it during individual `run()` calls.

### 4. Tool Integration
- `@agent.tool_plain` is incredibly useful for utility functions that don't need access to the agent's internal state.
- The agent successfully "decided" to call the `fetch_community_sentiment` tool when it encountered a relevant keyword, demonstrating autonomous reasoning.

## 🚀 Recommendation for AI Scout
We should migrate the **entire** n8n "Projectize" logic from raw templates to a Pydantic AI script. This will allow us to use:
- **Validators**: e.g., Ensuring the `relevance_score` is always an integer.
- **Enums**: e.g., Forcing `difficulty` to be strictly one of `['Beginner', 'Intermediate', 'Advanced']`.
