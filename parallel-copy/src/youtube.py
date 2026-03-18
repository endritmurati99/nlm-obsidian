"""
YouTube search and transcript extraction module.

Supports either a search query or a direct YouTube URL. Transcripts are saved as
clean .txt files for downstream processing.
"""

from __future__ import annotations

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
    mode: str
    source_arg: str
    videos: list[VideoMeta] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def transcript_files(self) -> list[Path]:
        return [video.transcript_path for video in self.videos if video.transcript_path]


YOUTUBE_URL_RE = re.compile(r"^(https?://)?(www\.)?(youtube\.com|youtu\.be)/", re.IGNORECASE)


def _resolve_ytdlp_command() -> list[str]:
    if shutil.which("yt-dlp"):
        return ["yt-dlp"]

    code, _ = _run([sys.executable, "-m", "yt_dlp", "--version"])
    if code == 0:
        return [sys.executable, "-m", "yt_dlp"]

    return []


def _require_ytdlp() -> list[str]:
    command = _resolve_ytdlp_command()
    if not command:
        sys.exit(
            "yt-dlp not found. Install it with:\n"
            "  py -m pip install yt-dlp\n"
            "Then re-run the pipeline."
        )
    return command


def _run(cmd: list[str], cwd: Path | None = None) -> tuple[int, str]:
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    return result.returncode, (result.stdout + result.stderr).strip()


def _clean_srt(srt_path: Path) -> str:
    """Strip timestamps and deduplicate consecutive lines from an SRT file."""
    text = srt_path.read_text(encoding="utf-8", errors="ignore")
    text = re.sub(r"^\d+\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}", "", text)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return ""
    deduped = [lines[0]] + [line for index, line in enumerate(lines[1:]) if line != lines[index]]
    return " ".join(deduped)


def _parse_metadata_line(line: str) -> VideoMeta | None:
    parts = line.strip().split("\t")
    if len(parts) < 5:
        return None
    video_id, title, url, views_raw, upload_date = parts[:5]
    try:
        view_count = int(views_raw)
    except ValueError:
        view_count = 0
    return VideoMeta(
        video_id=video_id,
        title=title,
        url=url,
        view_count=view_count,
        upload_date=upload_date,
    )


def _build_source_arg(query: str, max_results: int) -> tuple[str, str]:
    if YOUTUBE_URL_RE.match(query.strip()):
        return query.strip(), "url"
    return f"ytsearch{max_results}:{query}", "search"


def _find_srt_file(output_dir: Path, video_id: str) -> Path | None:
    preferred = [
        output_dir / f"{video_id}.en.srt",
        output_dir / f"{video_id}.en-US.srt",
        output_dir / f"{video_id}.en-GB.srt",
        output_dir / f"{video_id}.srt",
    ]
    for candidate in preferred:
        if candidate.exists():
            return candidate

    matches = sorted(output_dir.glob(f"{video_id}*.srt"))
    return matches[0] if matches else None


def search(query: str, max_results: int = 5, output_dir: Path | None = None) -> SearchResult:
    """
    Search YouTube for *query* or process a direct video URL.

    Args:
        query: Search terms or direct YouTube URL.
        max_results: Number of videos to process for search queries.
        output_dir: Directory for transcripts. Defaults to tmp/transcripts/<slug>.
    """
    ytdlp = _require_ytdlp()
    max_results = min(max(1, max_results), 20)

    slug = re.sub(r"[^\w]+", "-", query.lower()).strip("-") or "youtube-source"
    if output_dir is None:
        output_dir = Path("tmp") / "transcripts" / slug
    output_dir.mkdir(parents=True, exist_ok=True)

    source_arg, mode = _build_source_arg(query, max_results)
    warnings: list[str] = []

    metadata_file = output_dir / "metadata.tsv"
    metadata_code, metadata_output = _run([
        *ytdlp,
        source_arg,
        "--skip-download",
        "--print",
        "%(id)s\t%(title)s\t%(webpage_url)s\t%(view_count)s\t%(upload_date)s",
        "--no-playlist",
    ])
    if metadata_code != 0:
        raise RuntimeError(f"yt-dlp metadata collection failed for '{query}':\n{metadata_output}")
    metadata_file.write_text(metadata_output, encoding="utf-8")

    videos: list[VideoMeta] = []
    for line in metadata_output.splitlines():
        meta = _parse_metadata_line(line)
        if meta:
            videos.append(meta)

    if not videos:
        raise RuntimeError(f"No videos found for '{query}'.")

    download_code, download_output = _run([
        *ytdlp,
        source_arg,
        "--skip-download",
        "--write-auto-sub",
        "--write-sub",
        "--sub-lang",
        "en,en-US,en-GB",
        "--sub-format",
        "ttml",
        "--convert-subs",
        "srt",
        "--no-playlist",
        "--sleep-interval",
        "1",
        "--max-sleep-interval",
        "3",
        "-o",
        str(output_dir / "%(id)s.%(ext)s"),
    ])
    if download_code != 0 and download_output:
        warnings.append(download_output)

    for video in videos:
        srt_file = _find_srt_file(output_dir, video.video_id)
        if not srt_file:
            warnings.append(f"No transcript found for {video.title} ({video.video_id}).")
            continue

        clean_text = _clean_srt(srt_file)
        if not clean_text:
            warnings.append(f"Transcript file was empty for {video.title} ({video.video_id}).")
            continue

        txt_path = output_dir / f"{video.video_id}.txt"
        txt_path.write_text(clean_text, encoding="utf-8")
        video.transcript_path = txt_path

    result = SearchResult(
        query=query,
        transcript_dir=output_dir,
        mode=mode,
        source_arg=source_arg,
        videos=videos,
        warnings=warnings,
    )

    if not result.transcript_files:
        details = "\n".join(warnings) if warnings else "yt-dlp did not produce usable subtitle files."
        raise RuntimeError(f"No transcripts were captured for '{query}'.\n{details}")

    return result
