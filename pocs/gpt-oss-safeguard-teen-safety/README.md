# POC: Teen Safety Middleware with gpt-oss-safeguard

This POC implements a **pre/post content moderation pipeline** for teen-oriented AI apps using OpenAI's `gpt-oss-safeguard-20b` model, hosted via **Groq**.

## 🚀 Architecture

```
User Prompt
    │
    ▼
[Pre-Check: safeguard model]   ← Blocks unsafe prompts BEFORE the LLM sees them
    │ SAFE
    ▼
Main LLM (Gemini / GPT-4o)
    │
    ▼
[Post-Check: safeguard model]  ← Catches unsafe LLM responses BEFORE delivery
    │ SAFE
    ▼
Final Response to User
```

## 🛠️ Tech Stack
- **Safety Model**: `openai/gpt-oss-safeguard-20b` (via Groq Cloud)
- **Client**: `openai` Python SDK (OpenAI-compatible, pointed at Groq's base URL)
- **Policy**: OpenAI's published Teen Safety prompt-based policies (March 2026)
- **Runtime**: Python 3.9+

## 🏃 How to Run

1. Add your Groq API key to the root `.env`:
   ```
   GROQ_API_KEY=gsk_your_key_here
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the demo:
   ```bash
   python demo.py
   ```

## 📁 Files
| File | Purpose |
|---|---|
| `safeguard.py` | Core middleware — `check_content()` and `safe_chat()` |
| `demo.py` | 7 edge-case test prompts (safe, borderline, unsafe) |

## 🧠 Key Learnings
*(To be filled in after running the demo)*
