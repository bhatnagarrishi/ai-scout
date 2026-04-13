import os
import sys
from dotenv import load_dotenv
from typing import List
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

# Load environment variables
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
if not load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env')):
    print("Warning: .env file not found. Ensure API keys are set.")

MODEL_NAME = "gpt-4o-mini"
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "output.md")

llm = ChatOpenAI(model=MODEL_NAME, temperature=0.7)

def generate_brainstorm(topic: str) -> str:
    system_prompt = (
        "You are an expert Strategic Consultant and Systems Architect. "
        "The user will provide a problem domain or a business idea. "
        "You must analyze it using 'First Principles' thinking and provide a quick SWOT analysis. "
        "Format your response cleanly using markdown (bullet points, bold text). "
        "Keep it concise, actionable, and structured."
    )
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Analyze this topic: {topic}")
    ]
    
    response = llm.invoke(messages)
    return response.content

def generate_mermaid_diagram(brainstorm_text: str) -> str:
    system_prompt = (
        "You are an expert at creating Mermaid.js diagrams. "
        "Take the provided Brainstorming analysis (SWOT/First Principles) and distill it into a highly structured Mermaid.js mindmap or flowchart diagram. "
        "Make it visually comprehensive but clean. "
        "IMPORTANT: You MUST output ONLY valid Mermaid code, wrapped in a ```mermaid markdown block. Do not include any other conversational text."
    )
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Here is the brainstorming material. Convert it to a diagram:\n\n{brainstorm_text}")
    ]
    
    response = llm.invoke(messages)
    return response.content

def main():
    print("=" * 60)
    print("LLM Visual Brainstorming to Project Plan Validator")
    print("=" * 60)
    
    default_topic = "Launching a new restaurant in New Delhi focusing on hyper-local community sourcing (Mandis) and centralized quality governance (Secret Spice Blend)."
    print(f"\nDefault Topic:\n{default_topic}\n")
    
    user_input = input("Press ENTER to use default, or type a custom topic: ").strip()
    topic = user_input if user_input else default_topic
    
    history = topic
    
    while True:
        print("\nGenerating Brainstorm Analysis (First Principles & SWOT)...")
        try:
            analysis = generate_brainstorm(history)
        except Exception as e:
            print(f"LLM generation failed: {e}")
            break
        
        print("\n" + "=" * 60)
        print("BRAINSTORMING RESULTS:")
        print("=" * 60)
        print(analysis)
        print("=" * 60)
        
        print("\nWhat would you like to do?")
        print("1. [P] Proceed and generate Visual Mermaid Diagram")
        print("2. [R] Refine this analysis (give me a prompt to adjust it)")
        print("3. [Q] Quit")
        
        choice = input("> ").strip().lower()
        
        if choice == '1' or choice == 'p' or choice == 'proceed':
            print("\nGenerating Mermaid.js Visual Plan...")
            try:
                mermaid_output = generate_mermaid_diagram(analysis)
            except Exception as e:
                print(f"Diagram generation failed: {e}")
                break
                
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                f.write(f"# Visual Project Plan\n\n")
                f.write(f"**Topic**: {topic}\n\n")
                f.write("## Brainstorm Summary\n")
                f.write(analysis + "\n\n")
                f.write("## Architecture / Flow Diagram\n")
                f.write(mermaid_output)
            
            print(f"\nSuccess! Diagram generated and saved to {OUTPUT_FILE}")
            print("Preview this markdown file in VSCode to see the rendered Mermaid diagram.")
            break
            
        elif choice == '2' or choice == 'r' or choice == 'refine':
            refinement = input("\nHow should we adjust this analysis? ").strip()
            history = f"Original Topic: {history}\n\nPrevious Analysis Context: {analysis}\n\nUser Refinement Request: {refinement}\n\nPlease update the analysis incorporating this feedback. Keep the formatting clean and structured."
            
        elif choice == '3' or choice == 'q' or choice == 'quit':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please press 1, 2, or 3.")

if __name__ == "__main__":
    main()
