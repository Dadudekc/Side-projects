import sqlite3

DB_FILE = "ai_refactor_reviews.db"

def initialize_database():
    """Creates the required database table if it doesn't exist."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS refactor_reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT NOT NULL,
            original_code TEXT NOT NULL,
            ai_suggestion TEXT NOT NULL,
            human_feedback TEXT DEFAULT NULL
        )
        """)
        conn.commit()

if __name__ == "__main__":
    initialize_database()
    print("✅ Database initialized successfully!")
