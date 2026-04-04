#!/usr/bin/env python3
import asyncio
import json
import os
from aiohttp import web
from dotenv import load_dotenv

from mcp.server import Server
from mcp.types import (
    Tool,
    TextContent,
    Resource,
    EmbeddedResource,
    CallToolResult,
    ReadResourceResult,
    TextResourceContents,
    ServerCapabilities,
    ResourcesCapability,
    ToolsCapability,
)
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server

# Load environment variables
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
load_dotenv(env_path)

POC_PORT = int(os.getenv("MCP_POC_PORT", 1337))
STATE_FILE = os.path.join(os.path.dirname(__file__), "state.json")

def load_state():
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except:
        return {"username": "Scout", "missions": 12, "success_rate": 85, "status": "Ready"}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

# Initialize the MCP Server
server = Server("scout-interactive-poc")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="get_scout_dashboard",
            description="Returns an interactive dashboard for the AI Scout system.",
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {"type": "string", "description": "The user's name to personalize the dashboard."},
                },
                "required": ["username"],
            },
        ),
        Tool(
            name="update_scout_stats",
            description="Updates the scout dashboard state. This immediately updates the Live View.",
            inputSchema={
                "type": "object",
                "properties": {
                    "missions": {"type": "integer", "description": "The total number of missions."},
                    "success_rate": {"type": "integer", "description": "The success rate percentage (0-100)."},
                    "status": {"type": "string", "description": "Short status message for the scout."},
                    "username": {"type": "string", "description": "Optionally update the username."}
                },
                "required": ["missions", "success_rate"],
            },
        )
    ]

@server.list_resources()
async def handle_list_resources() -> list[Resource]:
    """List available UI resources."""
    return [
        Resource(
            uri="ui://scout/dashboard",
            name="Scout Interactive Dashboard",
            description="An interactive interface for managing AI Scout missions.",
            mimeType="text/html;profile=mcp-app",
        )
    ]

def get_html_content():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; padding: 20px; background: #f4f6f8; color: #333; }
            .card { background: white; border-radius: 12px; padding: 24px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); max-width: 500px; margin: auto; }
            h1 { color: #2c3e50; font-size: 1.5rem; margin-top: 0; }
            .stat-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin: 20px 0; }
            .stat { background: #eef2f7; padding: 12px; border-radius: 8px; text-align: center; }
            .stat-val { font-size: 1.2rem; font-weight: bold; color: #3498db; }
            .btn { background: #3498db; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; width: 100%; transition: 0.2s; }
            .btn:hover { background: #2980b9; }
            .status { margin-top: 15px; font-size: 0.9rem; color: #666; text-align: center; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>AI Scout Dashboard</h1>
            <p>Welcome back, <span id="username">Scout</span>! Here's your current status:</p>
            <div class="stat-grid">
                <div class="stat">
                    <div class="stat-val" id="missions">--</div>
                    <div>New Missions</div>
                </div>
                <div class="stat">
                    <div class="stat-val" id="success_rate">--%</div>
                    <div>Success Rate</div>
                </div>
            </div>
            <button class="btn" onclick="alert('Mission processing started!')">⚡ Scan for New Signals</button>
            <div class="status" id="status">Status: Loading...</div>
        </div>
        <script>
            // Live View Polling
            async function fetchState() {
                try {
                    const response = await fetch('/state');
                    const data = await response.json();
                    document.getElementById('username').innerText = data.username;
                    document.getElementById('missions').innerText = data.missions;
                    document.getElementById('success_rate').innerText = data.success_rate + '%';
                    document.getElementById('status').innerText = 'Status: ' + data.status;
                } catch (e) {
                    console.log('Error fetching state', e);
                }
            }
            // Fetch immediately and then poll every 2 seconds
            fetchState();
            setInterval(fetchState, 2000);
            
            // Final compatibility 'Ready' Signal to Host (for MCP compatibility)
            window.onload = function() {
                if (window.parent) {
                    console.log('Sending ready signal to host...');
                    window.parent.postMessage({ type: 'mcp-app-ready' }, '*');
                    window.parent.postMessage({ type: 'ready' }, '*');
                }
            };
        </script>
    </body>
    </html>
    """

@server.read_resource()
async def handle_read_resource(uri: str) -> ReadResourceResult:
    """Read the UI resource and return the HTML content."""
    if uri == "ui://scout/dashboard":
        return ReadResourceResult(
            contents=[
                TextResourceContents(
                    uri=uri,
                    mimeType="text/html;profile=mcp-app",
                    text=get_html_content()
                )
            ]
        )
    raise ValueError(f"Resource not found: {uri}")

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> dict:
    """Handle tool calls with broad compatibility metadata."""
    if name == "get_scout_dashboard":
        username = arguments.get("username", "Scout")
        
        # Update state username
        state = load_state()
        state["username"] = username
        save_state(state)
        
        ui_metadata = {
            "uri": "ui://scout/dashboard",
            "resourceUri": "ui://scout/dashboard",
            "mimeType": "text/html;profile=mcp-app",
            "autoResize": True
        }
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Opening the interactive Scout Dashboard for {username}... Check http://localhost:{POC_PORT}/dashboard for the Live View if inline rendering fails.",
                }
            ],
            "isError": False,
            "meta": {"ui": ui_metadata},
            "_meta": {"ui": ui_metadata}
        }
    elif name == "update_scout_stats":
        state = load_state()
        if "missions" in arguments:
            state["missions"] = arguments["missions"]
        if "success_rate" in arguments:
            state["success_rate"] = arguments["success_rate"]
        if "status" in arguments:
            state["status"] = arguments["status"]
        if "username" in arguments:
            state["username"] = arguments["username"]
        save_state(state)
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Scout stats updated successfully! Missions: {state['missions']}, Success Rate: {state['success_rate']}%. Open http://localhost:{POC_PORT}/dashboard to see the Live View.",
                }
            ],
            "isError": False
        }
    raise ValueError(f"Tool not found: {name}")

# Web Server Handlers
async def get_state_handler(request):
    return web.json_response(load_state())

async def serve_dashboard(request):
    return web.Response(text=get_html_content(), content_type='text/html')

async def main():
    # Define custom capabilities to advertise UI support
    capabilities = ServerCapabilities(
        tools=ToolsCapability(listChanged=True),
        resources=ResourcesCapability(subscribe=True, listChanged=True),
        experimental={
            "io.modelcontextprotocol/ui": {}
        }
    )
    
    init_options = InitializationOptions(
        server_name="scout-interactive-poc",
        server_version="1.27.0",
        capabilities=capabilities
    )

    # Start the aiohttp web server in the background
    app = web.Application()
    app.add_routes([
        web.get('/state', get_state_handler), 
        web.get('/dashboard', serve_dashboard)
    ])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', POC_PORT)
    await site.start()

    # Run the server using stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            init_options,
        )

if __name__ == "__main__":
    asyncio.run(main())
