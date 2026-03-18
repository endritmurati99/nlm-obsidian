"""
NotebookLM integration module.
Wraps the notebooklm CLI (from notebooklm-py) to create notebooks,
add sources, and generate deliverables — all compute runs on Google's servers.
"""

import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

# Expected generation times in seconds (used for progress messaging only)
GENERATION_TIMES = {
    "infographic": 6 * 60,
    "podcast":     8 * 60,
    "slides":      15 * 60,
    "mindmap":     5 * 60,
    "flashcards":  5 * 60,
    "audio":       8 * 60,
}

DELIVERABLE_EXTENSIONS = {
    "infographic": [".png", ".pdf"],
    "podcast":     [".mp3"],
    "slides":      [".pdf"],
    "mindmap":     [".png", ".svg"],
    "flashcards":  [".pdf", ".json"],
    "audio":       [".mp3"],
}


@dataclass
class NotebookResult:
    notebook_id: str
    deliverable_type: str
    output_path: Path | None
    status: str  # "complete" | "error"
    message: str = ""


# ── Internal helpers ───────────────────────────────────────────────────────────

def _require_cli() -> str:
    """Return the notebooklm binary name or exit with instructions."""
    for name in ("notebooklm", "notebook-lm"):
        if shutil.which(name):
            return name
    sys.exit(
        "notebooklm CLI not found.\n"
        "Install it from: https://github.com/teng-lin/notebooklm-py\n"
        "  pip install notebooklm-py\n"
        "Then authenticate (in a SEPARATE terminal, NOT inside Claude Code):\n"
        "  notebooklm login"
    )


def _run(cmd: list[str]) -> tuple[int, str]:
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, (result.stdout + result.stderr).strip()


def _find_output(output_dir: Path, stem: str, deliverable: str) -> Path | None:
    """Search for the generated deliverable file by stem + known extensions."""
    for ext in DELIVERABLE_EXTENSIONS.get(deliverable, []):
        candidate = output_dir / f"{stem}{ext}"
        if candidate.exists():
            return candidate
    # Fallback: any file in output_dir matching the stem
    matches = list(output_dir.glob(f"{stem}*"))
    return matches[0] if matches else None


# ── Public API ─────────────────────────────────────────────────────────────────

def create_notebook(title: str) -> str:
    """Create a new NotebookLM notebook and return its notebook_id."""
    cli = _require_cli()
    code, out = _run([cli, "create", "--title", title])
    if code != 0:
        raise RuntimeError(f"Failed to create notebook '{title}':\n{out}")
    # Parse notebook_id from output (expected: "notebook_id: <id>" or just the id)
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("notebook_id:"):
            return line.split(":", 1)[1].strip()
        if line and not line.startswith("#"):
            return line  # assume bare id
    raise RuntimeError(f"Could not parse notebook_id from output:\n{out}")


def add_source(notebook_id: str, source: Path) -> None:
    """Add a text file as a source to the notebook."""
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
    """
    Request a deliverable from NotebookLM and wait for completion.

    Args:
        notebook_id:  ID returned by create_notebook().
        deliverable:  One of infographic | podcast | slides | mindmap | flashcards | audio.
        output_dir:   Local directory to save the result.
        title:        Used to name the output file.

    Returns:
        Path to the saved deliverable, or None if the file can't be located.
    """
    cli = _require_cli()
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = f"{title}-{deliverable}"
    out_prefix = str(output_dir / stem)

    est = GENERATION_TIMES.get(deliverable, 300)
    print(f"  Generating {deliverable} (estimated ~{est // 60} min) — do not cancel…")

    code, out = _run([
        cli, "generate",
        "--notebook-id", notebook_id,
        "--type", deliverable,
        "--output", out_prefix,
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
    Full NotebookLM pipeline: create notebook → add sources → generate deliverable.

    Args:
        title:        Notebook/research title.
        source_files: List of .txt transcript or document paths (up to 50).
        deliverable:  Output format.
        output_dir:   Where to save the deliverable.
    """
    if not source_files:
        return NotebookResult(
            notebook_id="",
            deliverable_type=deliverable,
            output_path=None,
            status="error",
            message="No source files provided.",
        )

    notebook_id = create_notebook(title)
    print(f"  Created notebook: {notebook_id}")

    for src in source_files[:50]:  # NLM limit: 50 sources per notebook
        add_source(notebook_id, src)
        print(f"  Added source: {src.name}")

    output_path = generate(notebook_id, deliverable, output_dir, title)

    return NotebookResult(
        notebook_id=notebook_id,
        deliverable_type=deliverable,
        output_path=output_path,
        status="complete",
    )
