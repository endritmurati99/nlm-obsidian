---
name: research-pipeline
description: Run the full end-to-end workflow from YouTube input to an Obsidian research note, optionally including NotebookLM deliverables. Use when the user wants search plus analysis plus vault output, or when they want to test a new YouTube video inside this workflow.
---

# Research Pipeline

Prefer this skill over the narrower skills when the user wants the full flow.

Use the deterministic runner:

```powershell
py scripts/run_research.py "<topic-or-url>" --deliverable flashcards
```

For a first validation run without NotebookLM:

```powershell
py scripts/run_research.py "<topic-or-url>" --skip-notebooklm
```

## Rules

- Accept either a YouTube search query or a direct YouTube URL.
- Write notes to `Research/` and binary output to `Research/assets/`.
- Fail fast on missing transcripts or missing deliverables.
- Report the resulting note path, deliverable path, processed transcript count, and NotebookLM status.
- Keep the workflow aligned with `CLAUDE.md` and the runner scripts.
