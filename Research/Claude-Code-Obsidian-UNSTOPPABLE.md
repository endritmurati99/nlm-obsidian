# Claude Code + Obsidian = UNSTOPPABLE

> Research generated: 2026-03-17
> Source: [YouTube — Claude Code + Obsidian = UNSTOPPABLE](https://www.youtube.com/watch?v=eRr2rTKriDM) · 72,108 views
> Notebook: `050ee6da-221b-4b0a-917e-ee1b986c613b`

---

## Deliverables

| Format | File | Purpose |
|--------|------|---------|
| 📑 Slide Deck | [[Research/assets/Claude Code Persistent Memory.pdf]] | Visual overview of all key concepts |
| 📖 Study Guide | [[Research/assets/Maximizing Claude Code with Obsidian_ A Comprehensive Study Guide.md]] | Deep-dive written guide with exercises |
| 🃏 Flashcards | [[Research/assets/flashcards.json]] | Active recall — memorise all key terms |

---

## Key Takeaways

- Claude Code lacks persistent memory across sessions — Obsidian acts as the **external memory layer** that fixes this
- The relationship is symbiotic: Obsidian organises for humans, Claude Code automates the linking and formatting
- The **Vault** = your second brain (all Markdown files); **Claude.md** = the frontal cortex (rules + conventions)
- Obsidian is the "filing cabinet" sweet spot — more organised than loose files, far less complex than Graph RAG
- Claude Code uses `[[double brackets]]` to create bidirectional links between notes automatically
- The `claude.md` feedback loop is what makes the system get smarter over time — update it regularly
- Obsidian is 100% local Markdown — no vendor lock-in, no extra token cost, 2,700+ community plugins

---

## Overview

The integration solves the core problem with AI agents: **they forget everything between sessions**. Obsidian gives Claude Code a structured, navigable knowledge base — a "filing cabinet" rather than a "black box" — so each new session builds on the last instead of starting from zero.

---

## Core Concepts

### The Three-Way Value Exchange
- **For you (the user):** Visual graph of how all your notes and projects connect
- **For Obsidian:** Claude Code handles the tedious work of drafting and linking Markdown files
- **For Claude Code:** Organised hierarchy improves AI performance — it can find relationships between documents far more effectively

### The Organisation Spectrum
| Level | Analogy | Reality |
|-------|---------|---------|
| No structure | Papers on the floor | Claude Code struggles, becomes a black box for humans |
| **Obsidian (Filing Cabinet)** | **Happy medium** | **Free, zero extra tokens, sufficient structure — recommended** |
| Graph RAG | Library of Congress | Nuclear-bomb approach — powerful but overkill for most users |

### Second Brain vs. Frontal Cortex
- **The Vault (Second Brain):** Every note, folder, and Markdown file — your total knowledge base
- **Claude.md (Frontal Cortex):** The single file Claude Code reads constantly — your thinking templates, conventions, and preferences

---

## Step-by-Step Setup

### Phase 1 — Install Obsidian
1. Download Obsidian from `obsidian.md`
2. Create a **Vault** — choose a folder name and location
3. Place the vault in the same directory where you run Claude Code projects

### Phase 2 — Launch Claude Code From the Vault
1. Open terminal
2. `cd` into the vault folder
3. Start Claude Code — it will see the full file structure (daily notes, research, projects)

### Phase 3 — Configure Claude.md
1. Create or edit `CLAUDE.md` in the project root
2. Add Obsidian rules: always use `[[double brackets]]` for linking files
3. Optional: run `/init` inside Claude Code to auto-generate conventions from existing notes

---

## Key Workflows

### Personal Assistant Workflow
- Give Claude Code raw text or brain dumps
- It creates proper Markdown files and links them to related existing notes
- Value compounds over months — nothing gets lost in a "black box"

### Research Agent Workflow
- Use Claude Code skills (YouTube search, NotebookLM) to pull external sources
- Dump research into the vault automatically
- `claude.md` helps Claude Code compare new notes to existing thinking templates

---

## Pro Tips

- **Living Document Strategy:** Periodically ask Claude to *"review all notes, compare to claude.md, and improve the conventions"* — keeps the system evolving
- **Claude.md scope:** Ideal for personal assistant workflows; may hurt performance in complex coding projects if conventions are too broad
- **No vendor lock-in:** Everything is plain `.md` files — you own your data forever
- **Plugin ecosystem:** 2,700+ community plugins available if base Obsidian isn't enough

---

## Glossary

| Term | Definition |
|------|------------|
| [[Vault]] | The local folder where Obsidian stores all notes and metadata |
| [[Claude.md]] | Project-level context file — Claude Code's "memory" of how you think |
| Markdown | Lightweight `.md` text format used for all Obsidian files |
| Graph View | Visual map of how notes connect to each other |
| Vendor Lock-in | Being trapped by proprietary formats — Obsidian avoids this |
| Orchestration Layer | System (Obsidian) that organises data for both humans and AI |
| [[Graph RAG]] | Heavy embedding-based retrieval system — overkill for most users |
| `/init` (Slashinit) | Claude Code command to auto-initialise `claude.md` conventions from a codebase |

---

## Practice

### Quick Quiz
1. What is an Obsidian "Vault"?
2. How does Obsidian give Claude Code persistent memory?
3. Why is Obsidian the "filing cabinet" and not the "Library of Congress"?
4. What syntax does Claude Code use to link notes?
5. What is the purpose of `claude.md` in this system?

### Essay Prompts
1. **Organisation Spectrum:** Compare a disorganised file system, Obsidian, and Graph RAG. Why is Obsidian the happy medium?
2. **Symbiotic Relationship:** How do Claude Code and Obsidian each solve the other's weaknesses?
3. **Living claude.md:** How does continuously updating `claude.md` move Claude Code toward a "Jarvis-type" personal assistant?

---

## Related

[[CLAUDE.md]] · [[Research]] · [[Graph RAG]] · [[Vault]]
