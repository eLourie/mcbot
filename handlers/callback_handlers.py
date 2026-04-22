"""Inline button callback handlers — executes the actual start/stop flows."""

import asyncio

from telegram import Update
from telegram.ext import ContextTypes

from utils.auth import is_allowed
from services.timeweb import start_server, stop_server, get_server_status
from services.ssh_client import start_minecraft, stop_minecraft, is_minecraft_running
from utils.waiter import wait_for_vps_online


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Route callback button presses to the appropriate action."""
    query = update.callback_query
    await query.answer()

    if not is_allowed(update):
        await query.edit_message_text("Access denied.")
        return

    action = query.data

    if action == "cancel":
        await query.edit_message_text("Cancelled.")
    elif action == "confirm_on":
        await _do_start(query)
    elif action == "confirm_off":
        await _do_stop(query)


async def _do_start(query) -> None:
    """Full startup flow: VPS → wait for boot → wait for SSH → launch Minecraft."""
    # Check current VPS state
    try:
        status = await get_server_status()
    except Exception as e:
        await query.edit_message_text(f"Failed to check VPS status: {e}")
        return

    if status == "on":
        # VPS already on — just make sure Minecraft is running
        try:
            if await is_minecraft_running():
                await query.edit_message_text("VPS is already on and Minecraft is running.")
                return
            await query.edit_message_text("VPS is on. Starting Minecraft...")
            await start_minecraft()
            await query.edit_message_text("Minecraft started.")
            return
        except Exception as e:
            await query.edit_message_text(f"VPS is on but failed to start Minecraft: {e}")
            return

    # Send start command to Timeweb API
    await query.edit_message_text("Starting VPS...")
    try:
        await start_server()
    except Exception as e:
        await query.edit_message_text(f"Failed to start VPS: {e}")
        return

    # Poll until VPS is online and SSH is reachable
    await query.edit_message_text("VPS is starting, waiting for it to come online...")
    online = await wait_for_vps_online()
    if not online:
        await query.edit_message_text("VPS did not come online in time. Check it manually.")
        return

    # Launch Minecraft in a screen session
    await query.edit_message_text("VPS is online. Starting Minecraft...")
    try:
        await start_minecraft()
    except Exception as e:
        await query.edit_message_text(f"VPS is online but failed to start Minecraft: {e}")
        return

    await query.edit_message_text("VPS is online and Minecraft is running!")


async def _do_stop(query) -> None:
    """Full shutdown flow: stop Minecraft → wait for save → shut down VPS."""
    try:
        status = await get_server_status()
    except Exception as e:
        await query.edit_message_text(f"Failed to check VPS status: {e}")
        return

    if status != "on":
        await query.edit_message_text(f"VPS is not running (status: {status}).")
        return

    # Gracefully stop Minecraft (sends "stop" to the screen session)
    try:
        if await is_minecraft_running():
            await query.edit_message_text("Stopping Minecraft...")
            await stop_minecraft()
            # Wait for Minecraft to save the world and shut down
            await asyncio.sleep(10)
    except Exception as e:
        await query.edit_message_text(f"Failed to stop Minecraft: {e}")
        return

    # Shut down the VPS
    await query.edit_message_text("Shutting down VPS...")
    try:
        await stop_server()
    except Exception as e:
        await query.edit_message_text(f"Failed to shut down VPS: {e}")
        return

    await query.edit_message_text("Minecraft stopped and VPS is shutting down.")
