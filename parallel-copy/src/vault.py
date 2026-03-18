"""
Obsidian vault writer.
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path


def _sanitize_filename(name: str) -> str:
    """Convert a topic string to a safe filename."""
    return re.sub(r"[^\w\s-]", "", name).strip().replace(" ", "-")


def _find_backlinks(vault_root: Path, keywords: list[str]) -> list[str]:
    """
    Scan all .md files in the vault for notes whose titles contain any keyword.
    Returns a list of [[backlink]] strings for related notes.
    """
    found: list[str] = []
    for md_file in vault_root.rglob("*.md"):
        note_name = md_file.stem
        for keyword in keywords:
            if keyword.lower() in note_name.lower() and f"[[{note_name}]]" not in found:
                found.append(f"[[{note_name}]]")
                break
    return found


def _relative_vault_path(path: Path, vault_root: Path) -> str:
    try:
        return path.relative_to(vault_root).as_posix()
    except ValueError:
        return path.as_posix()


def _deliverable_link(deliverable_path: Path | None, vault_root: Path) -> str:
    if deliverable_path is None or not deliverable_path.exists():
        return "_No deliverable file generated._"
    return f"[[{_relative_vault_path(deliverable_path, vault_root)}]]"


def _deliverable_embed(deliverable_path: Path | None, vault_root: Path) -> str:
    """Return a Markdown embed/link for the deliverable relative to vault root."""
    if deliverable_path is None or not deliverable_path.exists():
        return "_No deliverable file found._"

    relative_path = _relative_vault_path(deliverable_path, vault_root)
    if deliverable_path.suffix.lower() in (".png", ".jpg", ".jpeg", ".svg"):
        return f"![[{relative_path}]]"
    return f"[[{relative_path}]]"


def write_research_note(
    vault_root: Path,
    topic: str,
    videos: list,
    key_takeaways: list[str],
    analysis_text: str,
    deliverable_path: Path | None,
    deliverable_type: str,
    note_title: str | None = None,
    source_mode: str = "search",
    notebook_id: str = "",
    notebooklm_status: str = "skipped",
    notebooklm_message: str = "",
) -> Path:
    """
    Write a research note to Research/{note_title}.md inside the vault.
    """
    if note_title is None:
        note_title = _sanitize_filename(topic)

    research_dir = vault_root / "Research"
    research_dir.mkdir(parents=True, exist_ok=True)
    note_path = research_dir / f"{note_title}.md"

    keywords = [word for word in topic.split() if len(word) > 3]
    backlinks = _find_backlinks(vault_root, keywords)
    backlinks = [backlink for backlink in backlinks if note_title not in backlink]

    video_rows = "\n".join(
        f"| {video.title} | {video.url} | {video.view_count:,} | {video.upload_date or 'n/a'} |"
        for video in videos
    ) or "| _No source videos captured._ | - | - | - |"

    takeaways_md = "\n".join(f"- {takeaway}" for takeaway in key_takeaways) if key_takeaways else "_No takeaways available._"
    deliverable_embed = _deliverable_embed(deliverable_path, vault_root)
    deliverable_link = _deliverable_link(deliverable_path, vault_root)
    analysis_block = analysis_text.strip() if analysis_text.strip() else "_Full analysis not available in text form._"
    related_block = "  ".join(backlinks) if backlinks else "_No related notes found yet._"

    notebook_line = notebook_id or notebooklm_status
    if notebooklm_message:
        notebook_line = f"{notebook_line} - {notebooklm_message}"

    note_content = f"""# {topic}

> Research generated: {date.today().isoformat()}
> Source mode: {source_mode}
> Sources: {len(videos)} YouTube entries
> NotebookLM: {notebook_line}
> Deliverable ({deliverable_type}): {deliverable_link}

## Key Takeaways

{takeaways_md}

## Deliverable

{deliverable_embed}

## Source Videos

| Title | URL | Views | Upload Date |
|-------|-----|-------|-------------|
{video_rows}

## Analysis

{analysis_block}

## Related

{related_block}
"""

    note_path.write_text(note_content, encoding="utf-8")
    return note_path
