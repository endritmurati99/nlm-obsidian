"""
Deterministic entry point for the research-pipeline skill.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.config import ensure_directories, load_config
from src.pipeline import run


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the full research pipeline")
    parser.add_argument("topic", help="YouTube search query or direct video URL")
    parser.add_argument("--max-videos", type=int, default=None, help="Maximum number of videos to process")
    parser.add_argument("--deliverable", default=None, help="Deliverable type for NotebookLM")
    parser.add_argument("--note-title", default=None, help="Optional note filename without .md")
    parser.add_argument("--skip-notebooklm", action="store_true", help="Only ingest YouTube content and write a note")
    parser.add_argument("--keep-transcripts", action="store_true", help="Do not delete transcript files after the run")
    parser.add_argument("--vault-root", type=Path, default=None, help="Override vault root for this run")
    args = parser.parse_args()

    config = load_config(args.vault_root)
    ensure_directories(config)

    result = run(
        topic=args.topic,
        vault_root=config.vault_root,
        max_videos=args.max_videos or config.default_max_results,
        deliverable=args.deliverable or config.default_deliverable,
        note_title=args.note_title,
        run_notebooklm=not args.skip_notebooklm,
        keep_transcripts=args.keep_transcripts,
    )

    payload = {
        "topic": result.topic,
        "source_mode": result.source_mode,
        "videos_found": result.videos_found,
        "videos_processed": result.videos_processed,
        "note_path": str(result.note_path),
        "deliverable_path": str(result.deliverable_path) if result.deliverable_path else None,
        "deliverable_type": result.deliverable_type,
        "notebook_id": result.notebook_id,
        "notebooklm_status": result.notebooklm_status,
    }
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
