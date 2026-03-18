---
name: notebooklm-pipeline
description: Send prepared text sources to NotebookLM and generate a deliverable such as flashcards, slides, infographic, podcast, audio, or mindmap. Use when source files already exist and the user wants the NotebookLM stage only.
---

# NotebookLM Pipeline

Use the deterministic runner:

```powershell
py scripts/run_notebooklm_job.py "Research Title" source1.txt source2.txt --deliverable flashcards
```

## Rules

- Use only after source text files already exist.
- Save output to `Research/assets/` unless the user requests a different folder.
- If NotebookLM is not installed or not authenticated, stop and surface that clearly.
- Do not invent analysis text that the CLI did not actually return.

## Output contract

The script prints JSON with:

- `notebook_id`
- `deliverable_type`
- `output_path`
- `status`
- `message`
