import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database.db')

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
rows = conn.execute('SELECT * FROM hackathon_registrations').fetchall()

print(f"Found {len(rows)} registrations.")
for row in rows:
    print(f"ID: {row['id']}, Proof: {row['payment_proof']}, College: {row['college_name']}")

conn.close()
