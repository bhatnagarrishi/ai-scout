import os
import json
from typing import List, Dict, Any
from agent_tools import BaseTool
from orchestrator import ModelOrchestrator, ResponseParser

class AutonomousAgent:
    """The core engine that runs the autonomous loop until a task is completed."""
    def __init__(self, orchestrator: ModelOrchestrator):
        self.orchestrator = orchestrator
        self.message_history: List[Any] = []

    def run(self, user_prompt: str, max_steps: int = 10):
        """Starts the autonomous execution loop."""
        print(f"--- Starting Agent Loop: '{user_prompt}' ---")
        self.message_history.append({"role": "user", "content": user_prompt})
        
        for step in range(max_steps):
            print(f"Step {step + 1}: Querying Model...")
            completion = self.orchestrator.query(self.message_history)
            assistant_msg = completion.choices[0].message
            
            # Always add model response to history
            self.message_history.append(assistant_msg)
            
            # Parse the response
            parsed = ResponseParser.parse(assistant_msg)
            
            if parsed["type"] == "final_answer":
                print(f"--- Final Answer Reached ---")
                return parsed["content"]
            
            if parsed["type"] == "tool_call":
                for call in parsed["calls"]:
                    tool_name = call["name"]
                    args = call["arguments"]
                    tool = self.orchestrator.tools.get(tool_name)
                    
                    if tool:
                        print(f"Action: Executing tool '{tool_name}' with args {args}")
                        result = tool.execute(**args)
                        
                        # Add tool result to history
                        self.message_history.append({
                            "role": "tool",
                            "tool_call_id": call["id"],
                            "name": tool_name,
                            "content": result
                        })
                    else:
                        error_msg = f"Error: Tool '{tool_name}' not found."
                        print(error_msg)
                        self.message_history.append({
                            "role": "tool",
                            "tool_call_id": call["id"],
                            "name": tool_name,
                            "content": error_msg
                        })

        return "Error: Maximum steps reached without a final answer."
