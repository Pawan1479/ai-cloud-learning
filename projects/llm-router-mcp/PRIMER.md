# LLM Router MCP Server: Primer

This project is a small **MCP (Model Context Protocol) server**. MCP is Anthropic's open protocol that
lets apps like Claude Code call external tools. The server exposes one tool per LLM provider, so you
can send a prompt to Claude, Gemini or a local Ollama model from inside a Claude Code session.

```
You ──► Claude Code ──(MCP over stdio)──► server.py ──► Anthropic API
                                                   ├──► Gemini API
                                                   └──► Ollama (localhost:11434)
```

## Project layout

| File | Purpose |
|---|---|
| `server.py` | The MCP server. Each LLM is one Python function plus one entry in `TOOL_FUNCS`. |
| `.env` | API keys (`ANTHROPIC_API_KEY`, `GEMINI_API_KEY`), loaded by `python-dotenv`. |
| `.mcp.json` | Tells Claude Code how to start the server (project scope). |
| `.venv/` | Python virtual environment with `mcp`, `requests`, `python-dotenv`. |

---

## Part 1: Using and switching models

Inside a Claude Code session (started from this folder), ask in plain English. Name the tool and the model:

```
Use local_llm with llama3:latest: explain recursion in two lines
Use local_llm with llama3.2:1b: give me 3 names for a cat
Use anthropic_llm with claude-sonnet-5-5: review this function for bugs ...
Use gemini_llm with gemini-2.5-flash: summarize this paragraph ...
```

To compare models, ask for several at once:

```
Ask the same question to local_llm (llama3:latest) and anthropic_llm (claude-haiku-5-5)
and compare the answers: what is MCP?
```

### Model names you can pass

| Tool | Example `model` values | How to see the full list |
|---|---|---|
| `local_llm` | `llama3:latest`, `llama3.2:1b` | `ollama list` |
| `anthropic_llm` | `claude-opus-5-5` (most capable), `claude-sonnet-5-5` (balanced), `claude-haiku-5-5` (fast/cheap) | `curl -s https://api.anthropic.com/v1/models -H "x-api-key: $ANTHROPIC_API_KEY" -H "anthropic-version: 2023-06-01"` |
| `gemini_llm` | `gemini-2.5-flash`, `gemini-2.5-pro` | `curl -s "https://generativelanguage.googleapis.com/v1beta/models?key=$GEMINI_API_KEY"` |

### Useful commands

| Where | Command | What it does |
|---|---|---|
| Terminal | `claude mcp list` | Shows registered MCP servers and whether they connect |
| Terminal | `claude mcp get llm-router-python` | Shows details for this server |
| Claude Code | `/mcp` | Shows server status and its tools, and lets you reconnect |
| Terminal | `ollama pull mistral` | Downloads another local model, usable immediately with `local_llm` |

> Tip: Adding a new **Ollama** model needs no code change. Run `ollama pull <name>`, then pass that name as `model`.

---

## Part 2: Setting up the server from scratch (step by step)

### Step 1: Clone the repo and create the virtual environment

```bash
git clone https://github.com/Pawan1479/ai-cloud-learning.git
cd ai-cloud-learning/projects/llm-router-mcp
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

### Step 2: Add your API keys to `.env`

```bash
cat > .env <<'EOF'
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=AIza...
EOF
chmod 600 .env
```

- Anthropic key: https://console.anthropic.com/settings/keys
- Gemini key: https://aistudio.google.com/apikey (it normally starts with `AIza`)
- Ollama needs no key. Install it from https://ollama.com, then run `ollama pull llama3`.

### Step 3: Write `server.py`

The server has three parts (see the real file):

1. **Tool functions**: one plain Python function per provider, `def xxx_llm(model, prompt) -> str`.
2. **`TOOL_FUNCS` registry**: maps a tool name to `(function, description)`.
3. **MCP plumbing**: `list_tools()` advertises the tools, `call_tool()` dispatches to the function,
   and `main()` runs the server over stdio.

### Step 4: Check the server outside Claude Code (optional but recommended)

```bash
npx @modelcontextprotocol/inspector .venv/bin/python server.py
```

This opens a web UI where you can list the tools and call them by hand.

### Step 5: Register the server with Claude Code

```bash
cd ai-cloud-learning/projects/llm-router-mcp
claude mcp add llm-router-python --scope project -- \
  $(pwd)/.venv/bin/python $(pwd)/server.py
