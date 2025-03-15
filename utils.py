from typing import Union, Tuple
import re

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
    return message.edit_date is not None

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
