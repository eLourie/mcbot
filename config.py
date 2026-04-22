"""Application configuration — loads and validates all settings from .env."""

import os
import sys
import warnings

# Suppress paramiko TripleDES deprecation warnings (fixed in future paramiko versions)
warnings.filterwarnings("ignore", message=".*TripleDES.*")

from dotenv import load_dotenv

load_dotenv()


def _require(name: str) -> str:
    """Get a required env variable or exit with an error message."""
    value = os.getenv(name)
    if not value:
        sys.exit(f"Missing required environment variable: {name}")
    return value


# Telegram
TELEGRAM_TOKEN: str = _require("TELEGRAM_TOKEN")

# Timeweb Cloud API
TIMEWEB_API_TOKEN: str = _require("TIMEWEB_API_TOKEN")
TIMEWEB_API_BASE: str = "https://api.timeweb.cloud/api/v1"
SERVER_ID: str = _require("SERVER_ID")

# Initial user whitelist (seeded into allowed_users.json on first run)
ALLOWED_USERS: list[int] = [
    int(uid.strip())
    for uid in _require("ALLOWED_USERS").split(",")
    if uid.strip()
]

# SSH connection to VPS
SSH_HOST: str = _require("SSH_HOST")
SSH_USER: str = _require("SSH_USER")
SSH_PASSWORD: str = _require("SSH_PASSWORD")

# Minecraft server settings
MINECRAFT_DIR: str = os.getenv("MINECRAFT_DIR", "/opt/minecraft")
MINECRAFT_RAM_MAX: str = os.getenv("MINECRAFT_RAM_MAX", "2G")
MINECRAFT_RAM_MIN: str = os.getenv("MINECRAFT_RAM_MIN", "1G")

# How long to wait for VPS to boot before giving up (seconds)
VPS_BOOT_TIMEOUT: int = int(os.getenv("VPS_BOOT_TIMEOUT", "120"))
