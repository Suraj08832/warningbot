import logging
import time
from telegram import Update, ParseMode, BotCommand
from telegram.ext import CallbackContext
from telegram.error import BadRequest
from config import (
    BOT_NAME,
    START_MESSAGE,
    HELP_MESSAGE,
    WARNING_MESSAGE,
    ADMIN_ID,
    APPROVED_USERS,
    SUDO_USERS,
    BOT_COMMANDS
)
from database import Database
from utils import (
    extract_user_info, is_media_message, is_edited_message, 
    check_copyright_violation
)
from typing import Optional

logger = logging.getLogger(__name__)

db = Database()

def get_user_from_message(update: Update, context: CallbackContext) -> tuple[Optional[int], Optional[str]]:
    """Extract user info from command arguments or replied message"""
    try:
        if context.args:
            logger.debug(f"Extracting user info from arguments: {context.args[0]}")
            return extract_user_info(context.args[0])
        elif update.message.reply_to_message:
            reply_msg = update.message.reply_to_message
            user = reply_msg.from_user
            if user:
                logger.debug(f"Extracting user info from replied message. User ID: {user.id}, Username: {user.username}")
                return user.id, user.username or str(user.id)
        logger.debug("No user info found in command arguments or reply")
        return None, None
    except Exception as e:
        logger.error(f"Error in get_user_from_message: {e}")
        return None, None

def send_temp_message(update: Update, context: CallbackContext, text: str):
    """Send a temporary message that will be deleted after 30 seconds"""
    message = context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    context.job_queue.run_once(lambda _: message.delete(), 30)
    return message

def start_command(update: Update, context: CallbackContext):
    """Handle the /start command"""
    try:
        # Set bot commands for the user
        commands = [
            BotCommand(command, description) for command, description in BOT_COMMANDS
        ]
        context.bot.set_my_commands(commands)
        
        # Send welcome message with owner info (permanent message)
        welcome_text = START_MESSAGE.format(bot_name=BOT_NAME)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=welcome_text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True
        )
        
        # Log successful start command
        logger.info(f"Start command executed by user {update.effective_user.id}")
        
    except Exception as e:
        logger.error(f"Error in /start command: {e}")
        # Send error message to user
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ An error occurred while processing your request. Please try again later."
        )

def help_command(update: Update, context: CallbackContext):
    """Handle the /help command"""
    try:
        # Send help message (permanent message)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=HELP_MESSAGE
        )
    except Exception as e:
        logger.error(f"Error in /help command: {e}")

def approve_command(update: Update, context: CallbackContext):
    """Handle the /approve command"""
    try:
        if not update.message:
            return

        user_id = update.effective_user.id
        # Allow both admin and sudo users to approve
        if user_id != ADMIN_ID and not db.is_sudo_user(user_id):
            send_temp_message(update, context, "❌ You don't have permission to approve users.")
            return

        target_user_id, username = get_user_from_message(update, context)

        if not target_user_id and not username:
            send_temp_message(update, context, "❌ Please provide a user ID/username or reply to a user's message to approve them.")
            return

        logger.debug(f"Attempting to approve user. ID: {target_user_id}, Username: {username}")
        if target_user_id:
            if db.add_approved_user(target_user_id, username or str(target_user_id), user_id):
                send_temp_message(update, context, f"✅ User {target_user_id} has been approved.")
                logger.info(f"User {target_user_id} approved by {user_id}")
            else:
                send_temp_message(update, context, "❌ Failed to approve user.")
        elif username:
            if db.add_approved_user(0, username, user_id):  # Using 0 as temporary ID
                send_temp_message(update, context, f"✅ User {username} has been approved.")
                logger.info(f"User {username} approved by {user_id}")
            else:
                send_temp_message(update, context, "❌ Failed to approve user.")
    except Exception as e:
        logger.error(f"Error in /approve command: {e}")

def disapprove_command(update: Update, context: CallbackContext):
    """Handle the /disapprove command"""
    try:
        if not update.message or not db.is_sudo_user(update.effective_user.id):
            send_temp_message(update, context, "❌ You don't have permission to disapprove users.")
            return

        user_id, username = get_user_from_message(update, context)

        if not user_id and not username:
            send_temp_message(update, context, "❌ Please provide a user ID/username or reply to a user's message to disapprove them.")
            return

        logger.debug(f"Attempting to disapprove user. ID: {user_id}")
        if user_id:
            if db.remove_approved_user(user_id):
                send_temp_message(update, context, f"✅ User {user_id} has been disapproved.")
                logger.info(f"User {user_id} disapproved by {update.effective_user.id}")
            else:
                send_temp_message(update, context, "❌ Failed to disapprove user.")
    except Exception as e:
        logger.error(f"Error in /disapprove command: {e}")

