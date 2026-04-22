"""Persistent user whitelist — stored in allowed_users.json.

On first run the file is seeded from ALLOWED_USERS in .env.
After that, users are managed dynamically via /adduser.
"""

import json
import os

from config import ALLOWED_USERS

_STORE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "allowed_users.json")


def _load() -> set[int]:
    """Load the whitelist from disk, or seed it from .env on first run."""
    if os.path.exists(_STORE_PATH):
        with open(_STORE_PATH) as f:
            return set(json.load(f))
    users = set(ALLOWED_USERS)
    _save(users)
    return users


def _save(users: set[int]) -> None:
    """Persist the current whitelist to disk."""
    with open(_STORE_PATH, "w") as f:
        json.dump(sorted(users), f)


# Load whitelist at import time
_users: set[int] = _load()


def is_allowed(user_id: int) -> bool:
    """Check if a user ID is in the whitelist."""
    return user_id in _users


def add_user(user_id: int) -> bool:
    """Add a user to the whitelist. Returns True if new, False if already existed."""
    if user_id in _users:
        return False
    _users.add(user_id)
    _save(_users)
    return True


def get_all_users() -> list[int]:
    """Return all whitelisted user IDs sorted."""
    return sorted(_users)
