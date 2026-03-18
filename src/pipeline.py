"""
Research Pipeline orchestrator (Super Skill implementation).
Chains: YouTube search → NotebookLM analysis → Obsidian vault write.
"""

import shutil
from dataclasses import dataclass
from pathlib import Path

from . import youtube, notebooklm, vault


@dataclass
class PipelineResult:
    topic: str
    videos_processed: int
    note_path: Path
    deliverable_path: Path | None
    deliverable_type: str
    notebook_id: str


def run(
    topic: str,
    vault_root: Path,
    max_videos: int = 5,
    deliverable: str = "infographic",
    note_title: str | None = None,
) -> PipelineResult:
    """
    Run the full research pipeline end-to-end.

    Args:
        topic:       Research query, e.g. "Claude Code MCP servers".
        vault_root:  Absolute path to the Obsidian vault root.
        max_videos:  Number of YouTube videos to pull (default 5).
        deliverable: Output format — infographic | podcast | slides | mindmap | flashcards | audio.
        note_title:  Obsidian note filename (auto-generated from topic if omitted).
    """

    print(f"\n{'='*55}")
    print(f"  PIPELINE START: {topic}")
    print(f"{'='*55}\n")

    # ── Step 1: YouTube Search ─────────────────────────────────────────────────
    print(f"[1/3] YouTube Search  (max {max_videos} videos)")
    yt_result = youtube.search(
        query=topic,
        max_results=max_videos,
        output_dir=vault_root / "tmp" / "transcripts" / _slug(topic),
    )
    print(f"      Found {len(yt_result.videos)} videos, "
          f"{len(yt_result.transcript_files)} transcripts downloaded.\n")

    # ── Step 2: NotebookLM Analysis ────────────────────────────────────────────
    print(f"[2/3] NotebookLM Analysis  (deliverable: {deliverable})")
    nlm_result = notebooklm.run_pipeline(
        title=f"Research: {topic}",
        source_files=yt_result.transcript_files,
        deliverable=deliverable,
        output_dir=vault_root / "Research" / "assets",
    )
    print(f"      Notebook ID: {nlm_result.notebook_id}")
    print(f"      Deliverable: {nlm_result.output_path}\n")

    # ── Step 3: Write to Obsidian Vault ────────────────────────────────────────
    print(f"[3/3] Writing Obsidian note")
    # Build basic key takeaways from metadata (NLM text analysis goes in analysis_text)
    takeaways = _build_takeaways(yt_result)

    note_path = vault.write_research_note(
        vault_root=vault_root,
        topic=topic,
        videos=yt_result.videos,
        key_takeaways=takeaways,
        analysis_text="",  # NotebookLM delivers via deliverable file, not text stdout
        deliverable_path=nlm_result.output_path,
        deliverable_type=deliverable,
        note_title=note_title,
    )
    print(f"      Note saved: {note_path.relative_to(vault_root)}\n")

    # ── Cleanup temp transcripts ───────────────────────────────────────────────
    _cleanup(yt_result.transcript_dir)

    result = PipelineResult(
        topic=topic,
        videos_processed=len(yt_result.transcript_files),
        note_path=note_path,
        deliverable_path=nlm_result.output_path,
        deliverable_type=deliverable,
        notebook_id=nlm_result.notebook_id,
    )

    _print_summary(result, vault_root)
    return result


# ── Helpers ────────────────────────────────────────────────────────────────────

def _slug(text: str) -> str:
    import re
    return re.sub(r"[^\w]+", "-", text.lower()).strip("-")


def _build_takeaways(yt_result: youtube.SearchResult) -> list[str]:
    """Generate starter takeaways from video metadata (titles + view counts)."""
    if not yt_result.videos:
        return []
    top = sorted(yt_result.videos, key=lambda v: v.view_count, reverse=True)[:5]
    return [f"{v.title} ({v.view_count:,} views)" for v in top]


def _cleanup(transcript_dir: Path) -> None:
    if transcript_dir.exists():
        shutil.rmtree(transcript_dir, ignore_errors=True)
        print(f"      Cleaned up: {transcript_dir}")


def _print_summary(result: PipelineResult, vault_root: Path) -> None:
    print(f"\n{'='*55}")
    print(f"  PIPELINE COMPLETE")
    print(f"{'='*55}")
    print(f"  Topic:      {result.topic}")
    print(f"  Videos:     {result.videos_processed} processed")
    print(f"  Note:       {result.note_path.relative_to(vault_root)}")
    if result.deliverable_path:
        print(f"  Deliverable:{result.deliverable_path.relative_to(vault_root)}")
    print(f"  Notebook:   {result.notebook_id}")
    print(f"\n  Open Obsidian to see the new note and backlinks.\n")
