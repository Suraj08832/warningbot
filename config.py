import os

# Bot configuration
BOT_TOKEN = os.environ.get("BOT_TOKEN", "7617534486:AAEsA9dbH45Ysqn0BXpLyu6qgV99lpiJ9_g")  # Default for development
OWNER_ID = int(os.environ.get("OWNER_ID", "7845308909"))  # Default for development
OWNER_NAME = os.environ.get("OWNER_NAME", "𐏓  мым‌꯭𝆬ᷟj‌➥‌𝗭𝗲‌𝗳𝗿𝗼‌𝗻 ‌🔥❰⎯꯭ ꭗ‌‌")  # Default for development
OWNER_USERNAME = os.environ.get("OWNER_USERNAME", "@Crush_hu_tera")  # Default for development

# Bot Commands configuration
BOT_COMMANDS = [
    ("start", "Start the bot"),
    ("help", "Show help message"),
    ("approve", "Approve a user (Admin/Sudo only)"),
    ("disapprove", "Disapprove a user (Admin/Sudo only)"),
    ("addsudo", "Add sudo user (Owner only)"),
    ("removesudo", "Remove sudo user (Owner only)"),
    ("status", "Check your approval status")
]

# Database configuration
APPROVED_USERS = set()
SUDO_USERS = set()
SUDO_USERS.add(OWNER_ID)  # Owner is always a sudo user

# Message configurations
WELCOME_MESSAGE = """
Hello! I am a moderation bot that helps protect against copyright infringement and manages media content.
Only approved users can send media content.

Bot Owner: {owner_name}
Contact: {owner_username}
"""

HELP_MESSAGE = """
Available Commands:
🔹 /start - Start the bot
🔹 /help - Show this help message
🔹 /approve - Approve a user (Admin/Sudo only)
   • Use: /approve <user_id/username>
   • Or reply to a message with /approve
🔹 /disapprove - Disapprove a user (Admin/Sudo only)
   • Use: /disapprove <user_id/username>
   • Or reply to a message with /disapprove
🔹 /addsudo - Add sudo user (Owner only)
   • Use: /addsudo <user_id/username>
   • Or reply to a message with /addsudo
🔹 /removesudo - Remove sudo user (Owner only)
   • Use: /removesudo <user_id/username>
   • Or reply to a message with /removesudo
🔹 /status - Check your approval status

Note: Sudo users can approve/disapprove users. Only the owner can manage sudo users.
Media messages from unapproved users will be deleted automatically.
Edited messages are not allowed and will be deleted.
"""