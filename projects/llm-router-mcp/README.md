# 🔀 LLM Router MCP Server

> One MCP server that lets Claude Code route prompts to **Anthropic Claude**, **Google Gemini** or a **local Ollama** model.

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![MCP SDK](https://img.shields.io/badge/mcp-1.1.0-6E56CF)](https://pypi.org/project/mcp/)
[![Ollama](https://img.shields.io/badge/Ollama-local-000000?logo=ollama&logoColor=white)](https://ollama.com/)

## ✨ What it does

The [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) is an open protocol that lets AI apps such as Claude Code call external tools. This server exposes one tool per LLM provider:

| Tool | Provider | Cost |
|---|---|---|
| `local_llm` | Ollama on `localhost:11434` (e.g. `llama3`, `llama3.2:1b`) | Free; runs on your machine |
| `gemini_llm` | Google Gemini API | Pay-per-use (free tier available) |
| `anthropic_llm` | Anthropic Claude API | Pay-per-use |

```
You ──► Claude Code ──(MCP over stdio)──► server.py ──► Anthropic API
                                                   ├──► Gemini API
                                                   └──► Ollama (localhost:11434)
```

## 🏗️ How it works

`server.py` has three parts:

1. **Tool functions**: one plain function per provider, `xxx_llm(model, prompt) -> str`
2. **`TOOL_FUNCS` registry**: maps each tool name to its function and description
3. **MCP plumbing**: `list_tools()` advertises the tools, `call_tool()` dispatches, `main()` serves over stdio

Adding a provider takes one function and one registry entry. See [PRIMER.md, Part 3](PRIMER.md#part-3-adding-a-new-llm-later-step-by-step).

## ⚡ Quick start

**Prerequisites:** Python 3.10+, [Ollama](https://ollama.com/) (for `local_llm`), [Claude Code](https://claude.com/claude-code)

```bash
git clone https://github.com/Pawan1479/ai-cloud-learning.git
cd ai-cloud-learning/projects/llm-router-mcp

python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

cp .env.example .env              # add your API keys (only needed for the paid tools)
chmod 600 .env

ollama pull llama3                # a free local model
```

Register the server with Claude Code (this writes `.mcp.json`):

```bash
claude mcp add llm-router-python --scope project -- \
  "$(pwd)/.venv/bin/python" "$(pwd)/server.py"
```

Start Claude Code in this folder, approve the server, then run `/mcp` to check that it shows **connected**.

## 💬 Usage

Ask in plain English inside Claude Code:

```
Use local_llm with llama3: explain recursion in two lines
Use gemini_llm with gemini-2.5-flash: summarize this paragraph ...
Ask local_llm (llama3) and anthropic_llm (claude-haiku-5-5) the same question and compare: what is MCP?
```

## 🔐 Security and cost controls

- API keys live in `.env`, which is **gitignored**. Only `.env.example` is committed.
- [`.claude/settings.json`](.claude/settings.json) **allows** the free `local_llm` tool without prompting and **always asks** before the paid `gemini_llm` and `anthropic_llm` tools.

## 📚 What I learned

- How MCP servers talk to clients over **stdio** using JSON-RPC
- The difference between a **Claude subscription** (Claude Code usage) and **API billing** (per-token)
- Ollama streams NDJSON by default, so `"stream": false` is needed for a single JSON response
- Claude Code permission rules (`allow` / `ask`) for controlling tool usage

## 🛣️ Next steps

- [ ] Add OpenAI-compatible providers (Groq, Mistral, OpenRouter)
- [ ] Add a `compare_llms` tool that fans one prompt out to several models
- [ ] Add timeouts, retries and clearer error messages
- [ ] Add unit tests

📘 **Full guide:** [PRIMER.md](PRIMER.md) covers setup from scratch, switching models, adding providers and troubleshooting.
