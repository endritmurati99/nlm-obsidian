"""
Setup script for the parallel research pipeline copy.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT / ".env"
ENV_EXAMPLE = ROOT / ".env.example"

sys.path.insert(0, str(ROOT))

from src.config import ensure_directories, load_config


GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
RESET = "\033[0m"


def ok(message: str) -> None:
    print(f"{GREEN}  OK {message}{RESET}")


def warn(message: str) -> None:
    print(f"{YELLOW}  !! {message}{RESET}")


def err(message: str) -> None:
    print(f"{RED}  XX {message}{RESET}")


def info(message: str) -> None:
    print(f"{CYAN}  -> {message}{RESET}")


def section(title: str) -> None:
    print(f"\n{CYAN}{'-' * 50}\n  {title}\n{'-' * 50}{RESET}")


def run(cmd: list[str]) -> tuple[int, str]:
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, (result.stdout + result.stderr).strip()


def cmd_exists(name: str) -> bool:
    return shutil.which(name) is not None


def pip_install(package: str) -> bool:
    info(f"Installing {package} ...")
    code, out = run([sys.executable, "-m", "pip", "install", "--upgrade", package])
    if code == 0:
        ok(f"{package} installed")
        return True
    warn(f"Install failed for {package}: {out}")
    return False


def check_python() -> bool:
    section("Python")
    major, minor = sys.version_info[:2]
    if (major, minor) < (3, 10):
        err(f"Python 3.10+ required (found {major}.{minor})")
        return False
    ok(f"Python {major}.{minor}")
    return True


def check_ytdlp(install: bool) -> bool:
    section("yt-dlp")
    if cmd_exists("yt-dlp"):
        code, out = run(["yt-dlp", "--version"])
        ok(f"yt-dlp available ({out[:30]})")
        return code == 0

    code, out = run([sys.executable, "-m", "yt_dlp", "--version"])
    if code == 0:
        ok(f"yt-dlp available via python module ({out[:30]})")
        return True

    warn("yt-dlp not found")
    if install:
        return pip_install("yt-dlp")
    return False


def check_pytest(install: bool) -> bool:
    section("pytest")
    code, _ = run([sys.executable, "-m", "pytest", "--version"])
    if code == 0:
        ok("pytest available")
        return True
    warn("pytest not found")
    if install:
        return pip_install("pytest")
    return False


def check_notebooklm(install: bool) -> bool:
    section("NotebookLM CLI")
    for binary in ("notebooklm", "notebook-lm"):
        if cmd_exists(binary):
            ok(f"{binary} found")
            status_code, status_out = run([binary, "status"])
            if status_code == 0:
                ok("NotebookLM authentication looks available")
            else:
                warn(f"{binary} found but not authenticated yet: {status_out}")
            return True

    warn("NotebookLM CLI not found")
    if not install:
        return False

    for package in ("notebooklm-py", "notebooklm", "notebook-lm-pi"):
        if pip_install(package):
            for binary in ("notebooklm", "notebook-lm"):
                if cmd_exists(binary):
                    ok(f"{binary} became available after installing {package}")
                    return True

    warn("Automatic NotebookLM installation did not succeed.")
    print("  Try a manual install, then run the login command in a separate terminal.")
    return False


def check_env() -> bool:
    section(".env file")
    if ENV_FILE.exists():
        ok(".env exists")
        return True
    if ENV_EXAMPLE.exists():
        shutil.copy(ENV_EXAMPLE, ENV_FILE)
        ok(".env created from .env.example")
        warn("Open .env if you want to override vault path or defaults.")
        return True
    err(".env.example missing")
    return False


def check_directories() -> bool:
    section("Vault directories")
    config = load_config()
    ensure_directories(config)
    ok(str(config.research_dir))
    ok(str(config.assets_dir))
    ok(str(config.transcript_root))
    return True


def check_skills() -> bool:
    section("Claude Code skills")
    required = [
        ROOT / ".claude" / "skills" / "youtube-search" / "SKILL.md",
        ROOT / ".claude" / "skills" / "notebooklm-pipeline" / "SKILL.md",
        ROOT / ".claude" / "skills" / "research-pipeline" / "SKILL.md",
    ]
    missing = [path for path in required if not path.exists()]
    if missing:
        for path in missing:
            err(f"Missing skill file: {path}")
        return False
    ok("All pipeline skills are present")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Parallel copy setup")
    parser.add_argument("--check-only", action="store_true", help="Only validate; do not install missing packages")
    args = parser.parse_args()

    install = not args.check_only

    print(f"\n{CYAN}Parallel Copy Setup{RESET}")
    print("=" * 50)
    if args.check_only:
        warn("Running in check-only mode")

    checks = {
        "python": check_python(),
        "yt-dlp": check_ytdlp(install),
        "pytest": check_pytest(install),
        "notebooklm": check_notebooklm(install),
        ".env": check_env(),
        "dirs": check_directories(),
        "skills": check_skills(),
    }

    section("Summary")
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        err(f"Missing or incomplete: {', '.join(failed)}")
        print("\nSuggested next step:")
        print("  py scripts/setup.py\n")
        return 1

    ok("Everything required for the local workflow is ready.")
    print("\nSuggested next step:")
    print('  py scripts/run_research.py "https://www.youtube.com/watch?v=VIDEO_ID" --skip-notebooklm\n')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
