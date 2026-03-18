"""
Shared configuration for the parallel research pipeline copy.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT / ".env"


@dataclass(slots=True)
class PipelineConfig:
    root: Path
    vault_root: Path
    default_deliverable: str
    default_max_results: int
    google_account: str

    @property
    def research_dir(self) -> Path:
        return self.vault_root / "Research"

    @property
    def assets_dir(self) -> Path:
        return self.research_dir / "assets"

    @property
    def transcript_root(self) -> Path:
        return self.vault_root / "tmp" / "transcripts"


def _read_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("'").strip('"')
    return values


def _get_setting(env_values: dict[str, str], key: str, default: str = "") -> str:
    return os.getenv(key) or env_values.get(key, default)


def _parse_int(raw: str, default: int) -> int:
    try:
        return int(raw)
    except (TypeError, ValueError):
        return default


def load_config(vault_root: Path | None = None) -> PipelineConfig:
    env_values = _read_env_file(ENV_FILE)
    vault_value = str(vault_root) if vault_root else _get_setting(env_values, "VAULT_PATH", str(ROOT))

    return PipelineConfig(
        root=ROOT,
        vault_root=Path(vault_value).expanduser().resolve(),
        default_deliverable=_get_setting(env_values, "DEFAULT_DELIVERABLE", "infographic"),
        default_max_results=max(1, _parse_int(_get_setting(env_values, "YT_MAX_RESULTS", "5"), 5)),
        google_account=_get_setting(env_values, "GOOGLE_ACCOUNT", ""),
    )


def ensure_directories(config: PipelineConfig) -> None:
    config.research_dir.mkdir(parents=True, exist_ok=True)
    config.assets_dir.mkdir(parents=True, exist_ok=True)
    config.transcript_root.mkdir(parents=True, exist_ok=True)
