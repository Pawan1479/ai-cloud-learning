<div align="center">

# ☁️🤖 AI & Cloud Learning

**Hands-on projects, experiments and notes from my journey into AI engineering and cloud.**

Building real things, one project at a time, with LLMs, agents, MCP and cloud services.

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-6E56CF)](https://modelcontextprotocol.io/)
[![Claude](https://img.shields.io/badge/Claude-Anthropic-D97757?logo=anthropic&logoColor=white)](https://www.anthropic.com/)
[![Gemini](https://img.shields.io/badge/Gemini-Google-4285F4?logo=googlegemini&logoColor=white)](https://ai.google.dev/)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLMs-000000?logo=ollama&logoColor=white)](https://ollama.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

[Projects](#-projects) · [Tech stack](#-tech-stack) · [Roadmap](#-learning-roadmap) · [Repo structure](#-repository-structure) · [Getting started](#-getting-started)

</div>

---

## 👋 About

This repository is my public learning lab. Each project is:

- **Self-contained**: its own folder, dependencies and README
- **Runnable**: clear setup steps, no hidden magic
- **Documented**: what I built, why, and what I learned along the way

## 🚀 Projects

| Project | Description | Tech | Status |
|---|---|---|---|
| [**LLM Router MCP Server**](projects/llm-router-mcp/) | An MCP server that lets Claude Code send prompts to **Claude**, **Gemini** or a **local Ollama** model through one interface. | Python · MCP · Ollama · Claude API · Gemini API | ✅ Working |
| *More coming soon…* | Agents, RAG, cloud deployments | | 🛠️ Planned |

### ⭐ Featured: LLM Router MCP Server

```
You ──► Claude Code ──(MCP over stdio)──► server.py ──► Anthropic API
                                                   ├──► Gemini API
                                                   └──► Ollama (localhost:11434)
```

- 🔌 **One server, many models**: exposes `local_llm`, `gemini_llm` and `anthropic_llm` as MCP tools
- 💸 **Cost-aware**: free local models run without prompting; paid APIs need explicit approval
- 🧩 **Easy to extend**: adding a provider is one function plus one registry line

➡️ [Read the project README](projects/llm-router-mcp/) · 📘 [Full primer](projects/llm-router-mcp/PRIMER.md)

## 🧰 Tech stack

| Area | Tools |
|---|---|
| **Languages** | Python |
| **LLMs** | Anthropic Claude, Google Gemini, Llama 3 (Ollama) |
| **AI tooling** | Model Context Protocol (MCP), Claude Code |
| **Cloud** | *Coming soon*: AWS / Azure / GCP |
| **Dev environment** | WSL2 (Ubuntu), VS Code, Git, GitHub |

## 🗺️ Learning roadmap

- [x] Run LLMs locally with Ollama
- [x] Call hosted LLM APIs (Claude, Gemini)
- [x] Build an MCP server and connect it to Claude Code
- [ ] Prompt engineering and evaluation
- [ ] Retrieval-Augmented Generation (RAG) with a vector database
- [ ] Build AI agents with tool use
- [ ] Containerize AI apps with Docker
- [ ] Deploy an AI service to the cloud
- [ ] CI/CD with GitHub Actions

## 📁 Repository structure

```
ai-cloud-learning/
├── README.md                 ← you are here
├── LICENSE
├── docs/
│   └── LEARNING_LOG.md       ← dated notes on what I learned
└── projects/
    └── llm-router-mcp/       ← MCP server routing prompts to Claude, Gemini and Ollama
        ├── README.md
        ├── PRIMER.md
        ├── server.py
        ├── requirements.txt
        ├── .env.example
        └── .mcp.json.example
```

## ⚡ Getting started

```bash
git clone https://github.com/Pawan1479/ai-cloud-learning.git
cd ai-cloud-learning/projects/<project-name>
```

Then follow that project's README.

## 📓 Learning log

I keep short, dated notes on concepts and lessons in [docs/LEARNING_LOG.md](docs/LEARNING_LOG.md).

## 🤝 Connect

Suggestions and feedback are welcome. Feel free to open an [issue](https://github.com/Pawan1479/ai-cloud-learning/issues).

<div align="center">

**If you find something useful here, consider giving the repo a ⭐**

</div>
