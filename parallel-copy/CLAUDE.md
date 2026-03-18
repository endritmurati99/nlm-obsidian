# CLAUDE.md

This is the **parallel copy** of the NLM + Obsidian workflow. Keep the original
repository untouched and make changes here first.

## Project purpose

Use Claude Code skills to move from YouTube input to structured research notes in
Obsidian, optionally passing through NotebookLM for deliverables.

## Repository layout

```text
src/          core modules
scripts/      deterministic entry points used by skills
tests/        local test coverage
docs/         setup and architecture notes
.claude/      Claude Code permissions and skills
Research/     generated notes and assets
tmp/          transcript staging output
```

## Operating rules

1. Prefer the repo skills over ad hoc shell sequences.
2. Prefer `py scripts/run_research.py` for end-to-end runs.
3. Use `py scripts/run_youtube_ingest.py` when validating a new video before
   NotebookLM is ready.
4. Keep all generated note content in `Research/` and binary output in
   `Research/assets/`.
5. Keep `CLAUDE.md` and the skill files aligned with the actual scripts.

## Skill-backed commands

- `youtube-search` -> `py scripts/run_youtube_ingest.py`
- `notebooklm-pipeline` -> `py scripts/run_notebooklm_job.py`
- `research-pipeline` -> `py scripts/run_research.py`

## Config

- `.env` is optional but supported.
- If `VAULT_PATH` is missing, this copy uses its own root as the vault.
- `DEFAULT_DELIVERABLE` and `YT_MAX_RESULTS` are loaded by `src/config.py`.

## NotebookLM note

NotebookLM CLI availability varies. This copy is designed so the YouTube and
vault-writing parts can still be tested with `--skip-notebooklm`.
