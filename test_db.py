import os
import mysql.connector
from dotenv import load_dotenv

# 1. Load the secrets
load_dotenv()

print("--- TESTING DATABASE CONNECTION ---")
print(f"User: {os.getenv('DB_USER')}")
print(f"Database: {os.getenv('DB_NAME')}")

try:
    # 2. Try to connect
    conn = mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )
    
    # 3. If successful
    if conn.is_connected():
        print("✅ SUCCESS! Connected to the database.")
        print("Server Info:", conn.get_server_info())
        conn.close()
    else:
        print("❌ FAILED: Connection object created but not connected.")

except mysql.connector.Error as err:
    # 4. If it fails, PRINT THE REASON
    print(f"\n❌ ERROR: {err}")
    print("-----------------------------------")
    print("FIX SUGGESTIONS:")
    if "Access denied" in str(err):
        print(" -> Check your PASSWORD in the .env file.")
        print(" -> Check if the user 'it_admin' was actually created in phpMyAdmin.")
    elif "Unknown database" in str(err):
        print(" -> Check the DB_NAME in .env file.")
    elif "Can't connect" in str(err):
        print(" -> Is XAMPP (MySQL) running?")

except Exception as e:
    print(f"\n❌ GENERAL ERROR: {e}")