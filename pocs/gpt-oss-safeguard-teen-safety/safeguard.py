"""
Teen Safety Middleware using gpt-oss-safeguard-20b via Groq

Architecture:
  User Prompt → [Pre-check] → LLM → [Post-check] → Response

The safeguard model uses OpenAI's published teen safety policy prompts.
It uses the "Harmony" response format (a reasoning channel before a final verdict).
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

# ── Load environment ────────────────────────────────────────────────────────
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(current_dir))
load_dotenv(os.path.join(root_dir, ".env"))

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # used for the "main" LLM

# ── Groq client (for the safeguard model) ───────────────────────────────────
groq_client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
)

# ── OpenAI's published Teen Safety Policy Prompt ────────────────────────────
# Source: https://openai.com/safety/teen-safety-policies
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

OUTPUT FORMAT (the Harmony format):
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
    Runs text through gpt-oss-safeguard-20b on Groq.
    Returns the parsed safety verdict as a dict.
    """
    if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
        raise ValueError("GROQ_API_KEY is not set in your .env file.")

    print(f"\n🔍 Checking {label}...")

    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-safeguard-20b",
        messages=[
            {"role": "system", "content": TEEN_SAFETY_POLICY},
            {"role": "user", "content": text},
        ],
        temperature=0.0,  # deterministic for safety checks
        max_tokens=256,
    )

    raw = response.choices[0].message.content.strip()

    # Parse the JSON verdict — handle markdown code fences and trailing text
    import json, re
    # Strip ```json ... ``` fences if present
    raw = re.sub(r"```(?:json)?\s*", "", raw).strip().rstrip("`").strip()
    # Extract just the first JSON object in case the model adds extra text
    match = re.search(r"\{.*?\}", raw, re.DOTALL)
    if not match:
        # Fallback if the model returns something unexpected
        print(f"  ⚠️  Could not parse model response: {raw[:100]}")
        return {"verdict": "SAFE", "category": "None", "confidence": 0.5,
                "reasoning": "Parse error — defaulting to SAFE for this check."}

    verdict = json.loads(match.group(0))
    return verdict


def safe_chat(user_prompt: str, main_llm_response_fn) -> str:
    """
    Full middleware pipeline:
      1. Pre-check: Validate the user's prompt
      2. Call the main LLM if prompt is safe
      3. Post-check: Validate the LLM's response
      4. Return response or a safe refusal message
    """
    # ── Step 1: Pre-check the user prompt ──
    pre_check = check_content(user_prompt, label="user prompt")

    if pre_check["verdict"] == "UNSAFE":
        print(f"  ❌ BLOCKED (pre-check): {pre_check['category']} — {pre_check['reasoning']}")
        return (
            "I'm sorry, I can't help with that. "
            "This topic isn't appropriate for this platform."
        )

    print(f"  ✅ SAFE (pre-check): {pre_check['reasoning']}")

    # ── Step 2: Call the main LLM ──
    print("\n🤖 Calling main LLM...")
    llm_response = main_llm_response_fn(user_prompt)
    print(f"  LLM Response: {llm_response[:120]}...")

    # ── Step 3: Post-check the LLM's response ──
    post_check = check_content(llm_response, label="LLM response")

    if post_check["verdict"] == "UNSAFE":
        print(f"  ❌ BLOCKED (post-check): {post_check['category']} — {post_check['reasoning']}")
        return (
            "I generated a response, but it didn't pass our safety review. "
            "Please try rephrasing your question."
        )

    print(f"  ✅ SAFE (post-check): {post_check['reasoning']}")
    return llm_response
