# 📓 Learning Log

Short, dated notes on what I learned. Newest first.

---

## 2026-10-20: Building my first MCP server

**Project:** [LLM Router MCP Server](../projects/llm-router-mcp/)

- **MCP (Model Context Protocol)** lets AI apps like Claude Code call external tools. A server advertises tools (`list_tools`) and runs them (`call_tool`), talking JSON-RPC over stdio.
- Claude Code finds project MCP servers in **`.mcp.json`** (key `mcpServers`) and asks you to approve them the first time.
- **Ollama** streams responses as NDJSON by default; send `"stream": false` to get one JSON object back.
- **Subscription vs API:** a Claude Pro plan covers Claude Code usage; direct API calls with an API key are billed separately per token.
- **Permission rules** in `.claude/settings.json` (`allow` / `ask`) control which tools run without a prompt. That's useful for guarding paid APIs.
- **Secrets hygiene:** keep keys in a gitignored `.env`, commit only `.env.example`, and rotate any key that was exposed.
