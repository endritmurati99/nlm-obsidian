"""
Quick health check for the research pipeline.
Run any time to verify all tools are reachable.

Usage:
    python scripts/health_check.py
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent

GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
RESET  = "\033[0m"

def run(cmd):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return r.returncode, (r.stdout + r.stderr).strip()
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        return 1, str(e)

checks = []

def check(label, passed, detail=""):
    icon = f"{GREEN}✓{RESET}" if passed else f"{RED}✗{RESET}"
    line = f"  {icon}  {label}"
    if detail:
        line += f"  {CYAN}({detail}){RESET}"
    print(line)
    checks.append(passed)

print(f"\n{CYAN}NLM+Obsidian — Pipeline Health Check{RESET}")
print("=" * 45)

# Python
check("Python 3.10+", sys.version_info >= (3, 10),
      f"{sys.version_info.major}.{sys.version_info.minor}")

# yt-dlp
if shutil.which("yt-dlp"):
    code, ver = run(["yt-dlp", "--version"])
    check("yt-dlp", code == 0, ver[:20] if code == 0 else "version check failed")
else:
    check("yt-dlp", False, "not found — run: pip install yt-dlp")

# notebooklm
nlm_bin = "notebooklm" if shutil.which("notebooklm") else \
          "notebook-lm" if shutil.which("notebook-lm") else None
if nlm_bin:
    code, out = run([nlm_bin, "--version"])
    check("notebooklm CLI", True, nlm_bin)
    # Auth
    code2, out2 = run([nlm_bin, "status"])
    authed = code2 == 0 and "logged" in out2.lower()
    check("notebooklm auth", authed,
          "authenticated" if authed else f"run: {nlm_bin} login (separate terminal)")
else:
    check("notebooklm CLI", False, "not found — run: pip install notebooklm")
    check("notebooklm auth", False, "CLI missing")

# .env
env_ok = (ROOT / ".env").exists()
check(".env file", env_ok, ".env" if env_ok else "copy .env.example → .env and fill in values")

# Vault directories
for d in ["Research", "Research/assets", ".claude/skills"]:
    path = ROOT / d
    check(f"vault/{d}", path.exists(), str(path))

# Skills
for skill in ["youtube-search", "notebooklm-pipeline", "research-pipeline"]:
    skill_file = ROOT / ".claude" / "skills" / skill / "SKILL.md"
    check(f"skill: {skill}", skill_file.exists())

# Summary
print()
passed = sum(checks)
total  = len(checks)
color  = GREEN if passed == total else (YELLOW if passed >= total - 2 else RED)
print(f"  {color}{passed}/{total} checks passed{RESET}")

if passed < total:
    print(f"\n  Run {CYAN}python scripts/setup.py{RESET} to fix missing dependencies.\n")
else:
    print(f"\n  {GREEN}Pipeline is ready.{RESET} Launch Claude Code from this directory.\n")

sys.exit(0 if passed == total else 1)
