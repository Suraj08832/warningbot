import re
import asyncio
from typing import Union, Tuple
from telegram import Message

def extract_user_info(text: str) -> Tuple[Union[int, None], Union[str, None]]:
    """Extract user ID and username from command text"""
    user_id = None
    username = None

    # Try to extract user ID
    if text.isdigit():
        user_id = int(text)
    # Try to extract username
    elif text.startswith('@'):
        username = text

    return user_id, username

def is_media_message(message) -> bool:
    """Check if message contains media content"""
    return any([
        message.sticker,
        message.animation,
        message.video,
        message.photo,
        message.document
    ])

def is_edited_message(message) -> bool:
    """Check if message is edited"""
    try:
        # Check both edit_date and edit history for robustness
        return bool(message.edit_date) or bool(getattr(message, 'edited', False))
    except Exception:
        return False

def check_copyright_violation(text: str) -> bool:
    """Basic copyright violation check"""
    copyright_patterns = [
        r'©\s*\d{4}',  # Copyright symbol with year
        r'all\s*rights?\s*reserved',
        r'copyright\s*\d{4}',
        r'proprietary\s*content',
    ]

    text = text.lower()
    for pattern in copyright_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

async def delete_message_after_delay(message: Message, delay: int = 30):
    """Delete a message after specified delay in seconds"""
    try:
        await asyncio.sleep(delay)
        await message.delete()
    except Exception:
        pass  # Silently handle deletion errors