"""
Deterministic entry point for the notebooklm-pipeline skill.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.config import ensure_directories, load_config
from src.notebooklm import run_pipeline


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a NotebookLM deliverable job")
    parser.add_argument("title", help="Notebook title")
    parser.add_argument("source_files", nargs="+", type=Path, help="One or more source text files")
    parser.add_argument("--deliverable", default=None, help="Deliverable type")
    parser.add_argument("--output-dir", type=Path, default=None, help="Optional output directory")
    args = parser.parse_args()

    config = load_config()
    ensure_directories(config)

    result = run_pipeline(
        title=args.title,
        source_files=args.source_files,
        deliverable=args.deliverable or config.default_deliverable,
        output_dir=args.output_dir or config.assets_dir,
    )

    payload = {
        "notebook_id": result.notebook_id,
        "deliverable_type": result.deliverable_type,
        "output_path": str(result.output_path) if result.output_path else None,
        "status": result.status,
        "message": result.message,
    }
    print(json.dumps(payload, indent=2))
    return 0 if result.status == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
