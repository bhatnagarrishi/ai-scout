# AI Scout Repository Learnings

This document captures overarching, repository-wide architectural and technical learnings. For POC-specific learnings, refer to the `LEARNINGS.md` files localized within the `pocs/` subdirectories.

## OpenAI Configuration and Best Practices

### 1. Explicit Project IDs
When using organizational or specific project boundaries in OpenAI, you **must** supply the project ID.
- **Do not hardcode** the project ID inside Python scripts or application code.
- Store `OPENAI_PROJECT` in the `.env` file alongside `OPENAI_API_KEY`.
- When instantiating the native OpenAI client, fetch it securely:
  ```python
  from openai import OpenAI
  import os

  client = OpenAI(
      api_key=os.getenv("OPENAI_API_KEY"), 
      project=os.getenv("OPENAI_PROJECT")
  )
  ```
- When using LangChain's `ChatOpenAI`, inject it through `default_headers`:
  ```python
  from langchain_openai import ChatOpenAI
  import os

  llm = ChatOpenAI(
      model="gpt-4o", 
      openai_api_key=os.getenv("OPENAI_API_KEY"),
      default_headers={"OpenAI-Project": os.getenv("OPENAI_PROJECT")}
  )
  ```

### 2. API Deprecations (Assistants -> Responses)
The older OpenAI 'Assistants and Threads' APIs have been **deprecated** in favor of the new **Responses API**. 
When maintaining existing scripts (like the ones in `pocs/advanced-data-analysis`) or rolling out new agentic systems, ensure the integration points directly to the latest abstraction SDK endpoints natively avoiding deprecation warnings.

### 3. Environment Variable Security
All keys securely tied to an external service or cloud provider (OpenAI, Groq, local setups) should strictly be confined to `.env`. Code must map these using `os.getenv` or `python-dotenv`. Never check-in hardcoded literal strings.

---
*Append new overarching principles here as the repository evolves (e.g. state management, node coordination...)*
