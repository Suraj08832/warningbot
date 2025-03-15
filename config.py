# Bot configuration
BOT_TOKEN = "7617534486:AAFUkmCp_h429Vpv1ytU3Sn5YINdDYvOCfA"
OWNER_ID = 7845308909
OWNER_NAME = "𐏓  𝅥‌꯭𝆬ᷟj‌➥‌𝗭𝗲‌𝗳𝗿𝗼‌𝗻 ‌🔥❰⎯꯭ ꭗ‌‌"
OWNER_USERNAME = "@Crush_hu_tera"

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
🔹 /approve <user_id/username> - Approve a user (Admin/Sudo only)
🔹 /disapprove <user_id/username> - Disapprove a user (Admin/Sudo only)
🔹 /addsudo <user_id/username> - Add sudo user (Owner only)
🔹 /removesudo <user_id/username> - Remove sudo user (Owner only)
🔹 /status - Check your approval status
"""