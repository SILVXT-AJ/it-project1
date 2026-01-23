import mysql.connector

print("--- DIRECT CONNECTION TEST ---")

try:
    # We are typing the password directly here to prove it works
    conn = mysql.connector.connect(
        host="localhost",
        user="it_admin",
        password="ComplexPassword123!",
        database="it_department_db"
    )
    
    if conn.is_connected():
        print("✅ VICTORY! The database is working perfectly.")
        print("The issue was just your .env file not loading.")
        conn.close()
    else:
        print("❌ Connected but something is wrong.")

except Exception as e:
    print(f"\n❌ STILL FAILING: {e}")