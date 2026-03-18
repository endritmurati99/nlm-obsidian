# NLM + Obsidian - Parallel Copy

This folder is a **safe working copy** of the original setup. The original
repository stays untouched; improvements happen here.

The structure stays familiar for Claude Code:

- `.claude/skills/` holds the repo skills
- `src/` holds the pipeline modules
- `scripts/` holds deterministic runner scripts
- `Research/` holds generated notes and assets
- `tmp/` holds transcript staging output

## What changed in this copy

- direct YouTube URL support in addition to search queries
- deterministic runner scripts for each skill
- optional `--skip-notebooklm` mode for early testing
- stronger error handling instead of silent partial success
- accurate docs for the actual folder behavior

## Quick start (PowerShell)

```powershell
Copy-Item .env.example .env
py scripts/setup.py --check-only
py scripts/run_youtube_ingest.py "https://www.youtube.com/watch?v=VIDEO_ID"
py scripts/run_research.py "https://www.youtube.com/watch?v=VIDEO_ID" --skip-notebooklm
```

Use the full pipeline once NotebookLM is installed and authenticated:

```powershell
py scripts/run_research.py "your topic or video url" --deliverable flashcards
```

## Claude Code skill map

| Skill | Purpose | Backing script |
|------|---------|----------------|
| `youtube-search` | Pull transcripts and metadata from YouTube | `py scripts/run_youtube_ingest.py` |
| `notebooklm-pipeline` | Turn text sources into a NotebookLM deliverable | `py scripts/run_notebooklm_job.py` |
| `research-pipeline` | Run the full end-to-end flow | `py scripts/run_research.py` |

## Docs

- [docs/architecture.md](docs/architecture.md)
- [docs/notebooklm-setup.md](docs/notebooklm-setup.md)
- [docs/CLaudcode +NLM + Obisadian.md](docs/CLaudcode%20+NLM%20+%20Obisadian.md)
