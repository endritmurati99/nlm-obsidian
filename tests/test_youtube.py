"""Unit tests for src/youtube.py — no network calls."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.youtube import _clean_srt, _parse_metadata_line, VideoMeta


# ── _clean_srt ─────────────────────────────────────────────────────────────────

def test_clean_srt_removes_timestamps(tmp_path):
    srt = tmp_path / "sample.srt"
    srt.write_text(
        "1\n00:00:01,000 --> 00:00:03,000\nHello world\n\n"
        "2\n00:00:04,000 --> 00:00:06,000\nHello world\n\n"
        "3\n00:00:07,000 --> 00:00:09,000\nFoo bar\n",
        encoding="utf-8",
    )
    result = _clean_srt(srt)
    assert "00:00" not in result
    assert "Hello world" in result
    assert "Foo bar" in result


def test_clean_srt_deduplicates_consecutive():
    from pathlib import Path
    import tempfile, os
    with tempfile.NamedTemporaryFile(suffix=".srt", delete=False, mode="w", encoding="utf-8") as f:
        f.write("1\n00:00:01,000 --> 00:00:02,000\nDuplicate\n\n"
                "2\n00:00:03,000 --> 00:00:04,000\nDuplicate\n\n"
                "3\n00:00:05,000 --> 00:00:06,000\nUnique\n")
        name = f.name
    result = _clean_srt(Path(name))
    os.unlink(name)
    # "Duplicate" should appear only once
    assert result.count("Duplicate") == 1
    assert "Unique" in result


def test_clean_srt_empty_file(tmp_path):
    srt = tmp_path / "empty.srt"
    srt.write_text("", encoding="utf-8")
    assert _clean_srt(srt) == ""


# ── _parse_metadata_line ───────────────────────────────────────────────────────

def test_parse_metadata_line_valid():
    line = "abc123\tMy Video Title\thttps://youtu.be/abc123\t12345\t20240101"
    meta = _parse_metadata_line(line)
    assert meta is not None
    assert meta.video_id == "abc123"
    assert meta.title == "My Video Title"
    assert meta.view_count == 12345
    assert meta.upload_date == "20240101"


def test_parse_metadata_line_invalid_views():
    line = "abc123\tTitle\thttps://youtu.be/abc123\tN/A\t20240101"
    meta = _parse_metadata_line(line)
    assert meta is not None
    assert meta.view_count == 0


def test_parse_metadata_line_too_short():
    assert _parse_metadata_line("only\ttwo") is None
