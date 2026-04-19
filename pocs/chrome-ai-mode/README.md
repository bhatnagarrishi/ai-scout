# POC: Chrome Extension — AI Mode

> **Mission**: Prove that a Chrome Extension + local LLM backend can transform any webpage from passive content into an interactive, agentic experience — summarizing, reasoning over, and visualizing page structure on demand.

---

## 🎯 The Goal: Agentic Page Intelligence

Most browser AI tools treat a webpage as a static blob of text. This POC builds a **reasoning side panel** that:

1. **Auto-analyzes** the current page on load (title, headings, paragraphs, links, tables)
2. **Lets you issue commands** via chips — "Summarize", "Extract Tables", "Map Arguments", "Explore Links", "Visualize"
3. **Runs an agentic tool loop** via LangGraph ReAct agent to answer commands with the right tool
4. **Visualizes** content relationships as a live D3.js force-directed graph
5. **Stays open** as you browse — re-analyzes on each navigation automatically

## 🏗️ Architecture

```
Chrome Extension (Manifest V3 — no build step required)
  ├── content.js       — DOM extraction at document_idle
  │                      (headings, paragraphs, links, tables, OG meta)
  ├── background.js    — Service worker; routes to local backend
  │                      caches results in chrome.storage.session
  └── sidepanel/       — Dark glassmorphism panel UI
      ├── panel.html   — Two-zone layout: collapsible summary + chat
      ├── panel.css    — Inter font, indigo accent, animated orb
      └── panel.js     — Chat loop, command chips, D3.js force graph
              ↕  HTTP POST (localhost:8000)
FastAPI + LangGraph Backend (Python)
  ├── server.py        — /analyze, /explore, /graph endpoints + CORS
  └── tools.py         — LangGraph ReAct agent + 4 LangChain tools:
                          tool_extract_tables
                          tool_extract_arguments
                          tool_explore_links
                          tool_custom_query
                         + map_content_relationships (D3 graph builder)
                         + summarize_page (structured JSON summary)
```

## 🛠️ Setup

### Prerequisites
- Python 3.x with the repo-root `.venv` activated
- `OPENAI_API_KEY` set in root `.env` file (uses `gpt-4o-mini`)
- Chrome browser

### 1. Start the Python backend

```powershell
# From the POC root directory
cd pocs\chrome-ai-mode
.\start_server.ps1
```

This will activate the root `.venv`, install dependencies, and launch the FastAPI server at `http://localhost:8000`.

**Note:** Uses the `&` operator with an absolute python path to avoid PowerShell module loading issues with relative `.venv` paths.

### 2. Load the Chrome Extension

1. Open Chrome → navigate to `chrome://extensions`
2. Enable **Developer mode** (top-right toggle)
3. Click **"Load unpacked"**
4. Select the `extension/` folder inside this POC directory
5. The AI Mode icon appears in the toolbar — pin it via the 🧩 puzzle icon if needed

### 3. Use It

1. Navigate to any webpage (news articles and Wikipedia work best)
2. Click the **AI Mode** icon in the Chrome toolbar
3. The side panel opens and auto-analyzes the page within ~3 seconds
4. Use chips or type freely in the chat box

## 🧪 Command Chips

| Chip | Command Sent | Tool Used |
|------|-------------|-----------|
| 📝 Summarize | "Give me a concise 3-point summary" | `tool_custom_query` |
| 📊 Tables | "Extract all data tables" | `tool_extract_tables` |
| 🧠 Arguments | "What are the main claims?" | `tool_extract_arguments` |
| 🔗 Links | "Categorize the links" | `tool_explore_links` |
| 🕸️ Visualize | Calls `/graph` endpoint | `map_content_relationships` + D3.js |

## 💬 Panel UI Layout

```
┌─────────────────────────────┐
│ 🔵 AI Mode          [READY] │  ← Header (sticky)
├─────────────────────────────┤
│ NEWS ARTICLE · 4.5min · 😊  │  ← Page meta row (always visible)
│ ▼ Title of the page         │  ← Collapsible body (click meta to toggle)
│   Summary text here...      │
│   [tag1] [tag2] [tag3]      │
├─────────────────────────────┤
│ [📝 Summ] [📊 Tbl] [🧠 Arg] │  ← Command chips
│ [🔗 Links] [🕸️ Vis]         │
├─────────────────────────────┤
│ • AI message                │  ← Chat area (flex: 1, expands when
│ • User message              │    summary is collapsed)
│ • AI response...            │
├─────────────────────────────┤
│ Ask anything about this…  ➤ │  ← Always-visible chat input
└─────────────────────────────┘
```

## 📁 File Structure

```
chrome-ai-mode/
├── README.md              ← This file
├── LEARNINGS.md           ← Build notes, bugs found, fixes
├── SUMMARY.md             ← Post-run summary (TBD)
├── start_server.ps1       ← Backend launcher (activates venv, runs uvicorn)
├── extension/
│   ├── manifest.json      ← MV3: sidePanel, activeTab, scripting, storage
│   ├── background.js      ← Service worker: tab events, API routing, cache
│   ├── content.js         ← DOM extraction + SPA navigation detection
│   ├── icons/
│   │   ├── icon16.png
│   │   ├── icon48.png
│   │   └── icon128.png
│   └── sidepanel/
│       ├── panel.html     ← Two-zone layout HTML
│       ├── panel.js       ← Chat, command dispatch, D3.js graph
│       └── panel.css      ← Dark glassmorphism, animated orb, flex layout
└── server/
    ├── server.py          ← FastAPI app with CORS
    ├── tools.py           ← LangGraph agent + tools
    └── requirements.txt   ← Backend deps (with actual installed versions)
```

## ⚠️ Known Gotchas

1. **PowerShell + relative venv path**: Use `& "C:\..\.venv\Scripts\python.exe"` — do not use `uvicorn` directly
2. **LangChain ≥1.0 API change**: `create_tool_calling_agent` removed; use `langgraph.prebuilt.create_react_agent`
3. **Shared venv conflicts**: Use `>=` version pins, not `==` pinned versions
4. **Restricted pages**: Extension cannot inject into `chrome://`, `chrome-extension://`, or PDF pages

## 🧠 Why This Matters for AI Scout

This POC proves we can build a **companion browser layer** on top of any page a user visits — identical LangChain tool patterns can feed back into Scout's article scoring pipeline. A user reading a page flagged by Scout could click "Verify Claims" and get AI-powered cross-referencing in seconds.
