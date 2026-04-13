import os
import sys
from dotenv import load_dotenv

# Add project root to sys.path to load centralized config if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from langchainhub import Client
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from monitor import ReasoningAuditor

# --- Output Mirroring ---
class Tee:
    def __init__(self, *files):
        self.files = files
    def write(self, obj):
        for f in self.files:
            f.write(obj)
            f.flush()
    def flush(self):
        for f in self.files:
            f.flush()

# Load environment
load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

# Constants
RESEARCH_PATH = os.path.join(os.path.dirname(__file__), "research", "market_research.json")
MODEL_NAME = "gpt-4o-mini"

# Setup Auditor
auditor = ReasoningAuditor(RESEARCH_PATH)

# --- Mock Market Tools ---
def get_market_data():
    with open(RESEARCH_PATH, 'r') as f:
        return f.read()

# --- ReAct Agent Loop ---
llm = ChatOpenAI(
    model=MODEL_NAME, 
    temperature=0, 
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    default_headers={"OpenAI-Project": os.getenv("OPENAI_PROJECT")}
)

def run_strategy_session():
    # Load the "Ancient Scrolls" (Ground Truth)
    research_context = get_market_data()
    
    system_prompt = (
        "You are a Strategic Advisor for Samosa Hub. Your goal is to plan expansion into New Delhi, India.\n"
        "Our philosophy is Hyper-Localization: getting the 'pulse' of the local crowd and generating community goodwill.\n"
        "You MUST think before you act. Use the following format for your reasoning:\n"
        "Thought: <your internal logic here>\n"
        "Final Strategy: <your final plan here>\n\n"
        f"CONTEXT RESEARCH DATA:\n{research_context}"
    )
    
    user_prompt = (
        "Provide a 3-step strategy for our New Delhi expansion. "
        "Focus on local supply chains for goodwill, but maintain central governance for quality."
    )

    print("\n" + "="*50)
    print("STARTING EXPANSION STRATEGY SESSION")
    print("="*50 + "\n")

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]

    # Generate the response
    # In a real ReAct loop, we would handle tool calls here. 
    # For this POC, we focus on auditing the Reasoning/Chain of Thought (CoT).
    response = llm.invoke(messages)
    full_text = response.content

    print("EXTRACTING REASONING CHAIN...")
    
    # Extract "Thought" block using regex
    import re
    thoughts = re.findall(r"Thought: (.*?)(?=Final Strategy:|$)", full_text, re.DOTALL)
    
    if not thoughts:
        # Fallback if the model didn't use the prefix but provided CoT
        thoughts = [full_text.split("Final Strategy:")[0]]

    # Audit the extracted thoughts
    for i, thought in enumerate(thoughts):
        auditor.audit_step(i + 1, thought.strip())

    print("\n" + "="*50)
    print("FINAL STRATEGY OUTPUT")
    print("="*50)
    
    # Extract Final Strategy
    strategy_match = re.search(r"Final Strategy: (.*)", full_text, re.DOTALL)
    strategy = strategy_match.group(1).strip() if strategy_match else full_text
    
    print(f"\n{strategy}\n")
    
    report = auditor.get_final_report()
    print(f"Monitor Status: {report['status']}")
    print(f"Critical Flags Found: {len(report['critical_flags'])}")

if __name__ == "__main__":
    output_file_path = os.path.join(os.path.dirname(__file__), "chain-of-thought-output.txt")
    
    with open(output_file_path, "w", encoding="utf-8") as f:
        original_stdout = sys.stdout
        sys.stdout = Tee(sys.stdout, f)
        
        try:
            run_strategy_session()
        except Exception as e:
            print(f"\nExecution Failed: {str(e)}")
        finally:
            sys.stdout = original_stdout
            print(f"\n[INFO] Session log saved to: {output_file_path}")
