# database.py
import bcrypt
import mysql.connector
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

class Database:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        # Tabla de usuarios
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) UNIQUE,
            password VARCHAR(255) NOT NULL,
            ngrama INT DEFAULT 0
        )
        """)
        # Tabla de entradas del diario
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS diary_entries (
            user_id INT,
            date DATE,
            entry TEXT,
            happy DECIMAL(3,2),
            angry DECIMAL(3,2),
            surprise DECIMAL(3,2),
            sad DECIMAL(3,2),
            fear DECIMAL(3,2),
            UNIQUE (user_id, date),
            PRIMARY KEY (user_id, date),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """)
        # Tabla de historial de chat
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            date DATETIME,
            human_message TEXT,
            bot_message TEXT,
            happy DECIMAL(3,2),
            angry DECIMAL(3,2),
            surprise DECIMAL(3,2),
            sad DECIMAL(3,2),
            fear DECIMAL(3,2),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """)
        self.conn.commit()
        cursor.close()

    def register_user(self, username: str, password: str):
        cursor = self.conn.cursor()
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed))
        self.conn.commit()
        cursor.close()

    def verify_user(self, username: str, password: str) -> bool:
        cursor = self.conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
        row = cursor.fetchone()
        cursor.close()
        if row is None:
            return False
        stored = row[0]
        return bcrypt.checkpw(password.encode('utf-8'), stored.encode('utf-8'))

    def get_user_id(self, username: str):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        row = cursor.fetchone()
        cursor.close()
        return row[0] if row else None

    def insert_diary_entry(self, username: str, entry_data: dict):
        user_id = self.get_user_id(username)
        if user_id is None:
            return
        cursor = self.conn.cursor()
        query = """
        INSERT INTO diary_entries (user_id, date, entry, happy, angry, surprise, sad, fear)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
          entry = VALUES(entry),
          happy = VALUES(happy),
          angry = VALUES(angry),
          surprise = VALUES(surprise),
          sad = VALUES(sad),
          fear = VALUES(fear)
        """
        cursor.execute(query, (
            user_id,
            entry_data['date'],
            entry_data['entry'],
            entry_data['emotions']['Happy'],
            entry_data['emotions']['Angry'],
            entry_data['emotions']['Surprise'],
            entry_data['emotions']['Sad'],
            entry_data['emotions']['Fear']
        ))
        self.conn.commit()
        cursor.close()

    def get_diary_entries(self, username: str, limit: int = 50) -> list:
        user_id = self.get_user_id(username)
        if user_id is None:
            return []
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT date, entry, happy, angry, surprise, sad, fear
            FROM diary_entries
            WHERE user_id = %s
            ORDER BY date DESC
            LIMIT %s
        """, (user_id, limit))
        rows = cursor.fetchall()
        cursor.close()
        entries = []
        for row in rows:
            entries.append({
                "date": row[0].strftime("%Y-%m-%d"),
                "entry": row[1],
                "emotions": {
                    "Happy": float(row[2]),
                    "Angry": float(row[3]),
                    "Surprise": float(row[4]),
                    "Sad": float(row[5]),
                    "Fear": float(row[6])
                }
            })
        return entries

    def insert_chat_history(self, username: str, chat_data: dict):
        user_id = self.get_user_id(username)
        if user_id is None:
            return
        cursor = self.conn.cursor()
        query = """
        INSERT INTO chat_history (user_id, date, human_message, bot_message, happy, angry, surprise, sad, fear)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            user_id,
            chat_data['date'],
            chat_data['human_message'],
            chat_data['bot_message'],
            chat_data['emotions']['Happy'],
            chat_data['emotions']['Angry'],
            chat_data['emotions']['Surprise'],
            chat_data['emotions']['Sad'],
            chat_data['emotions']['Fear']
        ))
        self.conn.commit()
        cursor.close()

    def get_chat_history(self, username: str, limit: int = 10) -> list:
        user_id = self.get_user_id(username)
        if user_id is None:
            return []
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT human_message, bot_message, date
            FROM chat_history
            WHERE user_id = %s
            ORDER BY date DESC
            LIMIT %s
        """, (user_id, limit))
        rows = cursor.fetchall()
        cursor.close()
        messages = []
        for row in reversed(rows):
            messages.append({"role": "user", "content": row[0]})
            messages.append({"role": "assistant", "content": row[1]})
        return messages

    def close(self):
        self.conn.close()
