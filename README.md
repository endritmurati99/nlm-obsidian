# NLM Obsidian

NLM Obsidian is a research pipeline that connects Claude Code, NotebookLM, YouTube/web/PDF ingestion, and an Obsidian-style Markdown vault.

## Current Status

The repository is an experimental but structured pipeline for collecting sources, delegating heavy analysis to NotebookLM, and writing research notes back into a local vault. It includes Python modules, setup and health-check scripts, tests, docs, and a parallel prototype copy for a newer pipeline shape.

The intended workflow is local-first for storage, with NotebookLM used as an external analysis engine when the user explicitly runs that stage.

## Key Capabilities

- YouTube transcript extraction with `yt-dlp`.
- NotebookLM CLI integration for analysis deliverables.
- Markdown research-note generation into an Obsidian vault.
- Asset handling for generated deliverables.
- Health checks for required tools, auth state, env files, vault folders, and skills.
- Unit tests for vault-writing and YouTube helper behavior.

## Workflow

```text
YouTube URL / web page / PDF
  -> Claude Code orchestration
  -> transcript or source extraction
  -> NotebookLM analysis
  -> Markdown research note
  -> Obsidian vault
```

Useful docs:

- [NotebookLM Setup](docs/notebooklm-setup.md)
- [Original Pipeline Notes](docs/CLaudcode%20+NLM%20+%20Obisadian.md)
- [Parallel Prototype Architecture](parallel-copy/docs/architecture.md)

## Quick Start

```bash
python3 scripts/setup.py --check-only
cp .env.example .env
notebooklm login
python3 scripts/health_check.py
```

For a first setup run that may install missing Python tools:

```bash
python3 scripts/setup.py
```

Launch Claude Code from the repository root after the health check passes.

## Repository Layout

```text
src/             pipeline, NotebookLM, vault, and YouTube modules
scripts/         setup and health-check commands
tests/           unit tests
docs/            setup and architecture notes
Research/        generated research notes and vault content
parallel-copy/   experimental second pipeline shape
```

## Verification

Recommended checks:

```bash
git diff --check
python3 -m pytest tests -q
python3 scripts/health_check.py
```

If the host lacks optional tools such as `yt-dlp` or `notebooklm`, the health check should report the missing dependency clearly.

## Privacy And Safety

- Do not commit real `.env` credentials or OAuth artifacts.
- Treat NotebookLM as an external Google-backed analysis surface.
- Avoid sending private or sensitive research material to NotebookLM unless that is intended.
- Keep generated vault content reviewable before publishing it.
- Preserve local filesystem boundaries when writing notes and assets.

## Roadmap

- Consolidate the root pipeline and `parallel-copy/` prototype once the better flow is clear.
- Add stronger setup docs for NotebookLM auth and vault layout.
- Expand tests around pipeline orchestration and health-check behavior.
- Improve generated note structure and asset traceability.
