import os
import asyncio
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel

import sys
from pydantic_ai.models.test import TestModel

# 1. API Key Mapping
# Explicitly find and load the .env from the project root
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(current_dir))
env_path = os.path.join(root_dir, '.env')

print(f"--- DEBUG: Loading environment from: {env_path} ---")
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    print(f"--- WARNING: .env file NOT FOUND at {env_path} ---")

api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    # Print masked key for verification without leaking it in logs
    masked_key = f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) > 8 else "***"
    print(f"--- DEBUG: Detected GEMINI_API_KEY: {masked_key} (Length: {len(api_key)}) ---")
else:
    print("--- DEBUG: GEMINI_API_KEY is currently None ---")

# Set the model name. Pydantic AI's GoogleModel prepends 'models/' internally.
# Your API key has access to the experimental 'gemini-2.5-flash' model.
model_to_use = GoogleModel('gemini-2.5-flash')

if not api_key or api_key == "your_gemini_api_key_here":
    print("\n--- WARNING: No valid GEMINI_API_KEY found in .env ---")
    print("Falling back to Pydantic AI 'TestModel' (Mock Run) for verification.")
    # Initialize a mock model
    model_to_use = TestModel()
    os.environ["GOOGLE_API_KEY"] = "mock_key"
else:
    # Inject the key for Pydantic AI's provider
    os.environ["GOOGLE_API_KEY"] = api_key
    # As requested: Print the actual key (masked for safety but verifiable)
    print(f"--- DEBUG: Final GOOGLE_API_KEY in environment: {os.environ['GOOGLE_API_KEY'][:6]}...{os.environ['GOOGLE_API_KEY'][-4:]} ---")

# 1. Define the Expected Output Schema using Pydantic
class ScoutReport(BaseModel):
    """Structured report returned by the Scout analysis agent."""
    project_name: str = Field(description="The name of the project or technology being analyzed.")
    relevance_score: int = Field(ge=0, le=100, description="A score from 0 to 100 indicating how relevant this project is to Agentic AI and Developer Tools.")
    is_mcp_related: bool = Field(description="True if the project involves the Model Context Protocol (MCP).")
    key_features: list[str] = Field(description="A brief bulleted list of 2-3 core features of the project.")
    strategic_recommendation: str = Field(description="A 1-sentence recommendation on whether to adopt or research this tool further.")

# 2. Initialize the Pydantic AI Agent
# We enforce `output_type=ScoutReport` to guarantee structured validation.
agent = Agent(
    model=model_to_use,
    output_type=ScoutReport,
    system_prompt=(
        "You are an elite AI Scout. Your job is to analyze descriptions of software tools and open-source projects. "
        "You always extract the core capabilities and score the project's relevance to our team's mission. "
        "Our team focuses on Agentic AI, local tooling, and Model Context Protocol (MCP) integrations."
    )
)

# 3. Define a mock external tool that the Agent can call before generating the report
@agent.tool_plain
def fetch_community_sentiment(project_name: str) -> str:
    """Mock API tool that retrieves the current community sentiment for a given project."""
    print(f"\n[TOOL CALLED] Fetching sentiment for {project_name}...")
    if "pydantic" in project_name.lower():
        return "Sentiment: EXTREMELY POSITIVE. Developers love the enforced type safety and performance."
    return "Sentiment: NEUTRAL. Needs more data."

async def main():
    # 4. Provide messy/unstructured input text to the Agent
    unstructured_text = (
        "I just found this new framework called Pydantic AI. It's built by the Pydantic team. "
        "It acts as a lightweight agent framework that forces Gemini to return perfectly validated python classes. "
        "It doesn't seem to natively implement the MCP spec out of the box, but you can build tools with it "
        "easily using standard decorators."
    )
    
    print("\n--- Starting Pydantic AI Agent Analysis ---")
    print("Input Text:", unstructured_text)
    
    # 5. Execute the Agent
    # The agent will parse the text, optionally format/call tools, and return a validated ScoutReport.
    if isinstance(model_to_use, TestModel):
        # Mock result for TestModel demonstration
        data = ScoutReport(
            project_name="Pydantic AI (Mock Mode)",
            relevance_score=95,
            is_mcp_related=False,
            key_features=["Type safety", "Schema enforcement", "Tool integration"],
            strategic_recommendation="Use for all mission-critical AI-driven classification tasks."
        )
        print("\n--- [MOCK] Analysis Complete ---")
    else:
        # Live run against Gemini
        result = await agent.run(unstructured_text)
        print("\n--- Analysis Complete (Live Gemini) ---")
        # Modern Pydantic AI API uses .output for validated data
        data = result.output
    
    # 6. We can access the structured fields directly as Python attributes
    print("\n[Structured Output Data Validated by Pydantic]")
    print(f"Project Name: {data.project_name}")
    print(f"Relevance Score: {data.relevance_score}/100")
    print(f"Is MCP Related: {data.is_mcp_related}")
    print("Features:")
    for feature in data.key_features:
        print(f"  - {feature}")
    print(f"Recommendation: {data.strategic_recommendation}")

if __name__ == "__main__":
    asyncio.run(main())
