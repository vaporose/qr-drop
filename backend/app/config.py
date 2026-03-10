"""
Configuration module for QR Drop.

Dynaconf settings are loaded from /backend/config/settings.toml and
/backend/config/.secrets.toml. root_path is resolved relative to this
file's location at /backend/app/config.py.
"""

from dynaconf import Dynaconf
from pathlib import Path

SETTINGS = Dynaconf(
    envvar_prefix="APP",
    settings_files=["settings.toml", ".secrets.toml"],
    load_dotenv=True,
    default_env="default",
    environments=True,
    root_path=Path(__file__).parent.parent / "config",
)

