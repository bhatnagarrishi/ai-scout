# LEARNINGS: LLM Visual Brainstorming

## 🛠️ Technical Insights

### 1. Mermaid Rendering Constraints
*   **VS Code Support**: Standard VS Code Markdown preview **does not** render Mermaid by default. Users must install the `bierner.markdown-mermaid` extension.
*   **Crowding**: Mermaid mindmaps get "congested" quickly with long labels.
*   **Optimization**: Using `<br/>` tags and shorter keyword-based labels (Divergent Thinking -> Divergent Thinking) is essential for a professional look.
*   **Node Shapes**: Using distinct shapes (`(( ))`, `{{ }}`, `[ ]`) helps the user visually distinguish between analysis levels.

### 2. The Power of "SystemMessage" Segregation
Instead of one large prompt, using two distinct agents (the **Analyst** and the **Visualizer**) prevented the LLM from getting "distracted" by conversational fluff.
*   **Analyst**: Focused 100% on logic.
*   **Visualizer**: Focused 100% on syntax.

### 3. Human-in-the-Loop Gateway
Placing an `input()` call between Stage 1 and Stage 3 is a simple but effective "guardrail." It prevents the generation of complex diagrams based on flawed or incomplete analysis.

## 🚀 Recommendation for AI Scout
We should integrate this "Visualizer" pattern into the primary AI Scout loop. Before the agent creates a large set of GitHub issues, it should produce a Mermaid flowchart of the proposed plan for human approval.
