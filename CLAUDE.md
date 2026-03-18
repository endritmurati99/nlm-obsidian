# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

Automated research pipeline that chains Claude Code → NotebookLM → Obsidian. Claude Code orchestrates data gathering, NotebookLM handles heavy AI analysis (offloading compute to Google at zero token cost), and Obsidian persists results as a navigable knowledge graph.

## Repository Layout

```
src/          # Core pipeline modules (skills, integrations, utilities)
tests/        # Unit and integration tests
docs/         # Architecture decisions and usage guides
scripts/      # One-off setup and maintenance scripts
.claude/
  skills/     # Compiled Claude Code skills (Super Skills live here)
```

## Key Concepts

- **Skill** — A reusable, named Claude Code command stored in `.claude/skills/`. Created via `/skill creator`.
- **Super Skill** — A chained skill that combines sub-routines (e.g. YouTube search → NotebookLM analysis → Obsidian write) into a single zero-touch execution.
- **Vault** — This repository root is the Obsidian vault. Claude Code must be launched from this directory so Obsidian picks up file changes in real time.
- **`claude.md` feedback loop** — After each pipeline run, ask Claude Code to update this file to reflect new output preferences or conventions learned from recent sessions.

## Environment

All secrets and paths live in `.env` (never committed). See `.env.example` for required keys.

## NotebookLM Integration

NotebookLM has no public API. Integration uses the open-source `notebook-lm-pi` CLI wrapper with OAuth browser handshake (`notebooklm login`). Setup steps are documented in [docs/notebooklm-setup.md](docs/notebooklm-setup.md).
