import os
import sys
import asyncio
import argparse
import json
import logging
from enum import Enum
from typing import List, Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel

# Suppress the noisy "Both GOOGLE_API_KEY and GEMINI_API_KEY are set" warning
# that Pydantic AI's Google provider prints to stderr unconditionally.
logging.getLogger("pydantic_ai").setLevel(logging.ERROR)
os.environ.setdefault("PYDANTIC_AI_LOG_LEVEL", "ERROR")

# 1. Setup Environment
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, '.env')
load_dotenv(env_path)

# Map GEMINI_API_KEY → GOOGLE_API_KEY (Pydantic AI's Google provider uses this name)
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    os.environ["GOOGLE_API_KEY"] = api_key

# Set the established stable model for this account's experimental access
model_name = 'gemini-2.5-flash'
model = GoogleModel(model_name)

# 2. Define the Pydantic Schema that matches our n8n contract exactly
class StatusEnum(str, Enum):
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"

class DifficultyEnum(str, Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"

class ScoutReport(BaseModel):
    """The strictly validated output from the AI Scout agent."""
    status: StatusEnum = Field(description="Whether the content is 'Accepted' or 'Rejected' based on our criteria.")
    reasoning: str = Field(description="1 sentence explaining exactly why this was accepted or rejected.")
    project_title: str = Field(description="The formal title of the project or tool.")
    objective: str = Field(description="1-2 sentences explaining exactly what is being built and why it matters.")
    source: str = Field(description="Who created this? e.g., OpenAI, Anthropic, HuggingFace, etc.")
    area: str = Field(description="The primary domain, e.g., Image Generation, Agentic AI, RAG, Core Coding.")
    tech_stack: str = Field(description="Core tools required, e.g., Python, FastAPI, LangChain.")
    prerequisites: str = Field(description="Minimum requirements, e.g., OpenAI API Key, Local GPU.")
    difficulty: DifficultyEnum = Field(description="Overall difficulty level.")
    estimated_time: str = Field(description="Rough estimate of time to build a POC, e.g., '2 hours'.")
    action_plan: List[str] = Field(description="Exactly 5 actionable, sequential steps to build the Proof of Concept.")
    github_repo_name: str = Field(description="A clean, slugified-title (kebab-case) for the repository.")

# 3. Initialize the Agent
agent = Agent(
    model=model,
    output_type=ScoutReport,
    system_prompt=(
        "You are an AI Master Instructor and Elite Scout. "
        "Filter Criteria: Evaluate if the content describes a new model, library, tool, or technique "
        "that can be tested/implemented in Python within 3 hours. "
        "REJECT news about funding, policy, AI hype, or general corporate announcements."
    )
)

async def run_scout(title: str, snippet: str) -> str:
    """Classifies an RSS item and returns the validated JSON string."""
    input_text = f"Title: {title}\nContent: {snippet}"
    try:
        result = await agent.run(input_text)
        # .output holds the validated Pydantic object
        data = result.output.model_dump()
        # Always include the original title so n8n can display it on rejection
        data["input_title"] = title
        return json.dumps(data, indent=2, ensure_ascii=False)
    except Exception as e:
        error_result = {
            "status": "Rejected",
            "reasoning": f"Classification error: {str(e)}",
            "input_title": title,
            "project_title": title,
            "objective": "N/A",
            "source": "N/A",
            "area": "N/A",
            "tech_stack": "N/A",
            "prerequisites": "N/A",
            "difficulty": "Beginner",
            "estimated_time": "N/A",
            "action_plan": [],
            "github_repo_name": "error"
        }
        return json.dumps(error_result, indent=2)

def main():
    parser = argparse.ArgumentParser(description="Pydantic AI Scout Agent for RSS classification.")
    parser.add_argument("--title", required=True, help="RSS Item Title")
    parser.add_argument("--snippet", required=True, help="RSS Item Content Snippet")
    parser.add_argument("--test", action="store_true", help="Run a quick internal test.")
    
    args = parser.parse_args()

    if args.test:
        test_title = "Pydantic AI: Agentic Framework"
        test_snippet = "A new library for building agentic AI with Pydantic validation. Highly efficient."
        asyncio.run(run_scout(test_title, test_snippet))
        print("Test cycle complete.")
        return

    # Print ONLY clean JSON to stdout — n8n reads this
    # Redirect stderr to devnull to silence any remaining library warnings
    with open(os.devnull, 'w') as devnull:
        old_stderr = sys.stderr
        sys.stderr = devnull
        output = asyncio.run(run_scout(args.title, args.snippet))
        sys.stderr = old_stderr
    print(output)

if __name__ == "__main__":
    main()
