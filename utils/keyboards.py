"""Inline keyboard layouts for confirmation prompts."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Confirmation buttons for /on command
CONFIRM_ON = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("Yes, start", callback_data="confirm_on"),
        InlineKeyboardButton("Cancel", callback_data="cancel"),
    ]
])

# Confirmation buttons for /off command
CONFIRM_OFF = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("Yes, stop", callback_data="confirm_off"),
        InlineKeyboardButton("Cancel", callback_data="cancel"),
    ]
])
