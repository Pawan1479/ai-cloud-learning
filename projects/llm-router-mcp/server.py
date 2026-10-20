import asyncio
import os
import requests
from dotenv import load_dotenv

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

# -------------------------
# Tool implementations
# -------------------------

def local_llm(model: str, prompt: str) -> str:
    url = "http://localhost:11434/api/generate"
    payload = {"model": model, "prompt": prompt, "stream": False}
    res = requests.post(url, json=payload)
    data = res.json()
    return data.get("response", str(data))

def gemini_llm(model: str, prompt: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    res = requests.post(url, json=payload)
    data = res.json()
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except:
        return str(data)

def anthropic_llm(model: str, prompt: str) -> str:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    url = "https://api.anthropic.com/v1/messages"
    payload = {
        "model": model,
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt}]
    }
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01"
    }
    res = requests.post(url, json=payload, headers=headers)
    data = res.json()
    try:
        return data["content"][0]["text"]
    except:
        return str(data)

# -------------------------
# MCP Server
# -------------------------

server = Server("llm-router-python")

TOOL_FUNCS = {
    "local_llm": (local_llm, "Run a prompt on a local Ollama model"),
    "gemini_llm": (gemini_llm, "Run a prompt on Gemini"),
    "anthropic_llm": (anthropic_llm, "Run a prompt on Anthropic Claude"),
}

INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "model": {"type": "string"},
        "prompt": {"type": "string"}
    },
    "required": ["model", "prompt"]
}

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(name=name, description=desc, inputSchema=INPUT_SCHEMA)
        for name, (_, desc) in TOOL_FUNCS.items()
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name not in TOOL_FUNCS:
        result = f"Unknown tool: {name}"
    else:
        func = TOOL_FUNCS[name][0]
        result = await asyncio.to_thread(func, arguments["model"], arguments["prompt"])
    return [TextContent(type="text", text=result)]

# -------------------------
# Start server
# -------------------------

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
