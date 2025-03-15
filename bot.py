import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from config import BOT_TOKEN
from handlers import (
    start_command,
    help_command,
    approve_command,
    disapprove_command,
    addsudo_command,
    removesudo_command,
    status_command,
    handle_message,
    handle_edited_message
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG  # Set to DEBUG for more detailed logs
)

logger = logging.getLogger(__name__)

def main():
    """Start the bot"""
    # Create the Application
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("approve", approve_command))
    application.add_handler(CommandHandler("disapprove", disapprove_command))
    application.add_handler(CommandHandler("addsudo", addsudo_command))
    application.add_handler(CommandHandler("removesudo", removesudo_command))
    application.add_handler(CommandHandler("status", status_command))

    # Add message handler for edited messages (must be before the regular message handler)
    application.add_handler(MessageHandler(
        filters.UpdateType.EDITED_MESSAGE,  # Handle edited messages
        handle_edited_message
    ))

    # Add message handler for all types of messages and updates
    application.add_handler(MessageHandler(
        filters.ALL & ~filters.COMMAND,  # Handle all non-command messages
        handle_message
    ))

    # Start the bot
    logger.info("Starting bot...")
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True  # Ignore messages received while bot was offline
    )

if __name__ == '__main__':
    main()