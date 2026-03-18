"""
Obsidian vault writer.
Creates structured Markdown research notes with backlinks,
source tables, and embedded deliverable references.
"""

import re
from datetime import date
from pathlib import Path


# ── Helpers ────────────────────────────────────────────────────────────────────

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
        for kw in keywords:
            if kw.lower() in note_name.lower() and f"[[{note_name}]]" not in found:
                found.append(f"[[{note_name}]]")
                break
    return found


def _deliverable_embed(deliverable_path: Path | None, vault_root: Path) -> str:
    """Return a Markdown embed/link for the deliverable relative to vault root."""
    if deliverable_path is None or not deliverable_path.exists():
        return "_No deliverable file found._"
    try:
        rel = deliverable_path.relative_to(vault_root)
    except ValueError:
        rel = deliverable_path
    # Images: embed; other files: link
    if deliverable_path.suffix.lower() in (".png", ".jpg", ".jpeg", ".svg"):
        return f"![[{rel.as_posix()}]]"
    return f"[[{rel.as_posix()}]]"


# ── Public API ─────────────────────────────────────────────────────────────────

def write_research_note(
    vault_root: Path,
    topic: str,
    videos: list,          # list[VideoMeta] from youtube module
    key_takeaways: list[str],
    analysis_text: str,
    deliverable_path: Path | None,
    deliverable_type: str,
    note_title: str | None = None,
) -> Path:
    """
    Write a research note to Research/{note_title}.md inside the vault.

    Args:
        vault_root:       Absolute path to the Obsidian vault root.
        topic:            Research query / title.
        videos:           VideoMeta list from youtube.search().
        key_takeaways:    3-7 bullet point strings.
        analysis_text:    Full text output from NotebookLM (may be empty).
        deliverable_path: Path to the generated deliverable file (image/PDF/mp3).
        deliverable_type: infographic | podcast | slides | etc.
        note_title:       Filename (without .md). Auto-generated from topic if omitted.
    """
    if note_title is None:
        note_title = _sanitize_filename(topic)

    research_dir = vault_root / "Research"
    research_dir.mkdir(parents=True, exist_ok=True)
    note_path = research_dir / f"{note_title}.md"

    # Backlinks: scan vault for related notes using topic words
    keywords = [w for w in topic.split() if len(w) > 3]
    backlinks = _find_backlinks(vault_root, keywords)
    # Exclude a link to the note itself
    backlinks = [b for b in backlinks if note_title not in b]

    # Source videos table
    video_rows = "\n".join(
        f"| {v.title} | {v.url} | {v.view_count:,} |"
        for v in videos
    )

    # Takeaways
    takeaways_md = "\n".join(f"- {t}" for t in key_takeaways) if key_takeaways else "_No takeaways available._"

    # Deliverable embed
    deliverable_embed = _deliverable_embed(deliverable_path, vault_root)
    deliverable_filename = deliverable_path.name if deliverable_path else "N/A"

    # Analysis block
    analysis_block = analysis_text.strip() if analysis_text.strip() else "_Full analysis not available in text form._"

    # Related block
    related_block = "  ".join(backlinks) if backlinks else "_No related notes found yet._"

    note_content = f"""# {topic}

> Research generated: {date.today().isoformat()}
> Sources: {len(videos)} YouTube videos
> Deliverable: [[{deliverable_filename}]]

## Key Takeaways

{takeaways_md}

## Deliverable

{deliverable_embed}

## Source Videos

| Title | URL | Views |
|-------|-----|-------|
{video_rows}

## Analysis

{analysis_block}

## Related

{related_block}
"""

    note_path.write_text(note_content, encoding="utf-8")
    return note_path
