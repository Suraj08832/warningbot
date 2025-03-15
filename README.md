# Telegram Moderation Bot

A powerful Telegram bot for content moderation with copyright protection and media content restrictions.

## Features

- Media content moderation
- Copyright violation detection
- User approval system
- Sudo user management
- Auto-deletion of warnings and system messages
- Edited message detection and removal

## Deployment on Render

1. Fork or clone this repository
2. Create a new Web Service on Render
3. Connect your repository
4. Set the following environment variables:

### Required Environment Variables

- `BOT_TOKEN`: Your Telegram Bot Token from @BotFather
- `OWNER_ID`: Your Telegram User ID (numeric)
- `OWNER_NAME`: Your name or bot owner's name
- `OWNER_USERNAME`: Your Telegram username (with @ symbol)

### Deployment Steps

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" and select "Web Service"
3. Connect your GitHub repository
4. Fill in the following details:
   - Name: Your bot name
   - Environment: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python bot.py`
5. Select the Free plan
6. Click "Create Web Service"

The bot will automatically start running once deployed.

## Bot Commands

- `/start` - Start the bot
- `/help` - Show help message
- `/approve` - Approve a user (Admin/Sudo only)
- `/disapprove` - Disapprove a user (Admin/Sudo only)
- `/addsudo` - Add sudo user (Owner only)
- `/removesudo` - Remove sudo user (Owner only)
- `/status` - Check your approval status

## Features

- Auto-deletion of bot messages after 30 seconds
- Media message control for unapproved users
- Copyright violation detection
- Edited message detection and removal
- Multiple admin levels (Owner and Sudo users)

## Database

The bot uses SQLite3 for data storage, which is automatically initialized on first run. No additional database setup is required.