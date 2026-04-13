# SUMMARY: Advanced Data Analysis & Document Synthesis

## 🎯 Objective
To prove that AI Agents can serve as autonomous business analysts capable of synthesizing "messy" data from multiple formats (CSV and PDF) into high-fidelity visual and textual reports.

## 🏗️ Architecture
The POC utilizes a **Dual-Tool Interface** via the OpenAI Assistants API (v2):
1.  **Code Interpreter**: Acts as the "Quantitative Core," running Python scripts to perform statistical analysis and visualization on the `samosa_sales_complex.csv`.
2.  **File Search (Vector Store)**: Acts as the "Qualitative Core," performing semantic search over the `expansion_strategy.pdf` to ground numerical findings in business logic.
3.  **Stateful Persistence**: Uses a `Thread` based architecture to allow users to drill down into specific insights through follow-up questions.

## ✅ Success Metrics
*   **Visual Fidelity**: Successfully generated high-quality PNG charts in a sandboxed Python environment and retrieved them via the API.
*   **Logical Synthesis**: The model correctly identified that Gurugram sales were underperforming relative to the "South Delhi Benchmark" mentioned in the strategies.
*   **Environmental Robustness**: The implementation was hardened to resolve `.env` and data paths dynamically, ensuring the script runs flawlessly from both the POC subdirectory and the project root.
*   **SDK Versatility**: Successfully adapted the Assistant v2 logic to a non-standard OpenAI SDK structure (`v2.30.0`) found in the local environment.
