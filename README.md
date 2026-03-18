# NLM + Obsidian — Automated Research Pipeline

Chains **Claude Code → NotebookLM → Obsidian** into a zero-touch research workflow. Claude Code orchestrates data gathering, NotebookLM handles heavy AI analysis at zero token cost (runs on Google), and Obsidian stores the results as a navigable knowledge graph.

---

## How It Works

```
YouTube URL / Web Page / PDF
        │
        ▼
  Claude Code (orchestrator)
        │  1. Extract transcript via yt-dlp
        │  2. Feed to NotebookLM for analysis
        │  3. Write results to Obsidian vault as Markdown
        ▼
  Obsidian Vault (this repo root)
        └── Research notes with [[backlinks]]
        └── NLM deliverables (infographic, podcast, mindmap, slides)
```

---

## Prerequisites

| Tool | Purpose |
|------|---------|
| [Claude Code](https://claude.ai/code) | Orchestration and skill execution |
| [Obsidian](https://obsidian.md) | Open this repo as your vault |
| [yt-dlp](https://github.com/yt-dlp/yt-dlp) | YouTube transcript extraction |
| [notebooklm CLI](https://github.com/deta/notebooklm) | Unofficial NotebookLM CLI wrapper |
| Python 3.10+ | Script runtime |

---

## Setup

```bash
# 1. Clone and open this folder as your Obsidian vault

# 2. Copy and fill in environment file
cp .env.example .env

# 3. Authenticate with NotebookLM (run in a separate terminal — opens browser)
notebooklm login

# 4. Launch Claude Code from this directory
claude
```

---

## Repository Layout

```
NLM+Obsidian/
├── .claude/
│   └── skills/         # Claude Code skills (Super Skills)
├── src/                # Pipeline modules
│   ├── notebooklm.py   # NLM CLI integration
│   ├── pipeline.py     # Main orchestration logic
│   ├── vault.py        # Obsidian write utilities
│   └── youtube.py      # yt-dlp transcript extraction
├── tests/              # Unit and integration tests
├── docs/               # Architecture and setup guides
├── scripts/            # One-off setup and maintenance scripts
├── Research/           # Generated research notes (vault content)
├── parallel-copy/      # Experimental parallel pipeline variant
├── .env.example        # Required environment variables (copy to .env)
└── CLAUDE.md           # Claude Code instructions and conventions
```

---

## Skills

Skills live in `.claude/skills/` and are invoked as slash commands inside Claude Code. Create new skills with `/skill creator`.

---

## Key Concepts

- **Super Skill** — A chained Claude Code command that combines sub-routines (YouTube search → NLM analysis → Obsidian write) into a single execution
- **Vault** — This repo root is the Obsidian vault; launch Claude Code from here so Obsidian picks up file changes in real time
- **Zero token cost** — NotebookLM analysis (infographics, podcasts, study guides, mindmaps) runs on Google's servers, not on Claude API credits

---

## Docs

- [docs/notebooklm-setup.md](docs/notebooklm-setup.md) — NotebookLM OAuth setup
- [docs/architecture.md](docs/architecture.md) — Full system architecture
