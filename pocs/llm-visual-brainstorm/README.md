# POC: LLM Visual Brainstorming to Project Plan

> **Mission**: Transform unstructured idea generation into a concrete, structured visual process map.

---

## 🎯 The Goal
Large Language Models are excellent at raw brainstorming but often produce unstructured "walls of text" that are difficult to convert into actionable roadmaps. 

This POC demonstrates an **Iterative Funnel Workflow**:
1. **Divergent Thinking**: The LLM uses First Principles and SWOT analysis to break down a raw concept.
2. **Human-in-the-Loop Refinement**: The user reviews the structured analysis and can "steer" the LLM's logic in real-time.
3. **Convergent Visualization**: Once approved, a secondary agent takes the explicit reasoning and generates a structured **Mermaid.js diagram** visualizing the outcome.

## 🏗️ Architecture

This POC uses a **Multi-Stage LangChain Pipeline** interspersed with a Human-in-the-Loop gateway:

1. **Stage 1 (The Analyst Engine)**:
   - Uses `gpt-4o-mini` with a specialized `SystemMessage`.
   - **Input**: Raw, unstructured user concept.
   - **Output**: Pure markdown text strictly structured strictly around "First Principles" and "SWOT". 

2. **Stage 2 (The Human Gateway)**:
   - The interactive Python terminal (`input()`).
   - Pauses the pipeline. The LLM loses autonomy here; the user decides if the logic is sound or if the context needs forced refinement.

3. **Stage 3 (The Visual Translation Engine)**:
   - Uses `gpt-4o-mini` with a new, distinct `SystemMessage`.
   - **Input**: The approved SWOT analysis text from Stage 1.
   - **Output**: Extracts the structural components and generates a raw `Mermaid.js` syntax block. It strips all conversational chatter.

4. **Persistence Layer**:
   - The Python script combines both the textual context (Stage 1) and visual syntax (Stage 3) and writes them to a static `output.md` file, allowing standard Markdown viewers to render the final unified report.

## 🧪 The "Delhi Restaurant" Test Case
We default test this by asking the system to plan the launch of a new Samosa Hub restaurant in New Delhi. 
The plan enforces our previous rules: **Hyper-local community sourcing** combined with **Centralized quality governance**.

## 🛠️ How it Works
- **Orchestrator**: Simple python script `plan_generator.py` taking advantage of `langchain_openai`.
- **Model**: OpenAI `gpt-4o-mini` (fast and handles structured Mermaid syntax well).
- **Output**: Generates an `output.md` file containing the raw context and a fully rendered visual graph.

## 🏃 Setup
1. Ensure your root `.env` has a valid `OPENAI_API_KEY`.
2. Install dependencies: `pip install -r requirements.txt`.
3. Run the session: `python plan_generator.py`.
4. Open the generated `output.md` in VSCode with a Markdown extension (or GitHub) to view the rendered Mermaid graph.
