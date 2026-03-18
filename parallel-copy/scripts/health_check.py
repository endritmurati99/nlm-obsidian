"""
Quick health check for the parallel research pipeline copy.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.config import ensure_directories, load_config


GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
RESET = "\033[0m"


def run(cmd: list[str]) -> tuple[int, str]:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        return 1, str(exc)
    return result.returncode, (result.stdout + result.stderr).strip()


def check(label: str, passed: bool, detail: str = "") -> bool:
    icon = f"{GREEN}OK{RESET}" if passed else f"{RED}NO{RESET}"
    line = f"  {icon}  {label}"
    if detail:
        line += f"  {CYAN}({detail}){RESET}"
    print(line)
    return passed


def main() -> int:
    print(f"\n{CYAN}Parallel Copy Health Check{RESET}")
    print("=" * 45)

    config = load_config()
    ensure_directories(config)

    checks = []
    checks.append(check("Python 3.10+", sys.version_info >= (3, 10), f"{sys.version_info.major}.{sys.version_info.minor}"))

    if shutil.which("yt-dlp"):
        code, out = run(["yt-dlp", "--version"])
        checks.append(check("yt-dlp", code == 0, out[:20] if code == 0 else out))
    else:
        code, out = run([sys.executable, "-m", "yt_dlp", "--version"])
        if code == 0:
            checks.append(check("yt-dlp", True, "available via python module"))
        else:
            checks.append(check("yt-dlp", False, "run: py -m pip install yt-dlp"))

    notebook_binary = "notebooklm" if shutil.which("notebooklm") else "notebook-lm" if shutil.which("notebook-lm") else None
    if notebook_binary:
        code, out = run([notebook_binary, "status"])
        checks.append(check("NotebookLM CLI", True, notebook_binary))
        checks.append(check("NotebookLM auth", code == 0, out if out else "login may still be required"))
    else:
        checks.append(check("NotebookLM CLI", False, "optional for full pipeline"))
        checks.append(check("NotebookLM auth", False, "skip with --skip-notebooklm if needed"))

    checks.append(check(".env file", (ROOT / ".env").exists(), str(ROOT / ".env")))
    checks.append(check("Research dir", config.research_dir.exists(), str(config.research_dir)))
    checks.append(check("Assets dir", config.assets_dir.exists(), str(config.assets_dir)))
    checks.append(check("Transcript dir", config.transcript_root.exists(), str(config.transcript_root)))

    for skill_name in ("youtube-search", "notebooklm-pipeline", "research-pipeline"):
        skill_file = ROOT / ".claude" / "skills" / skill_name / "SKILL.md"
        checks.append(check(f"skill: {skill_name}", skill_file.exists(), str(skill_file)))

    passed = sum(1 for item in checks if item)
    total = len(checks)
    print(f"\n  {passed}/{total} checks passed")

    if passed == total:
        print("\n  Ready for a full skill-driven run.\n")
        return 0

    print("\n  Not fully ready yet. Run: py scripts/setup.py\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
