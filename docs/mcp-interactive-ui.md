# MCP Interactive UI Integration

This document records the architectural findings and implementation details for integrating interactive Model Context Protocol (MCP) tools into the AI Scout project.

## 📁 POC Documentation
- **Location**: `pocs/mcp-interactive-tool/`
- **Main Script**: `main.py`
- **Detailed Findings**: [learnings.md](../pocs/mcp-interactive-tool/learnings.md)
- **Walkthrough**: [walkthrough.md](../pocs/mcp-interactive-tool/walkthrough.md)

---

## 🛠️ Implementation Summary
Successfully built a Python-based MCP server that implements the "MCP Apps" extension standard for interactive UIs.

### Key technical wins:
- Developed a protocol-compliant `stdio` server using the `mcp[official]` SDK.
- Overcame Windows "Packaged App" configuration hurdles by identifying the correct `AppData\Local\Packages` path for Claude Desktop.
- Implemented a "Shotgun" compatibility metadata schema (`meta` + `_meta`) to ensure tool call responses are recognized by all current MCP host versions.
- Added an out-of-band **Hybrid Mode** architecture: Running an `aiohttp` web server (on port `1337`) asynchronously alongside the MCP `stdio` server to provide an unblocked visualization fallback.

## ⚠️ Rendering Hurdle & 🚀 Hybrid Resolution
During testing with the **Packaged** version of Claude Desktop (Windows Store install), the server successfully connected and the tool call was recognized, but the UI widget failed to render inline.

**Finding**: The model (Claude) explicitly responded: *"The Claude.ai web chat interface does not currently render MCP app UIs inline."* This suggested the packaged host restricts internal `iframe` sandboxing.

**Resolution (Hybrid Mode)**: 
To bypass the host's UI block, we attached a lightweight `aiohttp` Web Server to the MCP Python application. 
- Claude calls tools (e.g. `update_scout_stats`) via MCP to mutate a local `state.json` file.
- The user views the dashboard via `localhost:1337/dashboard` in a standard browser.
- The browser natively polls `state.json`, visualizing the LLM's agentic actions securely and in real-time.

---

## 🚀 Next Steps for Production
- **Enterprise Shell**: To use these interactive UIs in a production "Scout" environment, we recommend using a standard (non-packaged) Claude Desktop installation or a custom MCP host shell.
- **Workflow Integration**: Once the host environment is confirmed, the `get_scout_dashboard` tool can be integrated into the main n8n Scout workflow to provide graphical summaries of daily findings.
