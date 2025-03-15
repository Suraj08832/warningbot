import logging
import os
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
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
    level=logging.INFO
)

logger = logging.getLogger(__name__)

def main():
    # Create updater instance
    updater = Updater(token=BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Add command handlers
    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("approve", approve_command))
    dispatcher.add_handler(CommandHandler("disapprove", disapprove_command))
    dispatcher.add_handler(CommandHandler("addsudo", addsudo_command))
    dispatcher.add_handler(CommandHandler("removesudo", removesudo_command))
    dispatcher.add_handler(CommandHandler("status", status_command))

    # Add message handler for edited messages
    dispatcher.add_handler(MessageHandler(
        Filters.update.edited_message,
        handle_edited_message
    ))

    # Add message handler for all types of messages and updates
    dispatcher.add_handler(MessageHandler(
        Filters.all & ~Filters.command,
        handle_message
    ))

    # Start the bot
    logger.info("Starting bot...")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()