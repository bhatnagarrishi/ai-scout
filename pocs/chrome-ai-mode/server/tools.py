# tools.py — LangChain tool definitions for AI Mode POC

import json
import os
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent

# ── LLM Setup ─────────────────────────────────────────────────────────────────
def _get_llm(temperature: float = 0.3):
    return ChatOpenAI(
        model="gpt-4o-mini",
        temperature=temperature,
        api_key=os.environ.get("OPENAI_API_KEY"),
    )


# ── Summary Tool ──────────────────────────────────────────────────────────────
def summarize_page(context: str) -> dict:
    """Call LLM to produce a structured page summary."""
    llm = _get_llm(temperature=0.2)

    prompt = f"""You are an expert content analyst. Analyze the following webpage content and return a JSON object with these exact keys:
- "summary": A 2-3 sentence executive summary of the page
- "key_topics": A JSON array of 3-7 main topics covered (strings)
- "content_type": One of: "news_article", "research_paper", "product_page", "documentation", "blog_post", "social_media", "forum", "video_page", "other"
- "reading_time_minutes": Estimated reading time as a float
- "sentiment": One of: "positive", "negative", "neutral", "mixed"

Respond ONLY with valid JSON. No markdown fences.

PAGE CONTENT:
{context[:5000]}"""

    response = llm.invoke(prompt)
    content = response.content.strip()
    # Strip markdown code fences if present
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
    return json.loads(content)


# ── LangChain Tools for the Agent Loop ───────────────────────────────────────
@tool
def tool_extract_tables(context: str) -> str:
    """Extract and format all data tables found in the page content as structured markdown."""
    llm = _get_llm(temperature=0.1)
    prompt = f"""Extract all tabular data from the following webpage content.
Format each table in clean markdown with headers. If no tables exist, say "No structured tables found."
Return only the tables with brief labels, no additional commentary.

PAGE CONTENT:
{context[:4000]}"""
    return llm.invoke(prompt).content


@tool
def tool_extract_arguments(context: str) -> str:
    """Identify and structure the main claims, arguments, and supporting evidence on the page."""
    llm = _get_llm(temperature=0.3)
    prompt = f"""Analyze the following webpage and identify the key arguments or claims being made.
Format your response as:
## Main Arguments
1. [Argument] — [Supporting evidence or context]
2. ...

## Counterpoints (if present)
- ...

## Overall Position
[1-2 sentence summary of the page's overall stance]

PAGE CONTENT:
{context[:5000]}"""
    return llm.invoke(prompt).content


@tool
def tool_explore_links(links_json: str) -> str:
    """Categorize outbound links on the page into types: references, navigation, external resources, social, etc."""
    llm = _get_llm(temperature=0.1)
    prompt = f"""Analyze these links from a webpage and categorize them.
Group them as:
- **References / Citations**: Academic or journalistic sources
- **Internal Navigation**: Links within the same site
- **External Resources**: Relevant external sites
- **Social Media**: Twitter, LinkedIn, YouTube, etc.
- **Other / Ads**: Everything else

Links (JSON):
{links_json[:3000]}

Format as a clean markdown list grouped by category."""
    return llm.invoke(prompt).content


@tool
def tool_custom_query(query_and_context: str) -> str:
    """Answer a free-form question about the page content. Input format: 'QUERY: [question]\nCONTEXT: [page text]'"""
    llm = _get_llm(temperature=0.5)
    prompt = f"""You are a helpful AI assistant analyzing a webpage for a user.
Answer the user's question based ONLY on the provided page content.
If the page doesn't contain enough information, say so.

{query_and_context[:5000]}"""
    return llm.invoke(prompt).content


# ── Relationship Graph ─────────────────────────────────────────────────────────
def map_content_relationships(context: str, headings: list) -> dict:
    """Build a D3.js-compatible force graph of content relationships."""
    llm = _get_llm(temperature=0.2)

    headings_text = "\n".join(
        f"- {h.get('level', 'h2').upper()}: {h.get('text', '')}" for h in headings[:20]
    ) if headings else "No headings extracted."

    prompt = f"""Analyze this webpage and create a knowledge graph of content relationships.
Return a JSON object with exactly these keys:
- "nodes": array of objects with "id" (string), "label" (string), "type" ("topic"|"concept"|"entity"|"claim"|"source")
- "links": array of objects with "source" (node id), "target" (node id), "label" (relationship description string)

Rules:
- 8-20 nodes maximum
- Make the graph meaningful and connected
- Use the headings as primary topic nodes
- Connect related concepts as child/sibling nodes
- Respond ONLY with valid JSON, no markdown fences

PAGE HEADINGS:
{headings_text}

PAGE CONTENT (excerpt):
{context[:3000]}"""

    response = llm.invoke(prompt)
    content = response.content.strip()
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]

    try:
        graph = json.loads(content)
        # Validate structure
        nodes = graph.get("nodes", [])
        links = graph.get("links", [])
        # Ensure all link source/target IDs exist in nodes
        node_ids = {n["id"] for n in nodes}
        valid_links = [l for l in links if l["source"] in node_ids and l["target"] in node_ids]
        return {"nodes": nodes, "links": valid_links}
    except json.JSONDecodeError:
        # Fallback: return minimal graph from headings
        nodes = [{"id": f"h{i}", "label": h.get("text", "Topic"), "type": "topic"}
                 for i, h in enumerate(headings[:10])]
        links = [{"source": "h0", "target": f"h{i}", "label": "contains"} for i in range(1, len(nodes))]
        return {"nodes": nodes, "links": links}


# ── Agentic Loop ──────────────────────────────────────────────────────────────
def run_agent(command: str, context: str, page_data: dict) -> str:
    """
    Run the LangGraph ReAct agent to fulfill a user command.
    The agent selects and chains the right tools automatically.
    """
    llm = _get_llm(temperature=0.4)

    tools = [
        tool_extract_tables,
        tool_extract_arguments,
        tool_explore_links,
        tool_custom_query,
    ]

    system_prompt = f"""You are an intelligent web page analyst assistant built into a Chrome browser extension.
You have access to tools to analyze the current webpage. Use the right tool(s) to fulfill the user's command.

Always use the page context provided. Do not make up information not present in the page.
Be concise, well-structured, and use markdown formatting in your final answer.

CURRENT PAGE CONTEXT:
{context[:4000]}"""

    agent = create_react_agent(llm, tools, prompt=system_prompt)

    messages = [HumanMessage(content=command)]
    result = agent.invoke({"messages": messages})

    # Extract the last AI message as the final answer
    ai_messages = [m for m in result.get("messages", []) if hasattr(m, "content") and m.__class__.__name__ != "HumanMessage"]
    if ai_messages:
        return ai_messages[-1].content
    return "No result produced."
