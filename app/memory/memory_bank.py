import sqlite3, os
from app.logger import logger

DB = os.path.join(os.getenv("OUTPUT_DIR","outputs"), "memory_bank.db")

class MemoryBank:
    def __init__(self):
        os.makedirs(os.path.dirname(DB), exist_ok=True)
        self.conn = sqlite3.connect(DB, check_same_thread=False)
        self._init()

    def _init(self):
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_prefs (
                user_id TEXT PRIMARY KEY,
                prefs_json TEXT,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS past_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                topic TEXT,
                plan_path TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def save_prefs(self, user_id, prefs_json):
        cur = self.conn.cursor()
        cur.execute("INSERT OR REPLACE INTO user_prefs (user_id, prefs_json) VALUES (?, ?)", (user_id, prefs_json))
        self.conn.commit()

    def get_prefs(self, user_id):
        cur = self.conn.cursor()
        cur.execute("SELECT prefs_json FROM user_prefs WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        return row[0] if row else None

    def save_plan(self, user_id, topic, path):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO past_plans (user_id, topic, plan_path) VALUES (?, ?, ?)", (user_id, topic, path))
        self.conn.commit()

    def list_plans(self, user_id, limit=10):
        cur = self.conn.cursor()
        cur.execute("SELECT topic, plan_path, created_at FROM past_plans WHERE user_id = ? ORDER BY created_at DESC LIMIT ?", (user_id, limit))
        return cur.fetchall()
