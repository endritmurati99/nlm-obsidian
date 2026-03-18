# NotebookLM Setup Guide

NotebookLM has no official public API. This repository expects a compatible
command-line wrapper that exposes either `notebooklm` or `notebook-lm`.

## 1. Try the setup helper

From this folder:

```powershell
py scripts/setup.py
```

The setup script will try a few common package names and then tell you what is
still missing.

## 2. Authenticate outside Claude Code

If the CLI is installed, run the login flow in a **separate terminal**:

```powershell
notebooklm login
```

Do not run the browser login handshake inside Claude Code.

## 3. Validate the environment

```powershell
py scripts/health_check.py
```

## 4. Run a real job

Once authentication works, use the skill-backed runner:

```powershell
py scripts/run_research.py "your topic or video url" --deliverable flashcards
```

## Fallback plan

If NotebookLM is still unavailable, you can still validate the YouTube and
Obsidian parts of the workflow:

```powershell
py scripts/run_research.py "your topic or video url" --skip-notebooklm
```
