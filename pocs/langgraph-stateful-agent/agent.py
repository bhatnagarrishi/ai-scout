import os
import sqlite3
from typing import Annotated, TypedDict
from dotenv import load_dotenv

import yaml
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver

# Load .env from root
load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

# Load Central Config
def load_central_config():
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    config_path = os.path.join(root_dir, 'scout-config', 'config.yaml')
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

central_config = load_central_config()
model_name = central_config['models']['primary_brain']
temperature = central_config['models'].get('temperature', 0.2)

# 1. Define the State
class State(TypedDict):
    # add_messages ensures that new messages are appended to the history
    messages: Annotated[list[BaseMessage], add_messages]

# 2. Define the Node (The logic)
def call_model(state: State):
    # Use centralized model configuration
    llm = ChatGoogleGenerativeAI(
        model=model_name,
        temperature=temperature,
        google_api_key=os.getenv("GEMINI_API_KEY")
    )
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

# 3. Build the Graph
workflow = StateGraph(State)
workflow.add_node("agent", call_model)
workflow.set_entry_point("agent")
workflow.add_edge("agent", END)

# 4. Set up Persistence (SQLite)
# Ensure the DB is saved INSIDE the POC folder
db_path = os.path.join(os.path.dirname(__file__), "checkpoints.db")

with SqliteSaver.from_conn_string(db_path) as memory:
    app = workflow.compile(checkpointer=memory)

    def main():
        print("--- LangGraph Interactive Stateful Agent ---")
        print("Type 'exit' or 'quit' to stop.")
        print("Type 'reset' to clear the agent's memory.")
        print("-------------------------------------------\n")

        config = {"configurable": {"thread_id": "user_session_123"}}

        while True:
            user_input = input("User: ")
            
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            
            if user_input.lower() == "reset":
                if os.path.exists(db_path):
                    os.remove(db_path)
                    print(f"Memory reset: {db_path} deleted. Please restart the script.")
                    break
                else:
                    print("No memory to reset.")
                    continue

            # Run the agent with the user input
            input_data = {"messages": [HumanMessage(content=user_input)]}
            
            # Stream the response
            print("Processing...", end="\r")
            final_event = None
            for event in app.stream(input_data, config, stream_mode="values"):
                final_event = event
            
            if final_event and "messages" in final_event:
                last_message = final_event["messages"][-1]
                
                # Robust extraction of the text content
                content_text = ""
                if isinstance(last_message.content, str):
                    content_text = last_message.content
                elif isinstance(last_message.content, list):
                    for part in last_message.content:
                        if isinstance(part, dict) and 'text' in part:
                            content_text += part['text']
                        elif isinstance(part, str):
                            content_text += part
                
                print(f"Agent: {content_text}\n")

    if __name__ == "__main__":
        main()
