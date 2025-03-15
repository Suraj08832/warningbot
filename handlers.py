import logging
from telegram import Update, BotCommand
from telegram.ext import ContextTypes
from config import (
    OWNER_ID, OWNER_NAME, OWNER_USERNAME,
    WELCOME_MESSAGE, HELP_MESSAGE, BOT_COMMANDS
)
from database import Database
from utils import extract_user_info, is_media_message, check_copyright_violation
from typing import Optional

logger = logging.getLogger(__name__)

db = Database()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command"""
    try:
        # Set bot commands for the user
        await context.bot.set_my_commands([
            BotCommand(command, description) for command, description in BOT_COMMANDS
        ])
        # Send welcome message with owner info
        await update.message.reply_text(
            WELCOME_MESSAGE.format(
                owner_name=OWNER_NAME,
                owner_username=OWNER_USERNAME
            )
        )
    except Exception as e:
        logger.error(f"Error in /start command: {e}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /help command"""
    try:
        await update.message.reply_text(HELP_MESSAGE)
    except Exception as e:
        logger.error(f"Error in /help command: {e}")

async def approve_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /approve command"""
    try:
        if not update.message or not db.is_sudo_user(update.effective_user.id):
            await update.message.reply_text("❌ You don't have permission to approve users.")
            return

        if not context.args:
            await update.message.reply_text("❌ Please provide a user ID or username to approve.")
            return

        user_id, username = extract_user_info(context.args[0])
        if user_id:
            if db.add_approved_user(user_id, username or str(user_id), update.effective_user.id):
                await update.message.reply_text(f"✅ User {user_id} has been approved.")
            else:
                await update.message.reply_text("❌ Failed to approve user.")
        elif username:
            if db.add_approved_user(0, username, update.effective_user.id):  # Using 0 as temporary ID
                await update.message.reply_text(f"✅ User {username} has been approved.")
            else:
                await update.message.reply_text("❌ Failed to approve user.")
    except Exception as e:
        logger.error(f"Error in /approve command: {e}")

async def disapprove_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /disapprove command"""
    try:
        if not update.message or not db.is_sudo_user(update.effective_user.id):
            await update.message.reply_text("❌ You don't have permission to disapprove users.")
            return

        if not context.args:
            await update.message.reply_text("❌ Please provide a user ID or username to disapprove.")
            return

        user_id, _ = extract_user_info(context.args[0])
        if user_id:
            if db.remove_approved_user(user_id):
                await update.message.reply_text(f"✅ User {user_id} has been disapproved.")
            else:
                await update.message.reply_text("❌ Failed to disapprove user.")
    except Exception as e:
        logger.error(f"Error in /disapprove command: {e}")

async def addsudo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /addsudo command"""
    try:
        if not update.message or update.effective_user.id != OWNER_ID:
            await update.message.reply_text("❌ Only the owner can add sudo users.")
            return

        if not context.args:
            await update.message.reply_text("❌ Please provide a user ID or username to add as sudo.")
            return

        user_id, username = extract_user_info(context.args[0])
        if user_id:
            if db.add_sudo_user(user_id, username or str(user_id), update.effective_user.id):
                await update.message.reply_text(f"✅ User {user_id} has been added as sudo.")
            else:
                await update.message.reply_text("❌ Failed to add sudo user.")
        elif username:
            if db.add_sudo_user(0, username, update.effective_user.id):  # Using 0 as temporary ID
                await update.message.reply_text(f"✅ User {username} has been added as sudo.")
            else:
                await update.message.reply_text("❌ Failed to add sudo user.")
    except Exception as e:
        logger.error(f"Error in /addsudo command: {e}")

async def removesudo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /removesudo command"""
    try:
        if not update.message or update.effective_user.id != OWNER_ID:
            await update.message.reply_text("❌ Only the owner can remove sudo users.")
            return

        if not context.args:
            await update.message.reply_text("❌ Please provide a user ID to remove from sudo.")
            return

        user_id, _ = extract_user_info(context.args[0])
        if user_id:
            if db.remove_sudo_user(user_id):
                await update.message.reply_text(f"✅ User {user_id} has been removed from sudo.")
            else:
                await update.message.reply_text("❌ Failed to remove sudo user.")
    except Exception as e:
        logger.error(f"Error in /removesudo command: {e}")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /status command"""
    try:
        if not update.message:
            return

        user_id = update.effective_user.id
        is_approved = db.is_user_approved(user_id)
        is_sudo = db.is_sudo_user(user_id)

        status = []
        if user_id == OWNER_ID:
            status.append("👑 You are the bot owner")
        if is_sudo:
            status.append("⭐ You are a sudo user")
        if is_approved:
            status.append("✅ You are an approved user")
        if not any([user_id == OWNER_ID, is_sudo, is_approved]):
            status.append("❌ You are not approved")

        await update.message.reply_text("\n".join(status))
    except Exception as e:
        logger.error(f"Error in /status command: {e}")

async def handle_edited_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle edited messages"""
    try:
        if not update.edited_message:
            return

        # Log the edited message event
        logger.debug(f"Handling edited message: {update.edited_message.message_id}")

        try:
            # Delete the edited message
            await update.edited_message.delete()
            # Send warning about edited messages
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Edited messages are not allowed."
            )
        except Exception as e:
            logger.error(f"Error deleting edited message: {e}")

    except Exception as e:
        logger.error(f"Error in edited message handler: {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle new messages"""
    try:
        if not update.message:
            return

        user_id = update.effective_user.id
        logger.debug(f"Handling message from user {user_id}")

        # Check for media content
        if is_media_message(update.message):
            if not db.is_user_approved(user_id):
                try:
                    await update.message.delete()
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text="❌ You need to be approved to send media content."
                    )
                except Exception as e:
                    logger.error(f"Error handling media message: {e}")
                return

        # Check for copyright violation
        if update.message.text and check_copyright_violation(update.message.text):
            try:
                await update.message.delete()
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="❌ Message deleted due to potential copyright violation."
                )
            except Exception as e:
                logger.error(f"Error handling copyright violation: {e}")
            return

    except Exception as e:
        logger.error(f"Error in message handler: {e}")