import os
from flask import Flask, render_template, request, redirect, session, url_for
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'fallback_secret_key')

# Database configuration
def get_db_connection():
    # DIRECT CONNECTION (Bypassing the .env file issues)
    conn = mysql.connector.connect(
        host="localhost",
        user="it_admin",
        password="ComplexPassword123!",
        database="it_department_db"  # <--- explicitly forcing the correct name
    )
    return conn

# Public Routes
@app.route('/')
def home():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get recent events
        cursor.execute("SELECT * FROM events ORDER BY event_date DESC LIMIT 3")
        recent_events = cursor.fetchall()
        
        # Get recent achievements
        cursor.execute("SELECT * FROM blogs ORDER BY id DESC LIMIT 3")
        recent_blogs = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return render_template('index.html', recent_events=recent_events, recent_blogs=recent_blogs)
    except Error as e:
        print(f"Error: {e}")
        return render_template('index.html', recent_events=[], recent_blogs=[])

@app.route('/events')
def events():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM events ORDER BY event_date DESC")
        events = cursor.fetchall()
        cursor.close()
        connection.close()
        return render_template('programs.html', events=events)
    except Error as e:
        print(f"Error: {e}")
        return render_template('programs.html', events=[])

@app.route('/achievements')
def achievements():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM blogs ORDER BY id DESC")
        blogs = cursor.fetchall()
        cursor.close()
        connection.close()
        return render_template('about.html', blogs=blogs)
    except Error as e:
        print(f"Error: {e}")
        return render_template('about.html', blogs=[])

@app.route('/materials')
def materials():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM materials ORDER BY id DESC")
        materials = cursor.fetchall()
        cursor.close()
        connection.close()
        return render_template('materials.html', materials=materials)
    except Error as e:
        print(f"Error: {e}")
        return render_template('materials.html', materials=[])

@app.route('/event/<int:event_id>')
def event_detail(event_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM events WHERE id = %s", (event_id,))
        event = cursor.fetchone()
        cursor.close()
        connection.close()
        if event:
            return render_template('event_detail.html', event=event)
        else:
            return "Event not found", 404
    except Error as e:
        print(f"Error: {e}")
        return "Database error", 500

# Admin Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
            user = cursor.fetchone()
            cursor.close()
            connection.close()
            
            if user:
                session['admin'] = user['username']
                return redirect(url_for('dashboard'))
            else:
                return render_template('login.html', error='Invalid credentials')
        except Error as e:
            print(f"Error: {e}")
            return render_template('login.html', error='Database error')
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'admin' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/add_event', methods=['POST'])
def add_event():
    if 'admin' not in session:
        return redirect(url_for('login'))
    
    title = request.form['title']
    description = request.form['description']
    event_date = request.form['event_date']
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO events (title, description, event_date) VALUES (%s, %s, %s)",
                       (title, description, event_date))
        connection.commit()
        cursor.close()
        connection.close()
    except Error as e:
        print(f"Error: {e}")
    
    return redirect(url_for('dashboard'))

@app.route('/add_achievement', methods=['POST'])
def add_achievement():
    if 'admin' not in session:
        return redirect(url_for('login'))
    
    title = request.form['title']
    content = request.form['content']
    image_url = request.form['image_url']
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO blogs (title, content, image_url) VALUES (%s, %s, %s)",
                       (title, content, image_url))
        connection.commit()
        cursor.close()
        connection.close()
    except Error as e:
        print(f"Error: {e}")
    
    return redirect(url_for('dashboard'))

@app.route('/add_material', methods=['POST'])
def add_material():
    if 'admin' not in session:
        return redirect(url_for('login'))
    
    title = request.form['title']
    subject = request.form['subject']
    file_link = request.form['file_link']
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO materials (title, subject, file_link) VALUES (%s, %s, %s)",
                       (title, subject, file_link))
        connection.commit()
        cursor.close()
        connection.close()
    except Error as e:
        print(f"Error: {e}")
    
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