def addsudo_command(update: Update, context: CallbackContext):
    """Handle the /addsudo command"""
    try:
        if not update.message:
            return

        user_id = update.effective_user.id
        # Allow both admin and sudo users to add sudo users
        if user_id != ADMIN_ID and not db.is_sudo_user(user_id):
            send_temp_message(update, context, "❌ You don't have permission to add sudo users.")
            return

        target_user_id, username = get_user_from_message(update, context)

        if not target_user_id and not username:
            send_temp_message(update, context, "❌ Please provide a user ID/username or reply to a user's message to add them as sudo.")
            return

        logger.debug(f"Attempting to add sudo user. ID: {target_user_id}, Username: {username}")
        if target_user_id:
            if db.add_sudo_user(target_user_id, username or str(target_user_id), user_id):
                send_temp_message(update, context, f"✅ User {target_user_id} has been added as sudo.")
                logger.info(f"User {target_user_id} added as sudo by {user_id}")
            else:
                send_temp_message(update, context, "❌ Failed to add sudo user.")
        elif username:
            if db.add_sudo_user(0, username, user_id):  # Using 0 as temporary ID
                send_temp_message(update, context, f"✅ User {username} has been added as sudo.")
                logger.info(f"User {username} added as sudo by {user_id}")
            else:
                send_temp_message(update, context, "❌ Failed to add sudo user.")
    except Exception as e:
        logger.error(f"Error in /addsudo command: {e}")

def removesudo_command(update: Update, context: CallbackContext):
    """Handle the /removesudo command"""
    try:
        if not update.message or update.effective_user.id != ADMIN_ID:
            send_temp_message(update, context, "❌ Only the bot admin can remove sudo users.")
            return

        user_id, username = get_user_from_message(update, context)

        if not user_id and not username:
            send_temp_message(update, context, "❌ Please provide a user ID/username or reply to a user's message to remove them from sudo.")
            return

        logger.debug(f"Attempting to remove sudo user. ID: {user_id}")
        if user_id:
            if db.remove_sudo_user(user_id):
                send_temp_message(update, context, f"✅ User {user_id} has been removed from sudo.")
                logger.info(f"User {user_id} removed from sudo by admin")
            else:
                send_temp_message(update, context, "❌ Failed to remove sudo user.")
    except Exception as e:
        logger.error(f"Error in /removesudo command: {e}")

def status_command(update: Update, context: CallbackContext):
    """Handle the /status command"""
    try:
        if not update.message:
            return

        user_id = update.effective_user.id
        is_approved = db.is_user_approved(user_id)
        is_sudo = db.is_sudo_user(user_id)

        status = []
        if user_id == ADMIN_ID:
            status.append("👑 You are the bot admin")
        if is_sudo:
            status.append("⭐ You are a sudo user")
        if is_approved:
            status.append("✅ You are an approved user")
        if not any([user_id == ADMIN_ID, is_sudo, is_approved]):
            status.append("❌ You are not approved")

        logger.debug(f"Status check for user {user_id}: Admin={user_id == ADMIN_ID}, Sudo={is_sudo}, Approved={is_approved}")
        send_temp_message(update, context, "\n".join(status))
    except Exception as e:
        logger.error(f"Error in /status command: {e}")

def handle_edited_message(update: Update, context: CallbackContext):
    """Handle edited messages"""
    try:
        if not update.edited_message:
            return

        logger.debug(f"Handling edited message: {update.edited_message.message_id}")

        try:
            # Delete the edited message
            update.edited_message.delete()
            # Send warning about edited messages with auto-delete
            warning = WARNING_MESSAGE.format(
                user_name=update.edited_message.from_user.first_name
            )
            warning_msg = context.bot.send_message(
                chat_id=update.edited_message.chat_id,
                text=warning,
                parse_mode=ParseMode.HTML
            )
            
            # Delete warning message after 30 seconds
            context.job_queue.run_once(
                lambda _: warning_msg.delete(),
                30,
                context=warning_msg.chat_id
            )
        except Exception as e:
            logger.error(f"Error handling edited message: {e}")

    except Exception as e:
        logger.error(f"Error in edited message handler: {e}")

def handle_message(update: Update, context: CallbackContext):
    """Handle new messages"""
    try:
        if not update.message:
            return

        user_id = update.effective_user.id
        logger.debug(f"Handling message from user {user_id}")

        # Check for media content
        if is_media_message(update.message):
            is_approved = db.is_user_approved(user_id)
            is_sudo = db.is_sudo_user(user_id)
            logger.debug(f"Media message from user {user_id}: Approved={is_approved}, Sudo={is_sudo}")

            if not (is_approved or is_sudo):
                try:
                    update.message.delete()
                    send_temp_message(update, context, "❌ You need to be approved to send media content.")
                    logger.info(f"Deleted unauthorized media message from user {user_id}")
                except Exception as e:
                    logger.error(f"Error handling media message: {e}")
                return

        # Check for copyright violation
        if update.message.text and check_copyright_violation(update.message.text):
            try:
                update.message.delete()
                send_temp_message(update, context, "❌ Message deleted due to potential copyright violation.")
                logger.info(f"Deleted message with copyright violation from user {user_id}")
            except Exception as e:
                logger.error(f"Error handling copyright violation: {e}")
            return

    except Exception as e:
        logger.error(f"Error in message handler: {e}")

def ping_command(update: Update, context: CallbackContext):
    """Handle the /ping command"""
    try:
        start_time = time.time()
        message = context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="🏓 Pinging..."
        )
        end_time = time.time()
        response_time = round((end_time - start_time) * 1000, 2)  # Convert to milliseconds
        message.edit_text(f"🏓 Pong!\nResponse Time: {response_time}ms")
    except Exception as e:
        logger.error(f"Error in /ping command: {e}")
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Error while checking bot status."
        )