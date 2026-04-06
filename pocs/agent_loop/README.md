# Modular Agent Loop POC

This Proof of Concept demonstrates the core architecture of an autonomous agent using OpenAI's tool-calling capabilities. It showcases how to orchestrate model reasoning, validate tool schemas, and maintain an execution loop.

## Architecture Highlights
- **Layer 1: Tools (`agent_tools.py`)**: Uses **Pydantic** to define strict schemas for file-system operations (`read_file`, `write_file`, `list_directory`).
- **Layer 2: Orchestrator (`orchestrator.py`)**: Manages the conversation state and handles the interface with the OpenAI Chat Completion API.
- **Layer 3: Parser (`orchestrator.py`)**: A dedicated logic layer that detects if the model is asking for a tool call or giving a final answer.
- **Layer 4: Execution Loop (`execution_loop.py`)**: The autonomous engine that recursively processes tool calls until the task is complete.
- **Layer 5: Communication Trace (`agent_trace.log`)**: A real-time log that captures all raw JSON communication (requests/responses) with OpenAI.

## Prerequisites
- Python 3.10+
- OpenAI API Key (configured in your `.env`)

## Installation
From the root of the project, install the necessary dependencies:
```bash
pip install -r pocs/agent_loop/requirements.txt
```

## Running the POC
Execute the main entry point from the root directory:
```bash
python pocs/agent_loop/main.py
```

## Example Task
The embedded "Technical Audit" task asks the agent to:
1. List all files in the POC directory.
2. Read every `.py` file found and count its lines.
3. Generate a Markdown report (`audit_report.md`) summarizing the codebase complexity.
