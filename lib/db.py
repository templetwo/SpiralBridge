import sqlite3

def init_db():
    conn = sqlite3.connect('spiral_bridge.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS memory_artifacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT,
            text TEXT,
            tone TEXT,
            glyphs TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
