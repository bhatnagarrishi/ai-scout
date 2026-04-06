import os
import sys

# Ensure the current directory is in sys.path for local discovery
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent_tools import ReadFileTool, WriteFileTool, ListDirectoryTool
from orchestrator import ModelOrchestrator
from execution_loop import AutonomousAgent

def main():
    # 1. Initialize Tools
    tools = [ReadFileTool(), WriteFileTool(), ListDirectoryTool()]
    
    # 2. Setup System Prompt
    # We define the core rules for the autonomous agent here.
    system_prompt = (
        "You are an autonomous coding assistant. "
        "You have access to a file system. Use your tools sequentially to complete tasks. "
        "Always confirm your actions. Once the task is fully complete, "
        "provide a final answer summarizing what you did."
    )
    
    # 3. Initialize Orchestrator and Agent
    orchestrator = ModelOrchestrator(system_prompt=system_prompt, tools=tools)
    agent = AutonomousAgent(orchestrator=orchestrator)
    
    # 4. Define the task
    # This is a complex multi-step mission.
    task = "Perform a technical audit of the 'pocs/agent_loop' directory. " \
           "List all files, count the number of lines in every .py file found, " \
           "and create a 'pocs/agent_loop/audit_report.md' that summarizes your findings in a table."
    
    # 5. Run the loop
    result = agent.run(task)
    
    print("\n" + "="*50)
    print(f"AGENT FINAL RESPONSE:\n{result}")
    print("="*50)

if __name__ == "__main__":
    main()
