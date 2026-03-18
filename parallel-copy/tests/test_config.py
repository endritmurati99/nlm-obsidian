"""Tests for src/config.py."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import load_config


def test_load_config_uses_explicit_vault_root(tmp_path):
    config = load_config(tmp_path)
    assert config.vault_root == tmp_path.resolve()
    assert config.research_dir == tmp_path.resolve() / "Research"
    assert config.assets_dir == tmp_path.resolve() / "Research" / "assets"
    assert config.transcript_root == tmp_path.resolve() / "tmp" / "transcripts"
