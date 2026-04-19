# server.py — FastAPI backend for Chrome AI Mode POC
# Provides three endpoints consumed by the Chrome extension.

import os
import json
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from tools import (
    summarize_page,
    tool_extract_tables,
    tool_extract_arguments,
    tool_explore_links,
    map_content_relationships,
    run_agent,
)

# Load .env from repo root (two levels up from server/)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))

app = FastAPI(
    title="AI Mode — Page Intelligence API",
    description="LangChain-powered backend for the Chrome Extension AI Mode POC",
    version="1.0.0",
)

# ── CORS: allow the Chrome extension origin ───────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Chrome extension origins are chrome-extension://...
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response Models ─────────────────────────────────────────────────
class PagePayload(BaseModel):
    url: str
    title: str
    description: Optional[str] = ""
    author: Optional[str] = ""
    publishedDate: Optional[str] = ""
    text: str
    wordCount: Optional[int] = 0
    headings: Optional[list] = []
    links: Optional[list] = []
    tables: Optional[list] = []


class ExploreRequest(BaseModel):
    command: str
    page: PagePayload


class GraphRequest(BaseModel):
    page: PagePayload


class AnalysisResponse(BaseModel):
    summary: str
    key_topics: list[str]
    content_type: str
    reading_time_minutes: float
    sentiment: str


# ── Routes ────────────────────────────────────────────────────────────────────
@app.get("/")
async def health():
    return {"status": "ok", "service": "AI Mode Backend", "version": "1.0.0"}


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_page(payload: PagePayload):
    """
    Auto-invoked when a page loads in the panel.
    Returns a structured summary and metadata.
    """
    if not payload.text and not payload.title:
        raise HTTPException(status_code=400, detail="No page content provided")

    context = _build_context(payload)
    try:
        result = summarize_page(context)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/explore")
async def explore_command(request: ExploreRequest):
    """
    Agentic tool loop — routes the user's natural-language command
    to the appropriate LangChain tool(s).
    """
    context = _build_context(request.page)
    command = request.command.strip()

    try:
        result = run_agent(command=command, context=context, page_data=request.page.model_dump())
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/graph")
async def build_graph(request: GraphRequest):
    """
    Returns D3.js-compatible node/edge graph of content relationships.
    """
    context = _build_context(request.page)
    try:
        graph = map_content_relationships(context, request.page.headings)
        return graph
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Helpers ───────────────────────────────────────────────────────────────────
def _build_context(page: PagePayload) -> str:
    """Assemble a clean text context block from all page fields."""
    parts = [f"URL: {page.url}", f"Title: {page.title}"]

    if page.description:
        parts.append(f"Description: {page.description}")
    if page.author:
        parts.append(f"Author: {page.author}")

    if page.headings:
        headings_text = "\n".join(
            f"{'#' * int(h.get('level', 'h2')[1])} {h.get('text', '')}"
            for h in page.headings
        )
        parts.append(f"\n## Headings\n{headings_text}")

    if page.text:
        # Limit to ~6000 chars to stay within token budget
        parts.append(f"\n## Content\n{page.text[:6000]}")

    if page.tables:
        table_strs = []
        for i, t in enumerate(page.tables[:3]):
            headers = " | ".join(t.get("headers", []))
            rows = "\n".join(
                " | ".join(str(c) for c in row)
                for row in t.get("rows", [])[:8]
            )
            table_strs.append(f"Table {i+1}:\n{headers}\n{rows}")
        parts.append(f"\n## Tables\n" + "\n\n".join(table_strs))

    return "\n\n".join(parts)
