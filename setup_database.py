import mysql.connector
from mysql.connector import Error

def create_database():
    try:
        # Connect to MySQL server (without specifying a database)
        connection = mysql.connector.connect(
            host='localhost',
            user='root',  # Replace with your MySQL username
            password=''   # Replace with your MySQL password
        )

        if connection.is_connected():
            cursor = connection.cursor()

            # Create database if it doesn't exist
            cursor.execute("CREATE DATABASE IF NOT EXISTS it_department_db")
            print("Database 'it_department_db' created successfully")

            # Switch to the database
            cursor.execute("USE it_department_db")

            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL
                )
            """)
            print("Table 'users' created successfully")

            # Insert static admin user
            cursor.execute("""
                INSERT IGNORE INTO users (username, password) VALUES ('admin', 'admin123')
            """)
            print("Admin user inserted successfully")

            # Create events table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    event_date DATE
                )
            """)
            print("Table 'events' created successfully")

            # Create blogs table (for achievements)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS blogs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    content TEXT,
                    image_url VARCHAR(500)
                )
            """)
            print("Table 'blogs' created successfully")

            # Create materials table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS materials (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    subject VARCHAR(100),
                    file_link VARCHAR(500)
                )
            """)
            print("Table 'materials' created successfully")

            connection.commit()

    except Error as e:
        print(f"Error: {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed")

if __name__ == "__main__":
    create_database()
