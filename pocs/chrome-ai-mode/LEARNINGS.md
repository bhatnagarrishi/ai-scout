# LEARNINGS — Chrome Extension AI Mode POC

> Live notes captured during build and iteration. Updated after each meaningful session.

---

## 🧪 Run Log

### Session 1 — 2026-04-19: Initial build + first successful run

**Result:** ✅ Extension installed, side panel renders, backend `/analyze` endpoint returns structured JSON from a live page (CNN, CMU).

---

## 📌 Pre-Build Anticipated Challenges (vs. Reality)

| Anticipated | What Actually Happened |
|---|---|
| MV3 service worker killed after 30s | ✅ Mitigated by caching in `chrome.storage.session` |
| CSP blocking CDN scripts in side panel | ✅ Non-issue — `<script src>` tag for D3.js works fine in side panel context |
| CORS extension → localhost | ✅ Fixed by setting `allow_origins=["*"]` in FastAPI CORS middleware |
| DOM extraction quality | ✅ Semantic selectors (`article`, `main`, `p`) worked well on news pages |

---

## 🔥 Actual Surprises & Bugs Found

### 1. LangChain API: `create_tool_calling_agent` was removed

**What happened:** The plan called for `langchain.agents.create_tool_calling_agent` and `AgentExecutor`. These were removed in newer LangChain versions (≥1.0).

**Fix:** Migrated to `langgraph.prebuilt.create_react_agent` — the modern replacement. The agent is now a LangGraph ReAct loop rather than a classic LangChain executor.

```python
# OLD (broken)
from langchain.agents import create_tool_calling_agent, AgentExecutor

# NEW (correct)
from langgraph.prebuilt import create_react_agent
agent = create_react_agent(llm, tools, prompt=system_prompt)
result = agent.invoke({"messages": [HumanMessage(content=command)]})
```

### 2. PowerShell relative path syntax for executables

**What happened:** Running `.venv\Scripts\python.exe` fails in PowerShell — it tries to load it as a module.

**Fix:** Always use the `&` call operator with absolute paths:
```powershell
& "C:\path\to\.venv\Scripts\python.exe" -m uvicorn server:app ...
# or use Resolve-Path / Join-Path to build the path dynamically
```

> This is baked into `start_server.ps1` using `Join-Path $Root ".venv\Scripts\python.exe"`.

### 3. Shared venv version conflicts

**What happened:** Initially pinned exact versions (e.g., `fastapi==0.115.0`). These conflicted with `pydantic-ai`, `mcp`, and `langchain-google-genai` already in the shared venv.

**Fix:** Use minimum version pins (`>=`) so pip picks whatever satisfies all packages:
```
fastapi>=0.100.0
langchain>=0.3.0
```

**What installed:** `fastapi==0.136.0`, `langchain==1.2.15`, `openai==2.31.0`.

### 4. Panel layout — chat input hidden below the fold

**What happened:** The page summary card was tall and the body used `min-height: 100vh` without overflow containment. The chat input scrolled off-screen.

**Fix:** Restructured into two zones:
- `top-scroll-area`: `flex: 0 1 auto; max-height: 45vh; overflow-y: auto` — scrollable, caps at 45% of panel height
- `chat-section`: `flex: 1` — fills all remaining height automatically

### 5. Collapse doesn't reclaim space

**What happened:** After collapsing the page card, a large dead space appeared in the middle. The `chat-section` had `flex-shrink: 0` and a fixed `max-height: 55vh`, so it didn't expand.

**Fix:** Removed `max-height` from chat-section and set `flex: 1`. Now when the top area collapses, the chat panel grows to fill the freed space.

### 6. Server import names mismatch

**What happened:** `server.py` imported `extract_tables`, `extract_key_arguments`, `explore_links` but `tools.py` exported them as `tool_extract_tables`, `tool_extract_arguments`, `tool_explore_links`.

**Fix:** Updated `server.py` imports to use the `tool_` prefix — or removed unused direct imports since the agent calls tools internally.

---

## 📚 Key Architectural Insights

- **Side Panel vs. Popup**: Side panels persist across navigation — they don't close when the user clicks away, making them ideal for a companion AI layer. Use `chrome.sidePanel.open()` from the background worker.
- **Content Script SPA Support**: Patching `history.pushState` and `history.replaceState` is required to catch navigation in SPAs (React, Next.js sites) where no full page reload occurs.
- **LangGraph ReAct agent** selects tools automatically based on the command. No need to manually route commands to specific tools — the LLM decides which tool fits.
- **`chrome.storage.session`** (not `localStorage` or `chrome.storage.local`) is the right cache for tab-scoped data — it's fast, isolated per session, and doesn't require async indexedDB.

---

## 🔮 Next Improvements

- [ ] Streaming responses from backend to avoid long wait times during analysis
- [ ] Add a "re-analyze" button to re-trigger extraction without full reload
- [ ] Persist chat history per URL using `chrome.storage.local`
- [ ] Add a "copy to clipboard" icon on AI responses
- [ ] Test on more page types: PDFs (via PDF.js), YouTube pages, paywalled articles
