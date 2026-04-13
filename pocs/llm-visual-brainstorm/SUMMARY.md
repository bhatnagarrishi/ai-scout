# SUMMARY: LLM Visual Brainstorming

## 🎯 Objective
This POC addresses the difficulty of converting sprawling, unstructured LLM brainstorms into actionable, visual project plans. It implements a multi-stage pipeline that "funnels" ideas from raw concepts into structured Mermaid diagrams.

## 🏗️ Architecture
The system uses **LangChain** and **OpenAI GPT-4o-mini** to drive a three-stage process:
1.  **Divergent Analysis**: Breaking down the user prompt using First Principles and SWOT.
2.  **Human Gateway**: An interactive pause where the user must approve the logic before proceeding.
3.  **Convergent Visualization**: Translating the approved markdown analysis into a clean, hierarchical Mermaid Mindmap.

## ✅ Success Metrics
*   **Structure**: Successfully converts a paragraph of text into a structured Markdown + Mermaid report.
*   **Human Control**: Demonstrates that "steering" the LLM during the intermediate phase significantly improves the final diagram's relevance.
*   **Persistence**: Automates the generation of `output.md` as a living document.
