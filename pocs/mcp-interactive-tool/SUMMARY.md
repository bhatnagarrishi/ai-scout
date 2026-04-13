# SUMMARY: Interactive MCP Tool

## 🎯 Objective
This POC explores the Model Context Protocol (MCP) and its ability to bridge the gap between AI models and graphical interfaces. The goal was to build a tool that doesn't just return text, but allows an LLM to "drive" a live, interactive dashboard within a host application (like Claude Desktop).

## 🏗️ Architecture
The project implements a **Hybrid MCP/HTTP Architecture**:
1.  **MCP Stdio Server**: Handles the direct communication with the AI model, allowing it to call tools that modify system state.
2.  **AIOHTTP Background Server**: Serves a dynamic HTML/JS dashboard on a local port.
3.  **State Bridge**: A `state.json` file that acts as the "source of truth." The model updates the JSON via MCP tools, and the web dashboard polls the JSON to refresh its UI in real-time.
4.  **MIME & Metadata**: Uses the `text/html;profile=mcp-app` MIME type and `_meta` extensions to signal graphical capabilities to the host.

## ✅ Success Metrics
*   **Agentic UI Control**: Successfully demonstrated an LLM updating a complex dashboard graph simply by "deciding" to call a state-mutation tool.
*   **Windows Packaging Workaround**: Discovered and documented the specific sandboxed paths required for MCP configuration in the MSIX-packaged version of Claude Desktop.
*   **Dual-Server Persistence**: Proved that an MCP server can safely run a concurrent HTTP server without port conflicts or lifecycle crashes.
