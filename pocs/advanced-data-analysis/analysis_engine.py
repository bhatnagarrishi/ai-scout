import os
import time
import json
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# Load API key from the project root .env
root_dir = Path(__file__).resolve().parent.parent.parent
dotenv_path = root_dir / '.env'
load_dotenv(dotenv_path=dotenv_path)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), project=os.getenv("OPENAI_PROJECT"))

# Directories
script_dir = Path(__file__).resolve().parent
data_dir = script_dir / "data"
output_dir = script_dir / "output"

def create_advanced_analyst():
    print("Initializing Advanced Data Analyst Assistant...")
    
    # 1. Upload files
    sales_file = client.files.create(
        file=(data_dir / "samosa_sales_complex.csv").open("rb"),
        purpose="assistants"
    )
    
    strategy_file = client.files.create(
        file=(data_dir / "expansion_strategy.pdf").open("rb"),
        purpose="assistants"
    )
    
    # 2. Create Vector Store for the PDF (file_search)
    vector_store = client.vector_stores.create(name="Expansion Strategy Store")
    client.vector_stores.files.create(
        vector_store_id=vector_store.id,
        file_id=strategy_file.id
    )
    
    # 3. Create Assistant
    assistant = client.beta.assistants.create(
        name="NCR Samosa Analyst",
        instructions=(
            "You are a Senior Business Analyst for Samosa Hub. "
            "You have access to a complex sales dataset (CSV) and an expansion strategy (PDF). "
            "Use the 'code_interpreter' to analyze numeric trends in the CSV and 'file_search' to "
            "reference strategy documents. Always provide data-driven insights. "
            "If asked to visualize data, use matplotlib and save the plots as PNG files."
        ),
        tools=[
            {"type": "code_interpreter"},
            {"type": "file_search"}
        ],
        model="gpt-4o",
        tool_resources={
            "file_search": {"vector_store_ids": [vector_store.id]},
            "code_interpreter": {"file_ids": [sales_file.id]}
        }
    )
    
    return assistant, vector_store, [sales_file.id, strategy_file.id]

def wait_on_run(run, thread):
    while run.status in ["queued", "in_progress"]:
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
    return run

def download_images(messages):
    output_dir.mkdir(exist_ok=True)
    images = []
    for msg in messages.data:
        for content in msg.content:
            if content.type == "image_file":
                file_id = content.image_file.file_id
                image_data = client.files.content(file_id)
                image_data_bytes = image_data.read()
                
                filename = output_dir / f"chart_{file_id}.png"
                with filename.open("wb") as f:
                    f.write(image_data_bytes)
                images.append(str(filename))
                print(f"Downloaded generated chart: {filename}")
    return images

def run_interaction(assistant_id, thread_id, user_message):
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=user_message
    )
    
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )
    
    run = wait_on_run(run, client.beta.threads.retrieve(thread_id))
    
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    
    # Download any generated images
    download_images(messages)
    
    # Print the assistant's text response
    for msg in messages.data:
        if msg.role == "assistant":
            # Extract text from all text blocks in the message
            text_blocks = [c.text.value for c in msg.content if c.type == "text"]
            if text_blocks:
                print(f"\n[Analyst]: {' '.join(text_blocks)}")
            break

if __name__ == "__main__":
    assistant, v_store, file_ids = create_advanced_analyst()
    thread = client.beta.threads.create()
    
    print("\n--- POC SESSION START ---")
    print("Assistant and Data are ready.")
    
    # Initial prompt to trigger complex multi-file analysis
    initial_prompt = (
        "Analyze the provided sales data and strategy document. "
        "1. Summarize the top 3 performing regions. "
        "2. Identify if any regions are failing to meet the 'South Delhi' benchmark mentioned in the strategy. "
        "3. Generate a trend chart showing revenue by product over time, specifically identifying the 'Chocolate Fusion' cannibalization mentioned."
    )
    
    print(f"\n[Initial Prompt]: {initial_prompt}")
    run_interaction(assistant.id, thread.id, initial_prompt)
    
    # Interactive loop
    while True:
        user_input = input("\n[You] (or 'exit' to quit): ")
        if user_input.lower() in ['exit', 'quit']:
            break
        run_interaction(assistant.id, thread.id, user_input)

    # Cleanup (Optional - keep for POC verification, delete later if cost is concern)
    # client.beta.assistants.delete(assistant.id)
    # client.vector_stores.delete(v_store.id)
