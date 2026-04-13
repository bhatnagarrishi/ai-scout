# SUMMARY: Reasoning Chain Monitor

## 🎯 Objective
This POC addresses the "Black Box" problem of AI agents. When an agent comes up with a strategy, we often don't know if its reasoning was sound or if it hallucinated constraints. This project implements a way to audit the "Chain of Thought" (CoT) before a plan is finalized.

## 🏗️ Architecture
The system uses a **Dual-Layer Auditor Pattern**:
1.  **The Strategist (LLM)**: Generates a plan using internal scratchpads (CoT).
2.  **The Auditor (Python)**: A deterministic engine that intercepts the Strategist's "Thoughts" and checks them against a **Ground Truth** research database.
3.  **Segregation**: By using regex to extract `Thought:` blocks, the Auditor can validate logic without the LLM being able to influence or "trick" the guardrails.

## ✅ Success Metrics
*   **Safety**: Successfully flagged a "Logic Failure" when the agent proposed a supply chain strategy that violated hyper-local sourcing rules stored in the research data.
*   **Auditability**: Generated a full `chain-of-thought-output.txt` ledger, showing every step of the reasoning and the corresponding audit results.
