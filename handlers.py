import asyncio
import logging
from telegram import Update, BotCommand
from telegram.ext import ContextTypes
from config import (
    OWNER_ID, OWNER_NAME, OWNER_USERNAME,
    WELCOME_MESSAGE, HELP_MESSAGE, BOT_COMMANDS
)
from database import Database
from utils import (
    extract_user_info, is_media_message, is_edited_message, 
    check_copyright_violation, delete_message_after_delay
)
from typing import Optional

logger = logging.getLogger(__name__)

db = Database()

def get_user_from_message(update: Update, context) -> tuple[Optional[int], Optional[str]]:
    """Extract user info from command arguments or replied message"""
    if context.args:
        logger.debug(f"Extracting user info from arguments: {context.args[0]}")
        return extract_user_info(context.args[0])
    elif update.message.reply_to_message:
        reply_msg = update.message.reply_to_message
        user = reply_msg.from_user
        logger.debug(f"Extracting user info from replied message. User ID: {user.id}, Username: {user.username}")
        return user.id, user.username
    logger.debug("No user info found in command arguments or reply")
    return None, None

async def send_temp_message(chat_id: int, text: str, context: ContextTypes.DEFAULT_TYPE):
    """Send a temporary message that will be deleted after 30 seconds"""
    message = await context.bot.send_message(chat_id=chat_id, text=text)
    asyncio.create_task(delete_message_after_delay(message))
    return message

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command"""
    try:
        # Set bot commands for the user
        await context.bot.set_my_commands([
            BotCommand(command, description) for command, description in BOT_COMMANDS
        ])
        # Send welcome message with owner info
        message = await send_temp_message(update.effective_chat.id, WELCOME_MESSAGE.format(
                owner_name=OWNER_NAME,
                owner_username=OWNER_USERNAME
            ), context)
    except Exception as e:
        logger.error(f"Error in /start command: {e}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /help command"""
    try:
        message = await send_temp_message(update.effective_chat.id, HELP_MESSAGE, context)
    except Exception as e:
        logger.error(f"Error in /help command: {e}")

async def approve_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /approve command"""
    try:
        if not update.message or not db.is_sudo_user(update.effective_user.id):
            message = await send_temp_message(update.effective_chat.id, "❌ You don't have permission to approve users.", context)
            return

        user_id, username = get_user_from_message(update, context)

        if not user_id and not username:
            message = await send_temp_message(update.effective_chat.id, "❌ Please provide a user ID/username or reply to a user's message to approve them.", context)
            return

        logger.debug(f"Attempting to approve user. ID: {user_id}, Username: {username}")
        if user_id:
            if db.add_approved_user(user_id, username or str(user_id), update.effective_user.id):
                message = await send_temp_message(update.effective_chat.id, f"✅ User {user_id} has been approved.", context)
                logger.info(f"User {user_id} approved by {update.effective_user.id}")
            else:
                message = await send_temp_message(update.effective_chat.id, "❌ Failed to approve user.", context)
        elif username:
            if db.add_approved_user(0, username, update.effective_user.id):  # Using 0 as temporary ID
                message = await send_temp_message(update.effective_chat.id, f"✅ User {username} has been approved.", context)
                logger.info(f"User {username} approved by {update.effective_user.id}")
            else:
                message = await send_temp_message(update.effective_chat.id, "❌ Failed to approve user.", context)
    except Exception as e:
        logger.error(f"Error in /approve command: {e}")

async def disapprove_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /disapprove command"""
    try:
        if not update.message or not db.is_sudo_user(update.effective_user.id):
            message = await send_temp_message(update.effective_chat.id, "❌ You don't have permission to disapprove users.", context)
            return

        user_id, username = get_user_from_message(update, context)

        if not user_id and not username:
            message = await send_temp_message(update.effective_chat.id, "❌ Please provide a user ID/username or reply to a user's message to disapprove them.", context)
            return

        logger.debug(f"Attempting to disapprove user. ID: {user_id}")
        if user_id:
            if db.remove_approved_user(user_id):
                message = await send_temp_message(update.effective_chat.id, f"✅ User {user_id} has been disapproved.", context)
                logger.info(f"User {user_id} disapproved by {update.effective_user.id}")
            else:
                message = await send_temp_message(update.effective_chat.id, "❌ Failed to disapprove user.", context)
    except Exception as e:
        logger.error(f"Error in /disapprove command: {e}")

