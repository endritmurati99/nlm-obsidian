"""Unit tests for src/vault.py — filesystem only, no network."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.vault import write_research_note, _sanitize_filename, _find_backlinks
from src.youtube import VideoMeta


# ── _sanitize_filename ─────────────────────────────────────────────────────────

def test_sanitize_strips_special_chars():
    assert _sanitize_filename("Claude Code: MCP!") == "Claude Code MCP"

def test_sanitize_replaces_spaces():
    assert _sanitize_filename("hello world") == "hello-world"


# ── _find_backlinks ────────────────────────────────────────────────────────────

def test_find_backlinks_matches_note(tmp_path):
    (tmp_path / "Claude-Code.md").write_text("# Claude Code", encoding="utf-8")
    (tmp_path / "Unrelated.md").write_text("# Unrelated", encoding="utf-8")
    links = _find_backlinks(tmp_path, ["Claude"])
    assert "[[Claude-Code]]" in links
    assert "[[Unrelated]]" not in links

def test_find_backlinks_no_matches(tmp_path):
    (tmp_path / "Unrelated.md").write_text("# Unrelated", encoding="utf-8")
    links = _find_backlinks(tmp_path, ["MCP"])
    assert links == []


# ── write_research_note ────────────────────────────────────────────────────────

def _make_videos():
    return [
        VideoMeta("v1", "Intro to MCP", "https://youtu.be/v1", 5000, "20240101"),
        VideoMeta("v2", "Advanced MCP", "https://youtu.be/v2", 2000, "20240201"),
    ]


def test_write_research_note_creates_file(tmp_path):
    note = write_research_note(
        vault_root=tmp_path,
        topic="MCP Servers",
        videos=_make_videos(),
        key_takeaways=["Takeaway one", "Takeaway two"],
        analysis_text="Some analysis.",
        deliverable_path=None,
        deliverable_type="infographic",
    )
    assert note.exists()
    content = note.read_text(encoding="utf-8")
    assert "# MCP Servers" in content
    assert "Takeaway one" in content
    assert "Intro to MCP" in content


def test_write_research_note_embeds_image(tmp_path):
    assets = tmp_path / "Research" / "assets"
    assets.mkdir(parents=True)
    img = assets / "MCP-Servers-infographic.png"
    img.write_bytes(b"fake-png")

    note = write_research_note(
        vault_root=tmp_path,
        topic="MCP Servers",
        videos=_make_videos(),
        key_takeaways=[],
        analysis_text="",
        deliverable_path=img,
        deliverable_type="infographic",
    )
    content = note.read_text(encoding="utf-8")
    assert "![[" in content  # image embed syntax


def test_write_research_note_custom_title(tmp_path):
    note = write_research_note(
        vault_root=tmp_path,
        topic="MCP Servers",
        videos=[],
        key_takeaways=[],
        analysis_text="",
        deliverable_path=None,
        deliverable_type="infographic",
        note_title="custom-note-title",
    )
    assert note.stem == "custom-note-title"
