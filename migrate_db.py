import sqlite3
import os

DB_PATH = os.path.join(os.getcwd(), 'database.db')

def migrate_db():
    conn = sqlite3.connect(DB_PATH)
    try:
        print("Attempting to add 'participation_type' column...")
        conn.execute('ALTER TABLE hackathon_registrations ADD COLUMN participation_type TEXT DEFAULT "Solo"')
        conn.commit()
        print("Column added successfully.")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e):
            print("Column 'participation_type' already exists.")
        else:
            print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_db()
