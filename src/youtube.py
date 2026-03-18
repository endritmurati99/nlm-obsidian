"""
YouTube search and transcript extraction module.
Uses yt-dlp to search, download subtitles, and produce clean .txt transcripts.
"""

import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class VideoMeta:
    video_id: str
    title: str
    url: str
    view_count: int
    upload_date: str
    transcript_path: Path | None = None


@dataclass
class SearchResult:
    query: str
    transcript_dir: Path
    videos: list[VideoMeta] = field(default_factory=list)

    @property
    def transcript_files(self) -> list[Path]:
        return [v.transcript_path for v in self.videos if v.transcript_path]


# ── Internal helpers ───────────────────────────────────────────────────────────

def _require_ytdlp() -> None:
    if not shutil.which("yt-dlp"):
        sys.exit(
            "yt-dlp not found. Install it with:\n"
            "  pip install yt-dlp\n"
            "Then re-run the pipeline."
        )


def _run(cmd: list[str], cwd: Path | None = None) -> tuple[int, str]:
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    return result.returncode, (result.stdout + result.stderr).strip()


def _clean_srt(srt_path: Path) -> str:
    """Strip timestamps and deduplicate consecutive lines from an SRT file."""
    text = srt_path.read_text(encoding="utf-8", errors="ignore")
    text = re.sub(r"^\d+\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}", "", text)
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if not lines:
        return ""
    deduped = [lines[0]] + [l for i, l in enumerate(lines[1:]) if l != lines[i]]
    return " ".join(deduped)


def _parse_metadata_line(line: str) -> VideoMeta | None:
    parts = line.strip().split("\t")
    if len(parts) < 5:
        return None
    video_id, title, url, views_raw, date = parts[:5]
    try:
        views = int(views_raw)
    except ValueError:
        views = 0
    return VideoMeta(
        video_id=video_id,
        title=title,
        url=url,
        view_count=views,
        upload_date=date,
    )


# ── Public API ─────────────────────────────────────────────────────────────────

def search(query: str, max_results: int = 5, output_dir: Path | None = None) -> SearchResult:
    """
    Search YouTube for *query*, download transcripts, and return a SearchResult.

    Args:
        query:       Search terms, e.g. "Claude Code MCP servers"
        max_results: Number of videos to process (default 5, max 20).
        output_dir:  Directory for transcripts. Defaults to tmp/transcripts/<slug>.
    """
    _require_ytdlp()
    max_results = min(max(1, max_results), 20)

    slug = re.sub(r"[^\w]+", "-", query.lower()).strip("-")
    if output_dir is None:
        output_dir = Path("tmp") / "transcripts" / slug
    output_dir.mkdir(parents=True, exist_ok=True)

    search_arg = f"ytsearch{max_results}:{query}"

    # Step 1 — collect metadata
    metadata_file = output_dir / "metadata.tsv"
    _run([
        "yt-dlp", search_arg,
        "--skip-download",
        "--print", "%(id)s\t%(title)s\t%(webpage_url)s\t%(view_count)s\t%(upload_date)s",
        "--no-playlist",
    ] + [">", str(metadata_file)],
    )
    # yt-dlp --print goes to stdout; capture it properly
    code, stdout = _run([
        "yt-dlp", search_arg,
        "--skip-download",
        "--print", "%(id)s\t%(title)s\t%(webpage_url)s\t%(view_count)s\t%(upload_date)s",
        "--no-playlist",
    ])
    metadata_file.write_text(stdout, encoding="utf-8")

    videos: list[VideoMeta] = []
    for line in stdout.splitlines():
        meta = _parse_metadata_line(line)
        if meta:
            videos.append(meta)

    # Step 2 — download transcripts
    _run([
        "yt-dlp", search_arg,
        "--skip-download",
        "--write-auto-sub",
        "--write-sub",
        "--sub-lang", "en,en-US,en-GB",
        "--sub-format", "ttml",
        "--convert-subs", "srt",
        "--no-playlist",
        "--sleep-interval", "1",
        "--max-sleep-interval", "3",
        "-o", str(output_dir / "%(id)s.%(ext)s"),
    ])

    # Step 3 — clean each SRT → .txt
    for video in videos:
        srt_file = output_dir / f"{video.video_id}.en.srt"
        if not srt_file.exists():
            # Try without language suffix
            srt_file = output_dir / f"{video.video_id}.srt"
        if srt_file.exists():
            clean_text = _clean_srt(srt_file)
            if clean_text:
                txt_path = output_dir / f"{video.video_id}.txt"
                txt_path.write_text(clean_text, encoding="utf-8")
                video.transcript_path = txt_path

    return SearchResult(query=query, transcript_dir=output_dir, videos=videos)
