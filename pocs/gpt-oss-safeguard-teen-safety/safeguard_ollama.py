"""
Teen Safety Middleware — Ollama (Local) Implementation

Same pipeline as safeguard.py but runs 100% offline using Ollama.
Supports both gpt-oss-safeguard:20b and llama-guard3:8b (lighter alternative).

Usage:
    # Make sure Ollama is running and the model is pulled:
    #   ollama pull gpt-oss-safeguard:20b   (requires ~16GB RAM)
    #   OR
    #   ollama pull llama-guard3:8b          (requires ~8GB RAM)
    
    from safeguard_ollama import check_content, safe_chat
"""

import os
import json
import re
from openai import OpenAI  # Ollama exposes an OpenAI-compatible API

# ── Ollama runs a local server on port 11434 ────────────────────────────────
ollama_client = OpenAI(
    api_key="ollama",           # Ollama doesn't need a real key
    base_url="http://localhost:11434/v1",
)

# ── Model selection ─────────────────────────────────────────────────────────
# Use gpt-oss-safeguard:20b if you have 16GB+ RAM, else llama-guard3:8b
SAFEGUARD_MODEL = os.getenv("OLLAMA_SAFEGUARD_MODEL", "llama-guard3:8b")

# ── Teen Safety Policy (same policy, works with both models) ─────────────────
TEEN_SAFETY_POLICY = """
You are a content safety classifier for teen-oriented AI applications.

POLICY — Flag content as UNSAFE if it:
1. Contains graphic violence or gore
2. Contains sexual content of any kind
3. Promotes harmful body ideals, extreme dieting, eating disorders, or appearance rating
4. Encourages dangerous activities or viral challenges that risk physical harm
5. Involves intense romantic roleplay, or the AI acting as a substitute therapist/romantic partner
6. Provides instructions for self-harm or suicide
7. Contains hate speech, slurs, or discrimination based on identity

POLICY — Content is SAFE if it:
- Discusses these topics in a clearly educational or preventive context
- Is general knowledge, news, or age-appropriate entertainment content

OUTPUT FORMAT:
You must ALWAYS respond with a JSON object in this exact format:
{
  "verdict": "SAFE" or "UNSAFE",
  "category": "None" or one of [violence, sexual, body_image, dangerous_activity, inappropriate_roleplay, self_harm, hate_speech],
  "confidence": 0.0-1.0,
  "reasoning": "One sentence explaining the verdict."
}
""".strip()


def check_content(text: str, label: str = "content") -> dict:
    """
    Runs text through the local Ollama safeguard model.
    Returns the parsed safety verdict as a dict.
    """
    print(f"\n🔍 Checking {label} (via Ollama / {SAFEGUARD_MODEL})...")

    try:
        response = ollama_client.chat.completions.create(
            model=SAFEGUARD_MODEL,
            messages=[
                {"role": "system", "content": TEEN_SAFETY_POLICY},
                {"role": "user", "content": text},
            ],
            temperature=0.0,
            max_tokens=256,
        )
    except Exception as e:
        if "Connection refused" in str(e) or "Failed to connect" in str(e):
            raise RuntimeError(
                "Cannot connect to Ollama. Is it running?\n"
                "Start it with: ollama serve"
            ) from e
        raise

    raw = response.choices[0].message.content.strip()

    # Parse JSON — handle markdown fences and extra text
    raw = re.sub(r"```(?:json)?\s*", "", raw).strip().rstrip("`").strip()
    match = re.search(r"\{.*?\}", raw, re.DOTALL)
    if not match:
        print(f"  ⚠️  Could not parse model response: {raw[:100]}")
        return {
            "verdict": "SAFE",
            "category": "None",
            "confidence": 0.5,
            "reasoning": "Parse error — defaulting to SAFE.",
        }

    return json.loads(match.group(0))


def safe_chat(user_prompt: str, main_llm_response_fn) -> str:
    """
    Full middleware pipeline (identical interface to safeguard.py):
      1. Pre-check: Validate the user's prompt
      2. Call the main LLM if prompt is safe
      3. Post-check: Validate the LLM's response
      4. Return response or a safe refusal message
    """
    # ── Step 1: Pre-check ──
    pre_check = check_content(user_prompt, label="user prompt")

    if pre_check["verdict"] == "UNSAFE":
        print(f"  ❌ BLOCKED (pre-check): {pre_check['category']} — {pre_check['reasoning']}")
        return "I'm sorry, I can't help with that topic on this platform."

    print(f"  ✅ SAFE (pre-check): {pre_check['reasoning']}")

    # ── Step 2: Call main LLM ──
    print("\n🤖 Calling main LLM...")
    llm_response = main_llm_response_fn(user_prompt)
    print(f"  LLM Response: {llm_response[:120]}...")

    # ── Step 3: Post-check ──
    post_check = check_content(llm_response, label="LLM response")

    if post_check["verdict"] == "UNSAFE":
        print(f"  ❌ BLOCKED (post-check): {post_check['category']} — {post_check['reasoning']}")
        return "My response didn't pass our safety review. Please try rephrasing."

    print(f"  ✅ SAFE (post-check): {post_check['reasoning']}")
    return llm_response