async def addsudo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /addsudo command"""
    try:
        if not update.message or update.effective_user.id != OWNER_ID:
            message = await send_temp_message(update.effective_chat.id, "❌ Only the owner can add sudo users.", context)
            return

        user_id, username = get_user_from_message(update, context)

        if not user_id and not username:
            message = await send_temp_message(update.effective_chat.id, "❌ Please provide a user ID/username or reply to a user's message to add them as sudo.", context)
            return

        logger.debug(f"Attempting to add sudo user. ID: {user_id}, Username: {username}")
        if user_id:
            if db.add_sudo_user(user_id, username or str(user_id), update.effective_user.id):
                message = await send_temp_message(update.effective_chat.id, f"✅ User {user_id} has been added as sudo.", context)
                logger.info(f"User {user_id} added as sudo by owner")
            else:
                message = await send_temp_message(update.effective_chat.id, "❌ Failed to add sudo user.", context)
        elif username:
            if db.add_sudo_user(0, username, update.effective_user.id):  # Using 0 as temporary ID
                message = await send_temp_message(update.effective_chat.id, f"✅ User {username} has been added as sudo.", context)
                logger.info(f"User {username} added as sudo by owner")
            else:
                message = await send_temp_message(update.effective_chat.id, "❌ Failed to add sudo user.", context)
    except Exception as e:
        logger.error(f"Error in /addsudo command: {e}")

async def removesudo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /removesudo command"""
    try:
        if not update.message or update.effective_user.id != OWNER_ID:
            message = await send_temp_message(update.effective_chat.id, "❌ Only the owner can remove sudo users.", context)
            return

        user_id, username = get_user_from_message(update, context)

        if not user_id and not username:
            message = await send_temp_message(update.effective_chat.id, "❌ Please provide a user ID/username or reply to a user's message to remove them from sudo.", context)
            return

        logger.debug(f"Attempting to remove sudo user. ID: {user_id}")
        if user_id:
            if db.remove_sudo_user(user_id):
                message = await send_temp_message(update.effective_chat.id, f"✅ User {user_id} has been removed from sudo.", context)
                logger.info(f"User {user_id} removed from sudo by owner")
            else:
                message = await send_temp_message(update.effective_chat.id, "❌ Failed to remove sudo user.", context)
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

        logger.debug(f"Status check for user {user_id}: Owner={user_id == OWNER_ID}, Sudo={is_sudo}, Approved={is_approved}")
        message = await send_temp_message(update.effective_chat.id, "\n".join(status), context)
    except Exception as e:
        logger.error(f"Error in /status command: {e}")

async def handle_edited_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle edited messages"""
    try:
        if not update.edited_message:
            return

        logger.debug(f"Handling edited message: {update.edited_message.message_id}")

        try:
            # Delete the edited message
            await update.edited_message.delete()
            # Send warning about edited messages with auto-delete
            message = await send_temp_message(update.effective_chat.id, "❌ Edited messages are not allowed.", context)
            logger.info(f"Deleted edited message {update.edited_message.message_id} from user {update.effective_user.id}")
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
                    message = await send_temp_message(update.effective_chat.id, "❌ You need to be approved to send media content.", context)
                    logger.info(f"Deleted unauthorized media message from user {user_id}")
                except Exception as e:
                    logger.error(f"Error handling media message: {e}")
                return

        # Check for copyright violation
        if update.message.text and check_copyright_violation(update.message.text):
            try:
                await update.message.delete()
                message = await send_temp_message(update.effective_chat.id, "❌ Message deleted due to potential copyright violation.", context)
                logger.info(f"Deleted message with copyright violation from user {user_id}")
            except Exception as e:
                logger.error(f"Error handling copyright violation: {e}")
            return

    except Exception as e:
        logger.error(f"Error in message handler: {e}")