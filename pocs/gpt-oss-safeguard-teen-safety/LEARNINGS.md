# LEARNINGS: Teen Safety Middleware (gpt-oss-safeguard)

## 1. `gpt-oss-safeguard` is a model, not a library

The GitHub issue action plan said "pip install gpt-oss-safeguard" — this doesn't exist. It's an **open-weight reasoning model** by OpenAI, accessed via:
- **Groq** (cloud, OpenAI-compatible API)
- **Ollama** (local, OpenAI-compatible API)
- **vLLM** (self-hosted server)

The key insight: **the `openai` Python SDK works with all three** — you just change `base_url`.

---

## 2. The "Bring Your Own Policy" design pattern

Unlike traditional keyword filters, `gpt-oss-safeguard` doesn't have hardcoded rules. You provide a **policy prompt** in the system message, and it reasons against it. This means:

- **Flexibility**: Swap policies for different audiences (teens, enterprise, medical)
- **Auditability**: The model explains *why* it flagged content via the `reasoning` field
- **No retraining**: Update your policy by editing a string, not retraining a model

---

## 3. Context-aware classification beats keyword filtering

The most impressive result: **WWII question was correctly marked SAFE** despite containing "violence."

A keyword filter would block "war," "casualties," "killing." This model understood the *educational intent* and passed it through. This is the core value proposition of LLM-based moderation.

---

## 4. Ollama = OpenAI-compatible API at `localhost:11434`

Ollama runs a local REST server that's **100% compatible** with the `openai` Python SDK:

```python
# Cloud (OpenAI)
client = OpenAI(api_key="sk-...")

# Cloud (Groq)
client = OpenAI(api_key="gsk_...", base_url="https://api.groq.com/openai/v1")

# Local (Ollama) — no API key needed
client = OpenAI(api_key="ollama", base_url="http://localhost:11434/v1")
```

**Same code interface, three different execution environments.** This is the power of the OpenAI-compatible standard.

---

## 5. Pre-check AND post-check is critical

The two-layer pipeline catches different attack vectors:
- **Pre-check**: Stops jailbreak prompts from reaching the main LLM
- **Post-check**: Catches cases where the LLM generates unsafe content despite a safe-seeming prompt (prompt injection, indirect attacks)

Running only one layer leaves a gap.

---

## 6. Performance trade-offs

| Backend | Latency per check | Privacy | Cost |
|---|---|---|---|
| Groq (cloud) | ~1-2 seconds | Data leaves machine | Free tier |
| Ollama (local, 20B) | ~15-30 seconds (CPU) | 100% private | One-time download |
| Ollama (local, 8B) | ~5-10 seconds | 100% private | Smaller model |

For **real-time apps**: Use Groq. For **privacy-sensitive or offline apps**: Use Ollama with GPU acceleration.

---

## 7. Strategic Recommendation

This pattern (policy-prompt + reasoning model + pre/post pipeline) is directly applicable to the AI Scout project. Before creating GitHub issues, the `scout_agent.py` could run a **content-quality check** using the same middleware pattern to ensure generated issue content is professional and actionable.
