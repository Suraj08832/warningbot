import sqlite3
from typing import Set, Optional
from config import OWNER_ID

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('bot.db', check_same_thread=False)
        self.create_tables()
        
    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS approved_users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            approved_by INTEGER,
            approved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sudo_users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            added_by INTEGER,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        self.conn.commit()
        
    def add_approved_user(self, user_id: int, username: str, approved_by: int) -> bool:
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                'INSERT OR REPLACE INTO approved_users (user_id, username, approved_by) VALUES (?, ?, ?)',
                (user_id, username, approved_by)
            )
            self.conn.commit()
            return True
        except Exception:
            return False
            
    def remove_approved_user(self, user_id: int) -> bool:
        try:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM approved_users WHERE user_id = ?', (user_id,))
            self.conn.commit()
            return True
        except Exception:
            return False
            
    def is_user_approved(self, user_id: int) -> bool:
        if user_id == OWNER_ID:
            return True
        cursor = self.conn.cursor()
        cursor.execute('SELECT 1 FROM approved_users WHERE user_id = ?', (user_id,))
        return cursor.fetchone() is not None
        
    def add_sudo_user(self, user_id: int, username: str, added_by: int) -> bool:
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                'INSERT OR REPLACE INTO sudo_users (user_id, username, added_by) VALUES (?, ?, ?)',
                (user_id, username, added_by)
            )
            self.conn.commit()
            return True
        except Exception:
            return False
            
    def remove_sudo_user(self, user_id: int) -> bool:
        if user_id == OWNER_ID:
            return False
        try:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM sudo_users WHERE user_id = ?', (user_id,))
            self.conn.commit()
            return True
        except Exception:
            return False
            
    def is_sudo_user(self, user_id: int) -> bool:
        if user_id == OWNER_ID:
            return True
        cursor = self.conn.cursor()
        cursor.execute('SELECT 1 FROM sudo_users WHERE user_id = ?', (user_id,))
        return cursor.fetchone() is not None

