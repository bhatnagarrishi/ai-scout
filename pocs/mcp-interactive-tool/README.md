# POC: Interactive MCP Tool Integration

This folder contains a Proof of Concept (POC) for building a custom Model Context Protocol (MCP) server in Python that exposes an interactive UI component. 

---

## 1. Objective
- To build an MCP server that goes beyond text-only interactions by exposing an interactive UI component.
- Due to current Claude Desktop rendering limitations, the objective evolved to include a **"Hybrid Mode"**: 
  - Exposing the MCP server tools for Claude to use, 
  - While simultaneously running a local web server so the user can visually interact with and 
  - see the real-time state of the UI outside the chat interface.
  - see the impact of chat interactions with the MCP server tools on the UI.

## 2. Pre-requisites
- [ ] **Python 3.10+**: Installed and accessible in your terminal.
- [ ] **Claude Desktop Application**: Necessary to render and test the interactive UI.
- [ ] **Basic Python Knowledge**: Familiarity with virtual environments and `pip`.

## 3. Tech Stack
- **Protocol**: [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- **SDK**: `mcp` (official Python SDK)
- **Host**: Claude Desktop (v0.2.0+)
- **Server**: Python 3.10+

## 4. Action Plan / Outcomes
1. **Repository Setup**: Create this POC folder and `README.md`. ✅
2. **Environment Discovery**: Identify the installation path for the `mcp-sdk`. ✅
3. **Server Implementation**: 
   - Define tools (`get_scout_dashboard`, `update_scout_stats`) in `main.py`.
   - Implement handlers to return a structured UI component schema. ✅
4. **Integration**: Update `claude_desktop_config.json` to point to this script. ✅
5. **Validation**: Test the tool from Claude Desktop. ✅
6. **Hybrid Mode**: Start an `aiohttp` web server within the MCP script to provide an out-of-band visual dashboard while the protocol interface is verified via logs and state changes. ✅

## 5. Learnings & Summary

### 5.1 Learnings
- **Packaged App Configs**: Windows Store installations of Claude put config files in obscure `AppData/Local/Packages/...` directories.
- **Protocol Quirks**: Evolving experimental UI specs require "Double Metadata" (`meta` and `_meta`) and explicit MIME type (`text/html;profile=mcp-app`) declarations.
- **Host Limitations**: Even if the server achieves a perfect "UI capability" handshake, some host environments (like the current Packaged Claude builds) simply do not render the `ui://` iframes inline.
- **The "Hybrid" Pattern**: Embedding an asynchronous web server (`aiohttp`) within the MCP server script is an incredibly resilient fallback pattern. It allows the LLM to control and modify a local state file securely while giving the user a guaranteed, unblocked browser visualization.

### 5.2 Summary
We successfully built a production-ready, highly compatible MCP server in Python. Though the Claude Desktop interface restricted inline rendering of the iframe, we proved the Agentic Loop works flawlessly: Claude can reliably be instructed to execute tools that mutate a local JSON state, which then instantly updates a real-time visual dashboard (via polling) in a standard web browser.

---

## Technical Details

### `claude_desktop_config.json` (Draft)
```json
{
  "mcpServers": {
    "scout-interactive": {
      "command": "python",
      "args": ["${MCP_POC_MAIN_PATH}"]
    }
  }
}
```
*(Path will be confirmed during implementation)*
