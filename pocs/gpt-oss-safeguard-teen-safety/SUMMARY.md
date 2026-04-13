# SUMMARY: Teen Safety Middleware

## 🎯 Objective
This POC demonstrates a content moderation pipeline specifically designed for teen safety. It addresses the inadequacy of simple keyword filters by using **reasoning models** to understand context, intent, and educational value.

## 🏗️ Architecture
The project implements a **Dual-Layer Middleware**:
1.  **Pre-check**: Audits the user's prompt *before* it reaches the main LLM to block jailbreaks or harmful queries.
2.  **Post-check**: Audits the LLM's response *before* it reaches the user to ensure the generated content complies with the safety policy.
3.  **Backend Flexibility**: The system works with Cloud APIs (Groq), Local models (Ollama), and self-hosted servers (vLLM) using the standard OpenAI SDK.

## ✅ Success Metrics
*   **Context Awareness**: Successfully passed a complex question about WWII casualties (marked SAFE because it was educational) while blocking non-educational violent content.
*   **Policy-Driven**: Proved that moderation can be updated by simply changing a system prompt "policy" rather than retraining a model.
