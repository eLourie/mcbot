"""Async poll loop — waits for VPS to boot and SSH to become reachable."""

import asyncio
import socket

from config import VPS_BOOT_TIMEOUT, SSH_HOST
from services.timeweb import get_server_status


async def wait_for_vps_online() -> bool:
    """Poll Timeweb API until status is 'on', then wait for SSH port 22 to accept connections."""
    elapsed = 0
    interval = 5

    # Phase 1: wait for Timeweb API to report status "on"
    while elapsed < VPS_BOOT_TIMEOUT:
        status = await get_server_status()
        if status == "on":
            break
        await asyncio.sleep(interval)
        elapsed += interval
    else:
        return False

    # Phase 2: wait for SSH to become reachable (VPS is "on" but sshd may not be ready yet)
    while elapsed < VPS_BOOT_TIMEOUT:
        if await _is_ssh_ready():
            return True
        await asyncio.sleep(interval)
        elapsed += interval

    return False


async def _is_ssh_ready() -> bool:
    """Try to connect to SSH port in a thread pool."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _check_ssh_port)


def _check_ssh_port() -> bool:
    """Attempt a raw TCP connection to port 22."""
    try:
        with socket.create_connection((SSH_HOST, 22), timeout=5):
            return True
    except (OSError, TimeoutError):
        return False
