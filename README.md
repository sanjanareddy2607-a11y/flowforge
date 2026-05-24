# ⚡ FlowForge — Multi-Agent AI Workflow Automation Engine

> A configurable, backend-first AI pipeline engine that executes multi-step agent workflows using JSON config files — no code required to define new pipelines.

[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?style=flat-square)](https://fastapi.tiangolo.com)
[![Gemini](https://img.shields.io/badge/Gemini-API-orange?style=flat-square)](https://aistudio.google.com)
[![License](https://img.shields.io/badge/License-MIT-purple?style=flat-square)](LICENSE)

---

## What is FlowForge?

FlowForge lets you define multi-step AI workflows as JSON config files and execute them via a REST API. Each workflow is a sequence of **nodes** — scrape, AI-enrich, transform, filter, email — where the output of each node flows into the next.

**Example:** Search for competitor news → extract key claims with AI → generate a competitive brief → email it to your team. All defined in one JSON file, triggered by one API call.

---

## Architecture
JSON Workflow Config
│
▼
WorkflowEngine (orchestrator)
│
├── ScrapeNode    → fetches real-world data via SerpAPI
├── AINode        → calls Gemini API with prompt templates
├── TransformNode → reshapes/formats data between stages
├── FilterNode    → conditional branching (stop if condition fails)
└── EmailNode     → delivers output via SMTP
│
▼
StateManager → persists run history to JSON
│
▼
FastAPI REST API → /run · /status · /workflows · /history
│
▼
Dashboard UI (real-time pipeline status board)
---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend framework | FastAPI + Uvicorn |
| AI / LLM | Google Gemini API (gemini-2.5-flash) |
| Web scraping | SerpAPI + httpx |
| Email delivery | RESEND |
| State persistence | JSON flat-file store |
| Frontend | Vanilla HTML/CSS/JS |
| Deployment | Render (PaaS) |

---

## Key Engineering Concepts Demonstrated

- **Registry Pattern** — node types are resolved from a string→class map, making the engine open for extension with zero modification
- **Pipeline Orchestration** — sequential node execution with shared context (accumulated state dict passed between nodes)
- **Abstract Base Class** — enforces interface contract across all node types
- **Prompt Templating** — dynamic {input} injection into LLM prompts at runtime
- **Async API design** — sync and async workflow execution modes via FastAPI BackgroundTasks
- **Separation of concerns** — engine, nodes, state, and API are fully decoupled

---

## Quick Start

### 1. Clone and set up
`ash
git clone https://github.com/YOURUSERNAME/flowforge.git
cd flowforge
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
`

### 2. Add API keys
Create a .env file:
GEMINI_API_KEY=xxx
SERP_API_KEY=xxx
EMAIL_SENDER=sanjanareddy2607@gmail.com
EMIAL_PASSWORD=xxx
RESEND_API_KEY=xxx

### 3. Run
`ash
uvicorn main:app --reload
`

Open http://localhost:8000

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| POST | /run | Trigger a workflow run |
| GET | /status/{run_id} | Get run status and node outputs |
| GET | /workflows | List all available workflows |
| GET | /history | Full run history |
| GET | /docs | Auto-generated Swagger UI |

### Example request
`ash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"workflow_name": "hn_digest"}'
`

---

## Workflow Config Example

`json
{
  "name": "hn_digest",
  "nodes": [
    {"id": "fetch",     "type": "scrape", "config": {"query": "AI startup news", "num_results": 5}},
    {"id": "summarize", "type": "ai",     "config": {"prompt": "Summarize in 5 bullets: {input}", "input_key": "raw_text"}},
    {"id": "score",     "type": "ai",     "config": {"prompt": "Rate relevance 1-10: {input}", "input_key": "summary"}}
  ]
}
`

---

## Roadmap

- [ ] Parallel node execution with asyncio
- [ ] Visual drag-and-drop workflow builder
- [ ] Redis-backed state management
- [ ] Webhook trigger nodes
- [ ] Slack / Notion output nodes

---

## Author

Built by M Sanjana Reddy (https://github.com/sanjanareddy2607-a11y) as a portfolio project demonstrating AI pipeline engineering, backend architecture, and multi-agent orchestration.
