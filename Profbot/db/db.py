import aiosqlite
from datetime import datetime

DB_name = "quiz_results.sqlite3"

async def init_db():
    async with aiosqlite.connect(DB_name) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            time TEXT,
            user_id TEXT,
            result TEXT
        )
        """)
        await db.commit()


async def save_result(name, user_id, result):
    time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    async with aiosqlite.connect(DB_name) as db:
        await db.execute(
            "INSERT INTO results (name, time, user_id, result) VALUES (?, ?, ?, ?)",
            (name, time_str, user_id, result)
        )
        await db.commit()
