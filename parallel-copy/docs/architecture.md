# Parallel Copy Architecture

This folder is a hardened copy of the original NLM + Obsidian setup. The goal is
to preserve the same high-level Claude Code structure while making the workflow
more deterministic and easier to test.

## Design rules

1. Keep the original repository untouched.
2. Keep the same top-level shape: `.claude`, `docs`, `scripts`, `src`, `tests`, `Research`, `tmp`.
3. Make skills call deterministic Python runner scripts instead of rebuilding
   shell commands ad hoc.
4. Support both a YouTube search query and a direct YouTube video URL.
5. Allow a partial run with `--skip-notebooklm` so YouTube ingestion can be
   tested before NotebookLM is available.

## Runtime flow

```text
research-pipeline skill
    -> py scripts/run_research.py
        -> src.pipeline.run()
            -> src.youtube.search()
            -> src.notebooklm.run_pipeline()     # optional
            -> src.vault.write_research_note()
```

## Skill flow

- `youtube-search` calls `py scripts/run_youtube_ingest.py`
- `notebooklm-pipeline` calls `py scripts/run_notebooklm_job.py`
- `research-pipeline` calls `py scripts/run_research.py`

## Output flow

- Source transcripts: `tmp/transcripts/<slug>/`
- Deliverables: `Research/assets/`
- Research notes: `Research/<note>.md`

## Why this is better

- Skills are shorter and easier to trust.
- Runner scripts are reusable outside Claude Code.
- Testing a new YouTube video no longer requires NotebookLM to be ready first.
- Error handling is fail-fast instead of silently continuing on empty outputs.
