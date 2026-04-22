# MCBot — Telegram Minecraft Server Manager

Telegram bot for managing a Minecraft server on a Timeweb Cloud VPS.
Any whitelisted user can start/stop the server and add new players via their Telegram ID.

## Commands

| Command                      | Description                                 |
|------------------------------|---------------------------------------------|
| `/start`                     | Welcome message with instructions           |
| `/help`                      | Show all commands and how to connect         |
| `/on`                        | Start VPS, wait for boot, launch Minecraft   |
| `/off`                       | Stop Minecraft, shut down VPS                |
| `/status`                    | Show VPS status and Minecraft running state  |
| `/adduser <telegram_id>`     | Grant bot access to a new user               |

All commands require confirmation via inline buttons and are restricted to whitelisted user IDs.

## Setup

1. Clone the repository and create a virtual environment:
   ```bash
   git clone https://github.com/YOUR_USERNAME/mcbot.git
   cd mcbot
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and fill in your values:
   ```bash
   cp .env.example .env
   ```

3. Run the bot:
   ```bash
   python main.py
   ```

## Environment Variables

| Variable            | Required | Description                                          |
|---------------------|----------|------------------------------------------------------|
| `TELEGRAM_TOKEN`    | Yes      | Bot token from @BotFather                            |
| `TIMEWEB_API_TOKEN` | Yes      | Timeweb Cloud API token                              |
| `SERVER_ID`         | Yes      | Timeweb VPS server ID                                |
| `ALLOWED_USERS`     | Yes      | Comma-separated Telegram user IDs (initial whitelist)|
| `SSH_HOST`          | Yes      | VPS IP address or hostname                           |
| `SSH_USER`          | Yes      | SSH username (usually `root`)                        |
| `SSH_PASSWORD`      | Yes      | SSH password                                         |
| `MINECRAFT_DIR`     | No       | Minecraft server directory (default: `/opt/minecraft`) |
| `MINECRAFT_RAM_MAX` | No       | JVM max memory (default: `2G`)                       |
| `MINECRAFT_RAM_MIN` | No       | JVM min memory (default: `1G`)                       |
| `VPS_BOOT_TIMEOUT`  | No       | Seconds to wait for VPS boot (default: `120`)        |

## Architecture

```
main.py                          — Entry point, registers all handlers
config.py                        — Loads .env, validates required settings
handlers/command_handlers.py     — /start, /help, /on, /off, /status, /adduser
handlers/callback_handlers.py    — Inline button confirmations (start/stop flow)
services/timeweb.py              — Timeweb Cloud REST API (start/stop/status)
services/ssh_client.py           — SSH commands via paramiko (start/stop/check Minecraft)
utils/auth.py                    — User whitelist check per update
utils/keyboards.py               — Inline keyboard layouts for confirmations
utils/waiter.py                  — Async poll: waits for VPS boot + SSH readiness
utils/user_store.py              — Persistent user whitelist (allowed_users.json)
```

## How It Works

1. **`/on`** — sends a start request to Timeweb API, polls until VPS status is `on`, waits for SSH port 22 to accept connections, then launches Minecraft in a `screen` session via SSH.
2. **`/off`** — sends `stop` command to the Minecraft screen session, waits 10 seconds for world save, then shuts down the VPS via Timeweb API.
3. **User management** — initial whitelist is seeded from `ALLOWED_USERS` in `.env`. After that, any whitelisted user can add others via `/adduser`. The list is persisted in `allowed_users.json`.
