"""Entry point — registers all bot handlers and starts polling."""

from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler

from config import TELEGRAM_TOKEN
from handlers.command_handlers import cmd_on, cmd_off, cmd_status, cmd_start, cmd_help, cmd_add_user
from handlers.callback_handlers import handle_callback


def main() -> None:
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Bot commands
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("on", cmd_on))
    app.add_handler(CommandHandler("off", cmd_off))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("adduser", cmd_add_user))

    # Inline button callbacks (confirm/cancel for /on and /off)
    app.add_handler(CallbackQueryHandler(handle_callback))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
