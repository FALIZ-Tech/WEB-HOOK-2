import sqlite3
import json
from datetime import datetime
from contextlib import contextmanager
from config import Config

class Database:
    """SQLite database manager for conversation memory"""
    
    def __init__(self, db_path=None):
        self.db_path = db_path or Config.DATABASE_PATH
        self.init_db()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def init_db(self):
        """Initialize database tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    language_preference TEXT,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP
                )
            ''')
            
            # Conversations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    conversation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    created_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')
            
            # Messages table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id INTEGER NOT NULL,
                    user_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    detected_language TEXT,
                    created_at TIMESTAMP,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id),
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')
            
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON users(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversation_user ON conversations(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id)')
    
    def create_user(self, user_id, language_preference=None):
        """Create or update user record"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.utcnow().isoformat()
            
            cursor.execute('''
                INSERT OR IGNORE INTO users (user_id, language_preference, created_at, updated_at)
                VALUES (?, ?, ?, ?)
            ''', (user_id, language_preference, now, now))
            
            if language_preference:
                cursor.execute('''
                    UPDATE users SET language_preference = ?, updated_at = ? WHERE user_id = ?
                ''', (language_preference, now, user_id))
    
    def get_user(self, user_id):
        """Get user record"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def create_conversation(self, user_id):
        """Create new conversation"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.utcnow().isoformat()
            
            cursor.execute('''
                INSERT INTO conversations (user_id, created_at)
                VALUES (?, ?)
            ''', (user_id, now))
            
            return cursor.lastrowid
    
    def store_message(self, conversation_id, user_id, role, content, detected_language=None):
        """Store message in database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.utcnow().isoformat()
            
            cursor.execute('''
                INSERT INTO messages (conversation_id, user_id, role, content, detected_language, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (conversation_id, user_id, role, content, detected_language, now))
            
            return cursor.lastrowid
    
    def get_conversation_history(self, conversation_id, limit=50):
        """Get conversation history"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT role, content, detected_language, created_at
                FROM messages
                WHERE conversation_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (conversation_id, limit))
            
            rows = cursor.fetchall()
            return [dict(row) for row in reversed(rows)]
    
    def get_user_conversations(self, user_id, limit=10):
        """Get user's conversations"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT conversation_id, created_at
                FROM conversations
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (user_id, limit))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_latest_conversation(self, user_id):
        """Get user's latest conversation"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT conversation_id, created_at
                FROM conversations
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT 1
            ''', (user_id,))
            
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def delete_conversation(self, conversation_id):
        """Delete a conversation and its messages"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM messages WHERE conversation_id = ?', (conversation_id,))
            cursor.execute('DELETE FROM conversations WHERE conversation_id = ?', (conversation_id,))
