import mysql.connector
from mysql.connector import Error

def reset_admin():
    try:
        # Connect to MySQL server
        connection = mysql.connector.connect(
            host='localhost',
            user='admin',  # Replace with your MySQL username
            password='admin123',   # Replace with your MySQL password
            database='it_department_db'
        )

        if connection.is_connected():
            cursor = connection.cursor()

            # Check if users table exists
            cursor.execute("SHOW TABLES LIKE 'users'")
            table_exists = cursor.fetchone()

            if table_exists:
                # Delete existing admin user
                cursor.execute("DELETE FROM users WHERE username = 'admin'")
                print("Existing admin user deleted.")

                # Insert fresh admin user
                cursor.execute("INSERT INTO users (username, password) VALUES ('admin', 'admin123')")
                print("Fresh admin user inserted.")

                connection.commit()
                print("✅ Admin User Reset: admin / admin123")
            else:
                print("Users table does not exist. Please run setup_database.py first.")

    except Error as e:
        print(f"Error: {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed")

if __name__ == "__main__":
    reset_admin()
