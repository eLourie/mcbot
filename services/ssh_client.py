"""SSH client — start, stop, and check Minecraft server via paramiko."""

import asyncio
from functools import partial

import paramiko

from config import SSH_HOST, SSH_USER, SSH_PASSWORD, MINECRAFT_DIR, MINECRAFT_RAM_MAX, MINECRAFT_RAM_MIN


def _connect() -> paramiko.SSHClient:
    """Open an SSH connection to the VPS."""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=10)
    return client


def _run(cmd: str) -> str:
    """Execute a command over SSH and return stdout."""
    client = _connect()
    try:
        _, stdout, stderr = client.exec_command(cmd)
        return stdout.read().decode().strip()
    finally:
        client.close()


async def _async_run(cmd: str) -> str:
    """Run a blocking SSH command in a thread pool to avoid blocking the event loop."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, partial(_run, cmd))


async def is_minecraft_running() -> bool:
    """Check if a screen session named 'minecraft' exists."""
    output = await _async_run("screen -ls | grep minecraft || true")
    return "minecraft" in output


async def start_minecraft() -> None:
    """Launch the Minecraft server inside a detached screen session."""
    start_cmd = (
        f"screen -dmS minecraft bash -c "
        f"'cd {MINECRAFT_DIR} && java -Xmx{MINECRAFT_RAM_MAX} -Xms{MINECRAFT_RAM_MIN} -jar server.jar nogui'"
    )
    await _async_run(start_cmd)


async def stop_minecraft() -> None:
    """Send the 'stop' command to the Minecraft screen session for a graceful shutdown."""
    await _async_run("screen -S minecraft -p 0 -X stuff 'stop\n'")
