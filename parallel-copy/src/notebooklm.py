"""
NotebookLM integration module.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


GENERATION_TIMES = {
    "infographic": 6 * 60,
    "podcast": 8 * 60,
    "slides": 15 * 60,
    "mindmap": 5 * 60,
    "flashcards": 5 * 60,
    "audio": 8 * 60,
}

DELIVERABLE_EXTENSIONS = {
    "infographic": [".png", ".pdf"],
    "podcast": [".mp3"],
    "slides": [".pdf"],
    "mindmap": [".png", ".svg"],
    "flashcards": [".pdf", ".json"],
    "audio": [".mp3"],
}


@dataclass
class NotebookResult:
    notebook_id: str
    deliverable_type: str
    output_path: Path | None
    status: str  # "complete" | "error" | "skipped"
    message: str = ""


def _require_cli() -> str:
    """Return the notebooklm binary name or exit with instructions."""
    for name in ("notebooklm", "notebook-lm"):
        if shutil.which(name):
            return name
    sys.exit(
        "notebooklm CLI not found.\n"
        "Install a compatible NotebookLM wrapper and authenticate outside Claude Code.\n"
        "Then re-run the pipeline."
    )


def _run(cmd: list[str]) -> tuple[int, str]:
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, (result.stdout + result.stderr).strip()


def _find_output(output_dir: Path, stem: str, deliverable: str) -> Path | None:
    for ext in DELIVERABLE_EXTENSIONS.get(deliverable, []):
        candidate = output_dir / f"{stem}{ext}"
        if candidate.exists():
            return candidate
    matches = list(output_dir.glob(f"{stem}*"))
    return matches[0] if matches else None


def create_notebook(title: str) -> str:
    cli = _require_cli()
    code, out = _run([cli, "create", "--title", title])
    if code != 0:
        raise RuntimeError(f"Failed to create notebook '{title}':\n{out}")

    for line in out.splitlines():
        stripped = line.strip()
        if stripped.startswith("notebook_id:"):
            return stripped.split(":", 1)[1].strip()
        if stripped and not stripped.startswith("#"):
            return stripped
    raise RuntimeError(f"Could not parse notebook_id from output:\n{out}")


def add_source(notebook_id: str, source: Path) -> None:
    cli = _require_cli()
    code, out = _run([cli, "add-source", "--notebook-id", notebook_id, "--file", str(source)])
    if code != 0:
        raise RuntimeError(f"Failed to add source {source.name}:\n{out}")


def generate(
    notebook_id: str,
    deliverable: str,
    output_dir: Path,
    title: str,
) -> Path | None:
    cli = _require_cli()
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = f"{title}-{deliverable}"
    out_prefix = str(output_dir / stem)

    est = GENERATION_TIMES.get(deliverable, 300)
    print(f"  Generating {deliverable} (estimated ~{est // 60} min) - do not cancel...")

    code, out = _run([
        cli,
        "generate",
        "--notebook-id",
        notebook_id,
        "--type",
        deliverable,
        "--output",
        out_prefix,
    ])
    if code != 0:
        raise RuntimeError(f"NotebookLM generation failed:\n{out}")

    return _find_output(output_dir, stem, deliverable)


def run_pipeline(
    title: str,
    source_files: list[Path],
    deliverable: str,
    output_dir: Path,
) -> NotebookResult:
    """
    Full NotebookLM pipeline: create notebook -> add sources -> generate deliverable.
    """
    if not source_files:
        return NotebookResult(
            notebook_id="",
            deliverable_type=deliverable,
            output_path=None,
            status="error",
            message="No source files provided.",
        )

    if deliverable not in DELIVERABLE_EXTENSIONS:
        return NotebookResult(
            notebook_id="",
            deliverable_type=deliverable,
            output_path=None,
            status="error",
            message=f"Unsupported deliverable type: {deliverable}",
        )

    notebook_id = create_notebook(title)
    print(f"  Created notebook: {notebook_id}")

    for src in source_files[:50]:
        add_source(notebook_id, src)
        print(f"  Added source: {src.name}")

    output_path = generate(notebook_id, deliverable, output_dir, title)
    if output_path is None:
        return NotebookResult(
            notebook_id=notebook_id,
            deliverable_type=deliverable,
            output_path=None,
            status="error",
            message="NotebookLM finished but no local deliverable file was found.",
        )

    return NotebookResult(
        notebook_id=notebook_id,
        deliverable_type=deliverable,
        output_path=output_path,
        status="complete",
    )
