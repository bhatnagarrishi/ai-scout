import os
import sys
import asyncio
import argparse
import json
import logging
import yaml
from datetime import datetime
from enum import Enum
from typing import List, Optional
from dotenv import load_dotenv

# 1. Setup Environment & Suppress Warnings IMMEDIATELY
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, '.env')
load_dotenv(env_path)

# Map GEMINI_API_KEY → GOOGLE_API_KEY
# Then UNSET GEMINI_API_KEY so the library doesn't see both and complain
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    os.environ["GOOGLE_API_KEY"] = api_key
    # This is the secret sauce: delete the extra key so the warning never triggers
    if "GEMINI_API_KEY" in os.environ:
        del os.environ["GEMINI_API_KEY"]

# Suppress the noisy "Both GOOGLE_API_KEY and GEMINI_API_KEY are set" warning
# and other library-level chatter
logging.getLogger("pydantic_ai").setLevel(logging.ERROR)
os.environ["PYDANTIC_AI_LOG_LEVEL"] = "ERROR"

def load_config():
    """Loads the agent configuration from YAML."""
    config_path = os.path.join(current_dir, 'scout-config', 'scout_agent_config.yaml')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading YAML config: {e}", file=sys.stderr)
        return {"agent": {"system_prompt": "You are an AI Scout. {user_context}"}}

def load_user_preferences():
    """Loads and formats user-specific preferences from user_preferences.json."""
    pref_path = os.path.join(current_dir, 'scout-config', 'user_preferences.json')
    if not os.path.exists(pref_path):
        return "No specific user preferences provided."
    
    try:
        with open(pref_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        lines = []
        if positive := data.get("positive_preferences"):
            lines.append("POSITIVE PREFERENCES (Prioritize these):")
            for p in positive:
                lines.append(f"- {p['item']} (Reason: {p.get('reason', 'N/A')})")
        
        if negative := data.get("negative_constraints"):
            lines.append("\nNEGATIVE CONSTRAINTS (Reject these immediately):")
            for n in negative:
                lines.append(f"- {n['item']} (Reason: {n.get('reason', 'N/A')})")
        
        return "\n".join(lines) if lines else "No preferences specified."
    except Exception as e:
        return f"Error loading preferences: {str(e)}"

def load_central_config():
    """Loads the main project configuration from config.yaml."""
    config_path = os.path.join(current_dir, 'scout-config', 'config.yaml')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading central config: {e}", file=sys.stderr)
        return {"models": {"primary_brain": "gemini-2.0-flash", "temperature": 0.2}}

# 1. Load Configurations
config = load_config()
central_config = load_central_config()
user_pref_text = load_user_preferences()

# 2. Inject User Context into the System Prompt
final_system_prompt = config['agent']['system_prompt'].replace("{user_context}", user_pref_text)

def append_activity_log(title: str, status: str, reasoning: str):
    """Appends a single line to a local log file for real-time tracking."""
    log_path = os.path.join(current_dir, 'scout_activity.log')
    timestamp = datetime.now().strftime("%H:%M:%S")
    # Clean title to prevent log-splitting
    clean_title = title.replace('\n', ' ').replace('\r', '')[:80]
    log_entry = f"[{timestamp}] {status.upper().ljust(8)} | {clean_title.ljust(80)} | {reasoning}\n"
    try:
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except Exception:
        pass # Never fail the agent due to logging issues
    

from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel

# Set the model from central config
model_name = central_config['models']['primary_brain']
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
    system_prompt=final_system_prompt
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
        
        # Log the activity
        append_activity_log(title, data["status"], data["reasoning"])
        
        return json.dumps(data, indent=2, ensure_ascii=False)
    except Exception as e:
        reasoning = f"Classification error: {str(e)}"
        # Log the error status
        append_activity_log(title, "ERROR", reasoning)
        
        error_result = {
            "status": "Rejected",
            "reasoning": reasoning,
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
    parser.add_argument("--title", help="RSS Item Title")
    parser.add_argument("--snippet", help="RSS Item Content Snippet")
    parser.add_argument("--test", action="store_true", help="Run a quick internal test.")
    
    args = parser.parse_args()

    if args.test:
        test_title = "Pydantic AI: Agentic Framework"
        test_snippet = "A new library for building agentic AI with Pydantic validation. Highly efficient."
        asyncio.run(run_scout(test_title, test_snippet))
        print("Test cycle complete.")
        return
    elif not args.title or not args.snippet:
        parser.error("The following arguments are required: --title, --snippet (unless --test is used)")

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
