"""
Setup script for the NLM+Obsidian research pipeline.
Run this once before using the research-pipeline skill.

Usage:
    python scripts/setup.py
    python scripts/setup.py --check-only
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
ENV_FILE = ROOT / ".env"
ENV_EXAMPLE = ROOT / ".env.example"

# ── Colours ───────────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
RESET  = "\033[0m"

def ok(msg):  print(f"{GREEN}  ✓ {msg}{RESET}")
def warn(msg): print(f"{YELLOW}  ! {msg}{RESET}")
def err(msg):  print(f"{RED}  ✗ {msg}{RESET}")
def info(msg): print(f"{CYAN}  → {msg}{RESET}")
def section(title): print(f"\n{CYAN}{'─'*50}\n  {title}\n{'─'*50}{RESET}")

# ── Helpers ───────────────────────────────────────────────────────────────────

def run(cmd: list[str], capture=True) -> tuple[int, str]:
    result = subprocess.run(cmd, capture_output=capture, text=True)
    return result.returncode, (result.stdout + result.stderr).strip()

def pip_install(package: str) -> bool:
    info(f"Installing {package} ...")
    code, out = run([sys.executable, "-m", "pip", "install", "--upgrade", package])
    if code == 0:
        ok(f"{package} installed")
        return True
    err(f"Failed to install {package}:\n{out}")
    return False

def cmd_exists(name: str) -> bool:
    return shutil.which(name) is not None

# ── Checks ────────────────────────────────────────────────────────────────────

def check_python() -> bool:
    section("Python")
    major, minor = sys.version_info[:2]
    if major < 3 or minor < 10:
        err(f"Python 3.10+ required (found {major}.{minor})")
        return False
    ok(f"Python {major}.{minor}")
    return True

def check_ytdlp(install: bool) -> bool:
    section("yt-dlp  (YouTube transcript extraction)")
    if cmd_exists("yt-dlp"):
        code, ver = run(["yt-dlp", "--version"])
        ok(f"yt-dlp {ver}")
        return True
    warn("yt-dlp not found")
    if install:
        return pip_install("yt-dlp")
    err("Install with: pip install yt-dlp")
    return False

def check_notebooklm(install: bool) -> bool:
    section("notebooklm-pi  (NotebookLM CLI wrapper)")

    # Try both known binary names
    for binary in ("notebooklm", "notebook-lm"):
        if cmd_exists(binary):
            ok(f"{binary} found")
            _check_notebooklm_auth(binary)
            return True

    warn("notebooklm CLI not found")

    if install:
        # Try the most likely PyPI package names
        for pkg in ("notebooklm", "notebook-lm-pi"):
            if pip_install(pkg):
                if cmd_exists("notebooklm"):
                    _check_notebooklm_auth("notebooklm")
                    return True

        # Fallback: manual instructions
        print()
        warn("Could not install via pip. Install manually:")
        print("""
  Option A – pip (try these in order until one works):
      pip install notebooklm
      pip install notebook-lm-pi

  Option B – from source (GitHub):
      git clone https://github.com/teng-lin/notebooklm-py
      cd notebooklm-py
      pip install -e .

  After installing, run in a SEPARATE terminal (not inside Claude Code):
      notebooklm login
        """)
        return False

    err("Install with: pip install notebooklm")
    return False

def _check_notebooklm_auth(binary: str):
    info("Checking NotebookLM authentication ...")
    code, out = run([binary, "status"])
    if code == 0 and "logged" in out.lower():
        ok("Authenticated with Google")
    else:
        warn("Not authenticated yet — run this in a SEPARATE terminal:")
        print(f"\n      {binary} login\n")
        print("  This opens your browser for Google OAuth.")
        print("  Do NOT run it inside the Claude Code terminal.")

def check_env() -> bool:
    section(".env file")
    if ENV_FILE.exists():
        ok(".env exists")
        return True
    if ENV_EXAMPLE.exists():
        import shutil as sh
        sh.copy(ENV_EXAMPLE, ENV_FILE)
        ok(".env created from .env.example")
        warn("Open .env and fill in VAULT_PATH and GOOGLE_ACCOUNT")
        return True
    warn(".env.example missing — skipping")
    return False

def check_vault_dirs() -> bool:
    section("Vault directories")
    dirs = [
        ROOT / "Research",
        ROOT / "Research" / "assets",
        ROOT / "tmp" / "transcripts",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        ok(str(d.relative_to(ROOT)))
    return True

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="NLM+Obsidian pipeline setup")
    parser.add_argument("--check-only", action="store_true",
                        help="Only check — do not install anything")
    args = parser.parse_args()

    install = not args.check_only

    print(f"\n{CYAN}NLM+Obsidian Pipeline Setup{RESET}")
    print("=" * 50)
    if args.check_only:
        warn("Running in check-only mode (no installs)")

    results = {
        "Python 3.10+":   check_python(),
        "yt-dlp":         check_ytdlp(install),
        "notebooklm-pi":  check_notebooklm(install),
        ".env":           check_env(),
        "Vault dirs":     check_vault_dirs(),
    }

    # ── Summary ───────────────────────────────────────────────────────────────
    section("Summary")
    all_ok = True
    for name, passed in results.items():
        if passed:
            ok(name)
        else:
            err(name)
            all_ok = False

    print()
    if all_ok:
        print(f"{GREEN}All checks passed. Pipeline is ready.{RESET}")
        print("\nTo run the pipeline, open Claude Code from this directory and say:")
        print('  "research Claude Code MCP servers and make an infographic"\n')
    else:
        print(f"{YELLOW}Some checks failed. Fix the errors above, then re-run:{RESET}")
        print("  python scripts/setup.py\n")

    sys.exit(0 if all_ok else 1)

if __name__ == "__main__":
    main()
