"""
Deterministic entry point for the youtube-search skill.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.config import ensure_directories, load_config
from src.youtube import search


def main() -> int:
    parser = argparse.ArgumentParser(description="Run YouTube transcript ingestion")
    parser.add_argument("query", help="YouTube search query or direct video URL")
    parser.add_argument("--max-results", type=int, default=None, help="Maximum number of search results")
    parser.add_argument("--output-dir", type=Path, default=None, help="Optional transcript output directory")
    args = parser.parse_args()

    config = load_config()
    ensure_directories(config)

    result = search(
        query=args.query,
        max_results=args.max_results or config.default_max_results,
        output_dir=args.output_dir,
    )

    payload = {
        "query": result.query,
        "mode": result.mode,
        "source_arg": result.source_arg,
        "transcript_dir": str(result.transcript_dir),
        "transcript_files": [str(path) for path in result.transcript_files],
        "warnings": result.warnings,
        "videos": [
            {
                "video_id": video.video_id,
                "title": video.title,
                "url": video.url,
                "view_count": video.view_count,
                "upload_date": video.upload_date,
                "transcript_path": str(video.transcript_path) if video.transcript_path else None,
            }
            for video in result.videos
        ],
    }
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
