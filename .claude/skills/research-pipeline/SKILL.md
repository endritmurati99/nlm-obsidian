---
name: research-pipeline
description: Use when the user wants to run a full end-to-end research workflow: search a topic, analyze it with NotebookLM, and save results to the Obsidian vault. This is the Super Skill. Triggers on phrases like "research X", "run the pipeline on X", "search and analyze X", "find YouTube videos about X and make an infographic", or any request combining data gathering with AI analysis and saving to the vault. Always prefer this skill over calling youtube-search or notebooklm-pipeline individually when the user wants the full flow.
---

# Research Pipeline (Super Skill)

The end-to-end research workflow. One command triggers: **YouTube search → NotebookLM analysis → Obsidian vault write**. Zero manual steps between stages.

```
User prompt
    │
    ▼
[youtube-search skill]     ← yt-dlp, returns transcript files
    │
    ▼
[notebooklm-pipeline skill] ← Google processes, returns deliverable
    │
    ▼
[Write to Obsidian vault]   ← Markdown note + backlinks + deliverable file
```

## Inputs (ask user if missing)

| Parameter | Default | Description |
|-----------|---------|-------------|
| `topic` | required | Research query, e.g. `"Claude Code MCP servers"` |
| `max_videos` | `5` | How many YouTube videos to pull |
| `deliverable` | `infographic` | `infographic` \| `podcast` \| `slides` \| `mindmap` \| `flashcards` |
| `note_title` | auto-generated | Obsidian note filename |

## Execution (run each step fully before moving to the next)

### Step 1 — YouTube Search

Invoke the `youtube-search` skill:
- query = `{topic}`
- max_results = `{max_videos}`
- output_dir = `tmp/transcripts/{sanitized_topic}/`

Wait for all transcripts to be downloaded and cleaned.

### Step 2 — NotebookLM Analysis

Invoke the `notebooklm-pipeline` skill:
- title = `Research: {topic}`
- source_files = all `.txt` files from Step 1
- deliverable = `{deliverable}`
- output_dir = `Research/`

Wait for NotebookLM to finish. Do not skip or short-circuit this step — generation takes time but runs at zero token cost.

### Step 3 — Write to Obsidian vault

Create a Markdown note at `Research/{note_title}.md` with this structure:

```markdown
# {topic}

> Research generated: {date}
> Sources: {n} YouTube videos
> Deliverable: [[{deliverable_filename}]]

## Key Takeaways

{3-7 bullet points summarising the NotebookLM analysis}

## Source Videos

| Title | URL | Views |
|-------|-----|-------|
{rows from metadata.tsv}

## Analysis

{full text output from NotebookLM if available}

## Related

{[[backlinks]] to related notes already in the vault — scan vault for semantically related .md files and link them using double-bracket syntax}
```

Save any binary deliverable (image, PDF, mp3) to `Research/assets/{topic}-{deliverable}.{ext}` and reference it from the note.

### Step 4 — Confirm completion

Report back to the user:

```
PIPELINE COMPLETE
Topic: {topic}
Videos processed: {n}
Note: Research/{note_title}.md
Deliverable: Research/assets/{topic}-{deliverable}.{ext}
Vault graph: open Obsidian to see new backlinks
```

## Cleanup

After a successful run, delete `tmp/transcripts/{sanitized_topic}/` to keep the vault clean.

## Adapting the data source

The YouTube search module is swappable. To use local PDFs, articles, or text files instead:

1. Skip Step 1.
2. Point the `notebooklm-pipeline` skill directly at your local files.
3. Continue from Step 2.

The rest of the pipeline (NotebookLM → Obsidian write) is identical regardless of source type.

## Vault conventions (learned from claude.md feedback loop)

- All research notes live in `Research/`
- All binary assets live in `Research/assets/`
- Always add `[[backlinks]]` using double brackets around concepts that appear in other vault notes
- Use `> Research generated:` blockquote at the top for provenance
- After the pipeline runs, update CLAUDE.md if the user requests new output preferences
