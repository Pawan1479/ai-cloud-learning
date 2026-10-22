import asyncio
import os

import requests
from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

# Seconds to wait for a reply. Local models on a laptop can be slow, so they get longer.
LOCAL_TIMEOUT = 120
API_TIMEOUT = 60


class ToolError(Exception):
    """A problem worth showing to the user as a plain message (bad key, provider down, ...)."""


# -------------------------
# Helpers
# -------------------------

def require_key(name: str) -> str:
    key = os.getenv(name)
    if not key:
        raise ToolError(f"{name} is not set. Add it to .env (see .env.example).")
    return key

def post_json(provider: str, url: str, payload: dict, headers: dict | None = None,
              timeout: int = API_TIMEOUT) -> dict:
    try:
        res = requests.post(url, json=payload, headers=headers, timeout=timeout)
    except requests.Timeout:
        raise ToolError(f"{provider} did not reply within {timeout} seconds.")
    except requests.ConnectionError:
        raise ToolError(f"Could not connect to {provider}. Is it running and reachable?")
    except requests.RequestException as e:
        raise ToolError(f"{provider} request failed: {e.__class__.__name__}")

    try:
        data = res.json()
    except ValueError:
        raise ToolError(f"{provider} returned a non-JSON reply (HTTP {res.status_code}).")

    if not res.ok:
        # Providers put the reason in different places; fall back to the status code.
        error = data.get("error", {}) if isinstance(data, dict) else {}
        message = error.get("message") if isinstance(error, dict) else error
        raise ToolError(f"{provider} error (HTTP {res.status_code}): {message or 'no details'}")
    return data

# -------------------------
# Tool implementations
# -------------------------

def local_llm(model: str, prompt: str) -> str:
    url = "http://localhost:11434/api/generate"
    payload = {"model": model, "prompt": prompt, "stream": False}
    data = post_json("Ollama", url, payload, timeout=LOCAL_TIMEOUT)
    if "response" not in data:
        raise ToolError(f"Unexpected reply from Ollama: {data}")
    return data["response"]

def gemini_llm(model: str, prompt: str) -> str:
    # The key goes in a header, not the URL, so it never shows up in logs or error messages.
    headers = {"x-goog-api-key": require_key("GEMINI_API_KEY")}
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    data = post_json("Gemini", url, payload, headers=headers)
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError):
        raise ToolError(f"Unexpected reply from Gemini: {data}")

def anthropic_llm(model: str, prompt: str) -> str:
    url = "https://api.anthropic.com/v1/messages"
    payload = {
        "model": model,
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt}]
    }
    headers = {
        "Content-Type": "application/json",
        "x-api-key": require_key("ANTHROPIC_API_KEY"),
        "anthropic-version": "2023-06-01"
    }
    data = post_json("Anthropic", url, payload, headers=headers)
    try:
        return data["content"][0]["text"]
    except (KeyError, IndexError, TypeError):
        raise ToolError(f"Unexpected reply from Anthropic: {data}")

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
        try:
            result = await asyncio.to_thread(func, arguments["model"], arguments["prompt"])
        except ToolError as e:
            result = f"Error: {e}"
    return [TextContent(type="text", text=result)]

# -------------------------
# Start server
# -------------------------

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
