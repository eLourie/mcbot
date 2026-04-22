"""Timeweb Cloud REST API client — start, stop, and check VPS status."""

import aiohttp

from config import TIMEWEB_API_BASE, TIMEWEB_API_TOKEN, SERVER_ID


def _headers() -> dict[str, str]:
    """Auth and content-type headers for all Timeweb API requests."""
    return {
        "Authorization": f"Bearer {TIMEWEB_API_TOKEN}",
        "Content-Type": "application/json",
    }


async def get_server_status() -> str:
    """Return the current VPS status string (e.g. 'on', 'off', 'starting')."""
    url = f"{TIMEWEB_API_BASE}/servers/{SERVER_ID}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=_headers()) as resp:
            resp.raise_for_status()
            data = await resp.json()
            return data["server"]["status"]


async def start_server() -> None:
    """Send start action to the VPS."""
    url = f"{TIMEWEB_API_BASE}/servers/{SERVER_ID}/action"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=_headers(), json={"action": "start"}) as resp:
            resp.raise_for_status()


async def stop_server() -> None:
    """Send shutdown action to the VPS."""
    url = f"{TIMEWEB_API_BASE}/servers/{SERVER_ID}/action"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=_headers(), json={"action": "shutdown"}) as resp:
            resp.raise_for_status()
