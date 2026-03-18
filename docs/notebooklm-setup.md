# NotebookLM Setup Guide

NotebookLM has no public API. This pipeline uses the open-source
[notebooklm-py](https://github.com/teng-lin/notebooklm-py) CLI wrapper.

---

## 1. Install the CLI

Open a **regular terminal** (not inside Claude Code):

```bash
pip install notebooklm-py
```

Verify it installed:

```bash
notebooklm --version
```

---

## 2. Authenticate with Google

Still in the **separate terminal**:

```bash
notebooklm login
```

This opens your browser. Log in with the Google account you use for NotebookLM
and grant access. The token is stored locally and reused for future runs.

> **Important:** Do NOT run `notebooklm login` inside the Claude Code terminal.
> It requires an interactive browser handshake that conflicts with the Claude Code session.

---

## 3. Verify authentication

```bash
notebooklm status
```

Expected output: `Logged in as you@gmail.com`

---

## 4. Run the health check

Back in the Claude Code terminal (from the vault root):

```bash
python scripts/health_check.py
```

All checks should pass before running the pipeline.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `notebooklm: command not found` | Re-install: `pip install notebooklm-py` |
| Auth expired / 401 errors | Re-run `notebooklm login` in a separate terminal |
| Source file too large | Split into chunks smaller than 500 KB each |
| Generation timeout | Long deliverables (slides) take up to 15 min — wait; do not cancel |

---

## Generation time reference

| Deliverable | Estimated time |
|-------------|---------------|
| Text summary | < 1 minute |
| Infographic | ~6 minutes |
| Podcast | ~8 minutes |
| Slide deck | ~15 minutes |
| Mindmap / Flashcards | ~5 minutes |
