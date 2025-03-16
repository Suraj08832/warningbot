import os

# Bot token from environment variable
BOT_TOKEN = os.environ.get('BOT_TOKEN')

# Admin ID from environment variable (as integer)
ADMIN_ID = int(os.environ.get('ADMIN_ID', 0))

# Bot information
BOT_USERNAME = "Xsecurity_shielders_bot"
BOT_NAME = "🛡️ SECURITY SHIELD"
BOT_DESCRIPTION = """
🛡️ ULTIMATE SECURITY SHIELD ACTIVATED 🛡️
Protecting your conversations with military-grade encryption & AI-powered threat detection! Our advanced Security Bot safeguards against unauthorized media, edited messages, malicious links & spam content. 24/7 protection for a safe & secure chat experience! 💬

Features:
✅ Military-grade security protection
🛡️ AI-powered threat detection
🔒 Automatic message encryption
⚠️ Real-time spam prevention
⚡ 24/7 Active monitoring
🤖 Advanced security algorithms
"""

# Message templates
START_MESSAGE = """
👋 Hello! I'm {bot_name}.

I'm your ultimate security shield, protecting your group with advanced security features.
Use /help to see available commands.
"""

# Warning message (auto-deletes after 30 seconds)
WARNING_MESSAGE = """
⚠️ Security Alert: Unauthorized Message Edit Detected!
User: {user_name}
Action: Message edited and deleted
Status: Security protocol activated
"""

# Database configuration
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///bot.db')

# Bot configuration
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
SUDO_USERS.add(ADMIN_ID)  # Admin is always a sudo user

# Message configurations
WELCOME_MESSAGE = """
🛡️ Welcome to the Ultimate Security Shield! 🛡️
I am your advanced security bot, protecting your group with military-grade security features.
Only approved users can send media content.

Bot Name: {bot_name}
Username: {bot_username}
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