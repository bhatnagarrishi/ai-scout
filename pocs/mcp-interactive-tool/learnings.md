# Learnings: Interactive MCP Tool POC

This document captures the hurdles, solutions, and key insights gained while building the Interactive MCP Tool integration (Issue #51).

---

## 1. Environment & Configuration Challenges

### 🚨 Packaged App Config Path (Windows)
- **Issue**: Standard documentation points to `%APPDATA%\Claude\claude_desktop_config.json`. However, if Claude is installed via the Microsoft Store or as a packaged MSIX, the configuration file is actually located in a sandboxed directory:
  - `c:\Users\<user>\AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude_desktop_config.json`
- **Solution**: Use the **"Edit Config"** button in **Settings > Developer** within Claude Desktop to find the active file path.
- **Permission hurdle**: Re-writing this file from an external agent (like Antigravity) may be blocked by the OS sandbox, requiring a manual copy-paste.

### 🐍 Python Pathing on Windows
- **Issue**: Using a generic `"command": "python"` in the JSON config can fail if the environment variable points to a Windows store "execution alias" (shim) that isn't the real interpreter.
- **Solution**: Use the absolute, direct path to the python executable:
  - `C:/Users/<your_username>/AppData/Local/Programs/Python/Python313/python.exe`

---

## 2. Model Context Protocol (MCP) Implementation

### 📐 Schema Mismatch & Capability Handshake
- **Issue**: Even with correct JSON, the dashboard didn't render. 
- **Cause 1 (MIME Type)**: Claude Desktop requested `text/html;profile=mcp-app`, but the server provided `text/html`.
- **Cause 2 (Handshake)**: The server was not advertising the `io.modelcontextprotocol/ui` capability during the initial `initialize` request.
- **Cause 3 (Metadata Keys)**: Different host versions expect `meta` vs `_meta` or `uri` vs `resourceUri`.
- **Cause 4 (Ready Signal)**: Some sandboxed iframes require a `postMessage` from the child to the parent to signal that the UI is loaded and ready to be displayed.
- **Solution**:
  - Update resource MIME types to match exactly: `text/html;profile=mcp-app`.
  - Manually define `ServerCapabilities` in the Python SDK.
  - Provide "Double Metadata" (both `meta` and `_meta`).
  - Add `window.parent.postMessage({ type: 'ready' }, '*')` to the HTML.

### 🧩 MCP Apps / UI Metadata & Client Rendering
- **Issue**: Standard MCP tools return text. To trigger a graphical UI, you must use the `_meta` extension.
- **Insight**: Tool responses should include a `_meta` field pointing to the `resourceUri` of the UI component. Use `CallToolResult` to wrap this properly.
## 3. The "Hybrid Mode" Workaround
- **Observation**: Even when the model (Claude) correctly recognizes the UI response (`uri`, `mimeType`), the host interface may still fail to render the widget inline. Claude itself confirmed that *some* versions (like the Packaged Windows App) block the `ui://` scheme iframe from visibly rendering.
- **Solution (Hybrid Pattern)**: To prove the agentic loop still works perfectly, we implemented a **Hybrid Architecture**:
  1. The MCP `stdio_server` runs to communicate with Claude.
  2. An `aiohttp` web server runs concurrently in the background (on port 1337).
  3. A `state.json` file bridges the gap. Claude executes MCP tools to mutate `state.json`.
  4. The web server serves the HTML dashboard on `http://localhost:1337/dashboard`, which relies on simple JavaScript polling to fetch the newest data from `state.json` and updates the UI instantly.
- **Client Diagnostic**: 

---

## 4. Final Architecture Snapshot
- **Server**: Python 3.13 + `mcp` SDK
- **Web App Server**: `aiohttp` (runs alongside MCP)
- **Transport**: `stdio` (for MCP) and TCP HTTP (for standard Browser)
- **Metadata Keys**: Both `meta` and `_meta` (for maximum MCP capability compatibility)
- **MIME Type**: `text/html;profile=mcp-app`
- **Signal**: `window.parent.postMessage({ type: 'ready' }, '*')` added to HTML (to appease strict hosts).

---

## 5. Workflow Insights
- **Icon Visibility**: The 🧩 (puzzle) or 🛠️ (wrench) icon in the chat bar is the single most reliable indicator that the server is successfully connected.
- **System Tray Restart**: "Closing" the Claude window isn't enough to reload the config—you must **Quit** it from the system tray and relaunch.
- **Phantom Ports**: Because the MCP Server handles its lifecycle via Claude, if Claude doesn't properly kill the MCP script on exit, the `aiohttp` port (`1337`) may remain blocked on restart.

---

## 6. Unresolved / Open Questions
- Can the UI communicate back to the model for multi-step "looping" workflows natively?
- What are the performance implications of loading large JavaScript bundles into the Claude iframe?
