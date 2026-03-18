---
name: notebooklm-pipeline
description: Use when sending content to NotebookLM for deep analysis or generating deliverables (infographic, podcast, slides, mindmap, flashcards). Triggers when the user wants to analyze documents with NotebookLM, create a research deliverable, or offload AI processing to Google at zero token cost. Use this even if the user just says "analyze this with NotebookLM" or "make an infographic from this".
---

# NotebookLM Pipeline

Sends text sources to Google NotebookLM via the `notebook-lm-pi` CLI wrapper, generates a deliverable, and returns the output file path. This is the analysis and rendering module — it offloads all heavy AI compute to Google's servers (zero local tokens consumed).

## Prerequisites

NotebookLM has no public API. This skill uses the open-source `notebook-lm-pi` wrapper.

### First-time setup (run once, outside Claude Code terminal)

```bash
# Install the wrapper
pip install notebooklm   # or: pip install notebook-lm-pi

# Authenticate with your Google account (opens browser)
notebooklm login
```

If `notebooklm login` is not available, read the notebook-lm-pi repository README to learn the exact CLI commands — Claude Code will self-learn the tool from the docs.

## Inputs

| Parameter | Description |
|-----------|-------------|
| `title` | Notebook title |
| `source_files` | List of `.txt` transcript/document paths |
| `deliverable` | `infographic` \| `podcast` \| `slides` \| `mindmap` \| `flashcards` \| `audio` |
| `output_dir` | Where to save the deliverable |

## Execution Steps

### Step 1 — Create a new notebook

```bash
notebooklm create --title "{title}"
# Save the returned notebook_id
```

### Step 2 — Add sources (up to 50 per notebook)

For each source file:

```bash
notebooklm add-source \
  --notebook-id {notebook_id} \
  --file {source_file}
```

Or add plain text directly:

```bash
notebooklm add-source \
  --notebook-id {notebook_id} \
  --text "$(cat {source_file})"
```

### Step 3 — Request the deliverable

```bash
notebooklm generate \
  --notebook-id {notebook_id} \
  --type {deliverable} \
  --output {output_dir}/{title}-{deliverable}
```

Expected generation times:
- Text summary: < 1 minute
- Infographic: ~6 minutes
- Full slide deck: ~15 minutes

Wait for completion. Do not cancel — the job runs on Google's servers.

### Step 4 — Return result

```
NOTEBOOKLM_RESULT
notebook_id: {notebook_id}
deliverable_type: {deliverable}
output_path: {output_dir}/{title}-{deliverable}.*
status: complete
```

## Output Files by Deliverable Type

| Type | Extension | Notes |
|------|-----------|-------|
| `infographic` | `.png` or `.pdf` | Single visual summary |
| `podcast` | `.mp3` | AI-generated audio discussion |
| `slides` | `.pdf` | Multi-page presentation |
| `mindmap` | `.png` or `.svg` | Topic relationship graph |
| `flashcards` | `.pdf` or `.json` | Study cards |
| `audio` | `.mp3` | Audio review / summary |

## Common Issues

| Problem | Fix |
|---------|-----|
| `notebooklm: command not found` | Re-install: `pip install notebooklm` |
| Auth expired | Re-run `notebooklm login` |
| Source too large | Split into chunks < 500KB each |
| Generation timeout | Long-form deliverables (slides) take up to 15 min — wait |

## Note on Self-Learning

If the `notebook-lm-pi` CLI commands differ from above, pass the repository README to the Skill Creator and ask it to update this skill. Claude Code will read the docs and adapt.
