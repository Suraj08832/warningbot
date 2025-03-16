import sqlite3
import logging
from typing import Set, Optional, List, Tuple
from config import ADMIN_ID
import threading

logger = logging.getLogger(__name__)

class Database:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(Database, cls).__new__(cls)
            return cls._instance

    def __init__(self):
        """Initialize database connection and create tables if they don't exist."""
        if not hasattr(self, 'initialized'):
            self.conn = None
            self.initialized = True
            self.create_tables()
            # Ensure admin is always a sudo user
            self.add_sudo_user(ADMIN_ID, "admin", ADMIN_ID)

    def get_connection(self):
        """Get a thread-safe database connection."""
        if not hasattr(self, '_local'):
            self._local = threading.local()
        if not hasattr(self._local, 'connection'):
            self._local.connection = sqlite3.connect('bot.db')
        return self._local.connection

    def create_tables(self):
        """Create necessary database tables if they don't exist."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create approved users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS approved_users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                approved_by INTEGER,
                approved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create sudo users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sudo_users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                added_by INTEGER,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()

    def add_approved_user(self, user_id: int, username: str, approved_by: int) -> bool:
        """Add a user to the approved users list."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT OR REPLACE INTO approved_users (user_id, username, approved_by) VALUES (?, ?, ?)',
                (user_id, username, approved_by)
            )
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding approved user: {e}")
            return False

    def remove_approved_user(self, user_id: int) -> bool:
        """Remove a user from the approved users list."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM approved_users WHERE user_id = ?', (user_id,))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error removing approved user: {e}")
            return False

    def is_user_approved(self, user_id: int) -> bool:
        """Check if a user is approved."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT 1 FROM approved_users WHERE user_id = ?', (user_id,))
            return cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"Error checking approved user: {e}")
            return False

    def add_sudo_user(self, user_id: int, username: str, added_by: int) -> bool:
        """Add a user to the sudo users list."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT OR REPLACE INTO sudo_users (user_id, username, added_by) VALUES (?, ?, ?)',
                (user_id, username, added_by)
            )
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding sudo user: {e}")
            return False

    def remove_sudo_user(self, user_id: int) -> bool:
        """Remove a user from the sudo users list."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM sudo_users WHERE user_id = ?', (user_id,))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error removing sudo user: {e}")
            return False

    def is_sudo_user(self, user_id: int) -> bool:
        """Check if a user is a sudo user."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT 1 FROM sudo_users WHERE user_id = ?', (user_id,))
            return cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"Error checking sudo user: {e}")
            return False

    def get_approved_users(self) -> List[Tuple[int, str]]:
        """Get list of all approved users."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT user_id, username FROM approved_users')
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error getting approved users: {e}")
            return []

    def get_sudo_users(self) -> List[Tuple[int, str]]:
        """Get list of all sudo users."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT user_id, username FROM sudo_users')
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error getting sudo users: {e}")
            return []