```

This writes `.mcp.json`:

```json
{
  "mcpServers": {
    "llm-router-python": {
      "command": "/absolute/path/to/llm-router-mcp/.venv/bin/python",
      "args": ["/absolute/path/to/llm-router-mcp/server.py"]
    }
  }
}
```

Scopes:
- `--scope project`: `.mcp.json` in this folder. The server is available only when Claude Code runs here.
- `--scope user`: available in **every** project. Use this if you want the router everywhere.
- `--scope local` (default): only you, only this folder.

### Step 6: Start Claude Code and approve

```bash
cd ai-cloud-learning/projects/llm-router-mcp && claude
```

The first time, Claude Code asks you to approve the project MCP server. Then run `/mcp` to confirm it shows
**connected** with 3 tools.

### Step 7 (optional): Skip the permission prompt on every call

Add this to `.claude/settings.json` in the project:

```json
{
  "permissions": {
    "allow": ["mcp__llm-router-python__*"]
  }
}
```

---

## Part 3: Adding a new LLM later (step by step)

Example: adding **OpenAI**. The same pattern works for any HTTP API.

### Step 1: Add the key to `.env`

```
OPENAI_API_KEY=sk-...
```

### Step 2: Add a function to `server.py` (next to the other tool functions)

```python
def openai_llm(model: str, prompt: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    url = "https://api.openai.com/v1/chat/completions"
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}]
    }
    headers = {"Authorization": f"Bearer {api_key}"}
    res = requests.post(url, json=payload, headers=headers)
    data = res.json()
    try:
        return data["choices"][0]["message"]["content"]
    except:
        return str(data)
```

> Many providers (Groq, Mistral, DeepSeek, OpenRouter, Together) use this **same OpenAI-compatible format**.
> Copy the function and change only the `url`, the env var name and the function name.

### Step 3: Register it in `TOOL_FUNCS`

```python
TOOL_FUNCS = {
    "local_llm": (local_llm, "Run a prompt on a local Ollama model"),
    "gemini_llm": (gemini_llm, "Run a prompt on Gemini"),
    "anthropic_llm": (anthropic_llm, "Run a prompt on Anthropic Claude"),
    "openai_llm": (openai_llm, "Run a prompt on OpenAI"),   # <-- new
}
```

That is all the code you need. `list_tools()` and `call_tool()` pick it up automatically.

### Step 4: Restart the server

Claude Code starts `server.py` once per session, so code changes need a restart:
- In Claude Code: `/mcp`, select `llm-router-python`, then **Reconnect**, or
- Quit and run `claude` again.

### Step 5: Check it

```
/mcp                                   # should now list 4 tools
Use openai_llm with gpt-4o-mini: say hello
```

### Checklist for any new provider

- [ ] Key added to `.env`
- [ ] `xxx_llm(model, prompt) -> str` function written
- [ ] Entry added to `TOOL_FUNCS`
- [ ] Server reconnected (`/mcp`)
- [ ] Test prompt works

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `/mcp` shows **failed** | Run `.venv/bin/python server.py` by hand. Import errors appear immediately (press Ctrl+C to exit). |
| Tool returns `{'error': ... 401 ...}` | Wrong or missing API key in `.env` |
| Tool returns `API_KEY_SERVICE_BLOCKED` (Gemini) | The key is restricted or is not an AI Studio key. Create a new key at aistudio.google.com/apikey. |
| `local_llm` connection refused | Ollama is not running: `ollama serve` |
| Model not found | Check the exact name with `ollama list` or the curl commands above |
| Code changes have no effect | Reconnect the server (Part 3, Step 4) |
| Long answers cut off (Anthropic) | Raise `max_tokens` in `anthropic_llm` (currently 1024) |
