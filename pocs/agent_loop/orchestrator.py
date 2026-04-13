import os
import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from openai import OpenAI
from dotenv import load_dotenv

class ModelOrchestrator:
    """Orchestrates conversations with the LLM, managing system prompts and tool definitions."""
    def __init__(self, system_prompt: str, tools: List[Any], model: str = "gpt-4o"):
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key, project=os.getenv("OPENAI_PROJECT"))
        self.model = model
        self.system_prompt = system_prompt
        self.tools = {t.name: t for t in tools}
        self.tool_definitions = [t.get_openai_definition() for t in tools]
        self.log_path = os.path.join(os.path.dirname(__file__), "agent_trace.log")

    def _log_interaction(self, title: str, data: Any):
        """Appends a timestamped log entry to agent_trace.log."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(f"\n{'='*20} {title} ({timestamp}) {'='*20}\n")
            f.write(json.dumps(data, indent=2) if not isinstance(data, str) else data)
            f.write(f"\n{'='*60}\n")

    def query(self, messages: List[Dict[str, str]]) -> Any:
        """Sends the message history and tool definitions to the model."""
        
        # Ensure all messages in history are JSON-serializable (convert objects to dicts)
        serializable_history = []
        for m in messages:
            if hasattr(m, "model_dump"):
                serializable_history.append(m.model_dump())
            elif isinstance(m, dict):
                serializable_history.append(m)
            else:
                serializable_history.append(str(m))

        full_history = [{"role": "system", "content": self.system_prompt}] + serializable_history
        self._log_interaction("REQUEST TO OPENAI", full_history)
        
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=full_history,
            tools=self.tool_definitions,
            tool_choice="auto"
        )
        
        # Log serialized response (handling the AssistantMessage object)
        resp_data = completion.choices[0].message.model_dump() if hasattr(completion.choices[0].message, "model_dump") else str(completion.choices[0].message)
        self._log_interaction("RESPONSE FROM OPENAI", resp_data)
        
        return completion

class ResponseParser:
    """Parses model responses to determine if a tool call is required or if a final answer is provided."""
    @staticmethod
    def parse(message: Any) -> Dict[str, Any]:
        """Analyzes the message and extracts tool calls or text content."""
        if message.tool_calls:
            calls = []
            for tool_call in message.tool_calls:
                calls.append({
                    "id": tool_call.id,
                    "name": tool_call.function.name,
                    "arguments": json.loads(tool_call.function.arguments)
                })
            return {"type": "tool_call", "calls": calls}
        
        return {"type": "final_answer", "content": message.content}
