"""Telegram command handlers — /start, /help, /on, /off, /status, /adduser."""

from telegram import Update
from telegram.ext import ContextTypes

from config import SSH_HOST
from utils.auth import is_allowed
from utils.user_store import add_user
from utils.keyboards import CONFIRM_ON, CONFIRM_OFF
from services.timeweb import get_server_status
from services.ssh_client import is_minecraft_running

HELP_TEXT = (
    "Minecraft Server Bot\n"
    "\n"
    "Commands:\n"
    "/on — start the VPS and launch Minecraft\n"
    "/off — stop Minecraft and shut down the VPS\n"
    "/status — show VPS and Minecraft status\n"
    "/help — show this message\n"
    "/adduser <telegram_id> — grant access to a new user\n"
    "\n"
    "How to connect:\n"
    "1. Start the server with /on and wait for it to boot\n"
    "2. Open Minecraft → Multiplayer → Add Server\n"
    f"3. Server Address: {SSH_HOST}\n"
    "4. Port: 25565 (default, can be omitted)\n"
    "5. Click Join Server"
)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Welcome message with full help text."""
    if not is_allowed(update):
        await update.message.reply_text("Access denied.")
        return
    await update.message.reply_text(f"Hey!\n\n{HELP_TEXT}")


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show available commands and connection instructions."""
    if not is_allowed(update):
        await update.message.reply_text("Access denied.")
        return
    await update.message.reply_text(HELP_TEXT)


async def cmd_add_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add a new user to the whitelist by Telegram ID."""
    if not is_allowed(update):
        await update.message.reply_text("Access denied.")
        return

    if not context.args or len(context.args) != 1 or not context.args[0].isdigit():
        await update.message.reply_text("Usage: /adduser <telegram_id>")
        return

    new_id = int(context.args[0])
    if add_user(new_id):
        await update.message.reply_text(f"User {new_id} added.")
    else:
        await update.message.reply_text(f"User {new_id} already has access.")


async def cmd_on(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ask for confirmation before starting the server."""
    if not is_allowed(update):
        await update.message.reply_text("Access denied.")
        return
    await update.message.reply_text(
        "Start the VPS and launch Minecraft?",
        reply_markup=CONFIRM_ON,
    )


async def cmd_off(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ask for confirmation before stopping the server."""
    if not is_allowed(update):
        await update.message.reply_text("Access denied.")
        return
    await update.message.reply_text(
        "Stop Minecraft and shut down the VPS?",
        reply_markup=CONFIRM_OFF,
    )


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show current VPS status and whether Minecraft is running."""
    if not is_allowed(update):
        await update.message.reply_text("Access denied.")
        return

    try:
        vps_status = await get_server_status()
    except Exception as e:
        await update.message.reply_text(f"Failed to get VPS status: {e}")
        return

    # Only check Minecraft if VPS is on (SSH won't work otherwise)
    mc_status = "unknown"
    if vps_status == "on":
        try:
            running = await is_minecraft_running()
            mc_status = "running" if running else "stopped"
        except Exception:
            mc_status = "unable to connect"

    await update.message.reply_text(
        f"VPS: {vps_status}\n"
        f"Minecraft: {mc_status}"
    )
