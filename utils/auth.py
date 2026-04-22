"""Authorization check — verifies the user is in the whitelist."""

from telegram import Update

from utils.user_store import is_allowed as _is_allowed


def is_allowed(update: Update) -> bool:
    """Check if the user who sent the update is whitelisted."""
    return update.effective_user is not None and _is_allowed(update.effective_user.id)
