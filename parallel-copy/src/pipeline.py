"""
Research pipeline orchestrator.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from . import notebooklm, vault, youtube


@dataclass
class PipelineResult:
    topic: str
    source_mode: str
    videos_found: int
    videos_processed: int
    note_path: Path
    deliverable_path: Path | None
    deliverable_type: str
    notebook_id: str
    notebooklm_status: str


def run(
    topic: str,
    vault_root: Path,
    max_videos: int = 5,
    deliverable: str = "infographic",
    note_title: str | None = None,
    run_notebooklm: bool = True,
    keep_transcripts: bool = False,
) -> PipelineResult:
    """
    Run the full research pipeline end-to-end.
    """
    print(f"\n{'=' * 55}")
    print(f"  PIPELINE START: {topic}")
    print(f"{'=' * 55}\n")

    print(f"[1/3] YouTube Search  (max {max_videos} videos)")
    yt_result = youtube.search(
        query=topic,
        max_results=max_videos,
        output_dir=vault_root / "tmp" / "transcripts" / _slug(topic),
    )
    print(f"      Found {len(yt_result.videos)} videos, {len(yt_result.transcript_files)} transcripts downloaded.\n")

    if not yt_result.transcript_files:
        raise RuntimeError(f"No transcripts were captured for '{topic}'.")

    if run_notebooklm:
        print(f"[2/3] NotebookLM Analysis  (deliverable: {deliverable})")
        nlm_result = notebooklm.run_pipeline(
            title=f"Research: {topic}",
            source_files=yt_result.transcript_files,
            deliverable=deliverable,
            output_dir=vault_root / "Research" / "assets",
        )
        print(f"      Notebook ID: {nlm_result.notebook_id or 'n/a'}")
        print(f"      Deliverable: {nlm_result.output_path}\n")
        if nlm_result.status != "complete":
            raise RuntimeError(nlm_result.message or "NotebookLM step failed.")
    else:
        print("[2/3] NotebookLM Analysis  (skipped by request)")
        nlm_result = notebooklm.NotebookResult(
            notebook_id="",
            deliverable_type=deliverable,
            output_path=None,
            status="skipped",
            message="NotebookLM step was skipped.",
        )
        print("      NotebookLM step skipped.\n")

    print("[3/3] Writing Obsidian note")
    takeaways = _build_takeaways(yt_result)
    analysis_text = _build_analysis_text(yt_result, nlm_result)

    note_path = vault.write_research_note(
        vault_root=vault_root,
        topic=topic,
        videos=yt_result.videos,
        key_takeaways=takeaways,
        analysis_text=analysis_text,
        deliverable_path=nlm_result.output_path,
        deliverable_type=deliverable,
        note_title=note_title,
        source_mode=yt_result.mode,
        notebook_id=nlm_result.notebook_id,
        notebooklm_status=nlm_result.status,
        notebooklm_message=nlm_result.message,
    )
    print(f"      Note saved: {note_path.relative_to(vault_root)}\n")

    if not keep_transcripts:
        _cleanup(yt_result.transcript_dir)

    result = PipelineResult(
        topic=topic,
        source_mode=yt_result.mode,
        videos_found=len(yt_result.videos),
        videos_processed=len(yt_result.transcript_files),
        note_path=note_path,
        deliverable_path=nlm_result.output_path,
        deliverable_type=deliverable,
        notebook_id=nlm_result.notebook_id,
        notebooklm_status=nlm_result.status,
    )

    _print_summary(result, vault_root)
    return result


def _slug(text: str) -> str:
    import re

    return re.sub(r"[^\w]+", "-", text.lower()).strip("-")


def _build_takeaways(yt_result: youtube.SearchResult) -> list[str]:
    """Generate honest, source-based takeaways without inventing NotebookLM output."""
    if not yt_result.videos:
        return []

    top = sorted(yt_result.videos, key=lambda video: video.view_count, reverse=True)[:5]
    takeaways = [f"{video.title} ({video.view_count:,} views)" for video in top]
    if yt_result.mode == "url":
        takeaways.insert(0, "Input was a direct YouTube URL, so the run focused on one specific source.")
    else:
        takeaways.insert(0, f"Input was a YouTube search query and returned {len(yt_result.videos)} candidate videos.")
    if yt_result.warnings:
        takeaways.append("Some sources had subtitle or transcript issues; see the Analysis section for details.")
    return takeaways[:7]


def _build_analysis_text(yt_result: youtube.SearchResult, nlm_result: notebooklm.NotebookResult) -> str:
    lines = [
        "### Pipeline Status",
        f"- YouTube mode: {yt_result.mode}",
        f"- Source argument: `{yt_result.source_arg}`",
        f"- Videos discovered: {len(yt_result.videos)}",
        f"- Transcripts captured: {len(yt_result.transcript_files)}",
        f"- NotebookLM status: {nlm_result.status}",
    ]

    if nlm_result.notebook_id:
        lines.append(f"- Notebook ID: `{nlm_result.notebook_id}`")
    if nlm_result.output_path:
        lines.append(f"- Deliverable path: `{nlm_result.output_path.as_posix()}`")
    if nlm_result.message:
        lines.append(f"- NotebookLM message: {nlm_result.message}")

    if yt_result.warnings:
        lines.append("")
        lines.append("### YouTube Warnings")
        lines.extend(f"- {warning}" for warning in yt_result.warnings)

    lines.append("")
    lines.append("### Transcript Files")
    lines.extend(f"- `{path.name}`" for path in yt_result.transcript_files)
    return "\n".join(lines)


def _cleanup(transcript_dir: Path) -> None:
    if transcript_dir.exists():
        shutil.rmtree(transcript_dir, ignore_errors=True)
        print(f"      Cleaned up: {transcript_dir}")


def _print_summary(result: PipelineResult, vault_root: Path) -> None:
    print(f"\n{'=' * 55}")
    print("  PIPELINE COMPLETE")
    print(f"{'=' * 55}")
    print(f"  Topic:      {result.topic}")
    print(f"  Mode:       {result.source_mode}")
    print(f"  Found:      {result.videos_found} videos")
    print(f"  Videos:     {result.videos_processed} processed")
    print(f"  Note:       {result.note_path.relative_to(vault_root)}")
    if result.deliverable_path:
        print(f"  Deliverable:{result.deliverable_path.relative_to(vault_root)}")
    print(f"  NotebookLM: {result.notebooklm_status}")
    print(f"  Notebook:   {result.notebook_id}")
    print("\n  Open Obsidian to see the new note and backlinks.\n")
