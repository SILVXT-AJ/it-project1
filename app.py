from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'super_secret_key_123'

# --- 1. SET ABSOLUTE PATHS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database.db')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def log_activity(action):
    try:
        conn = get_db_connection()
        conn.execute('INSERT INTO activity_logs (action) VALUES (?)', (action,))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Log Error: {e}")

# --- ROUTES ---

@app.route('/')
def home():
    try:
        conn = get_db_connection()
        recent_events = conn.execute('SELECT * FROM events ORDER BY event_date DESC LIMIT 3').fetchall()
        recent_photos = conn.execute('SELECT * FROM gallery ORDER BY upload_date DESC LIMIT 6').fetchall()
        conn.close()
        return render_template('index.html', recent_events=recent_events, recent_photos=recent_photos)
    except Exception as e:
        print(f"Database Error: {e}")
        return render_template('index.html', recent_events=[], recent_photos=[])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and user['password'] == password:
            session['admin'] = True
            log_activity(f"User logged in: {username}")
            return redirect(url_for('dashboard'))
        else:
            log_activity(f"Failed login attempt for: {username}")
            flash('Invalid Credentials', 'danger')
            
    return render_template('login.html')

# --- ONLY ONE LOGOUT FUNCTION HERE ---
@app.route('/logout')
def logout():
    if session.get('admin'):
        log_activity("User logged out")
    session.pop('admin', None)
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if not session.get('admin'): return redirect(url_for('login'))
    conn = get_db_connection()
    events = conn.execute('SELECT * FROM events ORDER BY event_date DESC').fetchall()
    photos = conn.execute('SELECT * FROM gallery ORDER BY upload_date DESC').fetchall()
    materials = conn.execute('SELECT * FROM materials ORDER BY upload_date DESC').fetchall()
    conn.close()
    return render_template('dashboard.html', events=events, photos=photos, materials=materials)

# --- EVENTS ---
@app.route('/events')
def events():
    conn = get_db_connection()
    events = conn.execute('SELECT * FROM events ORDER BY event_date DESC').fetchall()
    conn.close()
    return render_template('events.html', events=events)

@app.route('/add_event', methods=['POST'])
def add_event():
    if not session.get('admin'): return redirect(url_for('login'))
    image = request.files.get('image_file')
    filename = ""
    if image and image.filename != '':
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    
    conn = get_db_connection()
    conn.execute('INSERT INTO events (title, event_date, event_manager, contact_number, description, image_file) VALUES (?, ?, ?, ?, ?, ?)',
                 (request.form['title'], request.form['event_date'], request.form['event_manager'], 
                  request.form['contact_number'], request.form['description'], filename))
    conn.commit()
    conn.close()
    log_activity(f"Added event: {request.form['title']}")
    return redirect(url_for('dashboard'))

@app.route('/edit_event/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    if not session.get('admin'): return redirect(url_for('login'))
    conn = get_db_connection()
    
    if request.method == 'POST':
        conn.execute('UPDATE events SET title=?, event_date=?, event_manager=?, contact_number=?, description=? WHERE id=?',
                     (request.form['title'], request.form['event_date'], request.form['event_manager'], 
                      request.form['contact_number'], request.form['description'], event_id))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
        
    event = conn.execute('SELECT * FROM events WHERE id = ?', (event_id,)).fetchone()
    conn.close()
    return render_template('edit_event.html', event=event)

@app.route('/delete_event/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    if not session.get('admin'): return redirect(url_for('login'))
    conn = get_db_connection()
    conn.execute('DELETE FROM events WHERE id = ?', (event_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

# --- GALLERY ---
@app.route('/gallery')
def gallery():
    conn = get_db_connection()
    photos = conn.execute('SELECT * FROM gallery ORDER BY upload_date DESC').fetchall()
    conn.close()
    return render_template('gallery.html', photos=photos)

@app.route('/upload_photo', methods=['POST'])
def upload_photo():
    if not session.get('admin'): return redirect(url_for('login'))
    image = request.files.get('image_file')
    if image and image.filename != '':
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        conn = get_db_connection()
        conn.execute('INSERT INTO gallery (image_file, caption) VALUES (?, ?)', (filename, request.form['caption']))
        conn.commit()
        conn.close()
    return redirect(url_for('dashboard'))

@app.route('/edit_photo/<int:photo_id>', methods=['GET', 'POST'])
def edit_photo(photo_id):
    if not session.get('admin'): return redirect(url_for('login'))
    conn = get_db_connection()
    if request.method == 'POST':
        conn.execute('UPDATE gallery SET caption=? WHERE id=?', (request.form['caption'], photo_id))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
    photo = conn.execute('SELECT * FROM gallery WHERE id = ?', (photo_id,)).fetchone()
    conn.close()
    return render_template('edit_photo.html', photo=photo)

@app.route('/delete_photo/<int:photo_id>', methods=['POST'])
def delete_photo(photo_id):
    if not session.get('admin'): return redirect(url_for('login'))
    conn = get_db_connection()
    conn.execute('DELETE FROM gallery WHERE id = ?', (photo_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

# --- MATERIALS ---
@app.route('/materials')
def materials():
    conn = get_db_connection()
    materials = conn.execute('SELECT * FROM materials ORDER BY upload_date DESC').fetchall()
    conn.close()
    return render_template('materials.html', materials=materials)

@app.route('/add_material', methods=['POST'])
def add_material():
    if not session.get('admin'): return redirect(url_for('login'))
    conn = get_db_connection()
    conn.execute('INSERT INTO materials (title, subject, target_year, semester, file_link) VALUES (?, ?, ?, ?, ?)',
                 (request.form['title'], request.form['subject'], request.form['target_year'], 
                  request.form['semester'], request.form['file_link']))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/edit_material/<int:id>', methods=['GET', 'POST'])
def edit_material(id):
    if not session.get('admin'): return redirect(url_for('login'))
    conn = get_db_connection()
    if request.method == 'POST':
        conn.execute('UPDATE materials SET title=?, subject=?, target_year=?, semester=?, file_link=? WHERE id=?',
                     (request.form['title'], request.form['subject'], request.form['target_year'], 
                      request.form['semester'], request.form['file_link'], id))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
    material = conn.execute('SELECT * FROM materials WHERE id = ?', (id,)).fetchone()
    conn.close()
    return render_template('edit_material.html', material=material)

@app.route('/delete_material/<int:id>', methods=['POST'])
def delete_material(id):
    if not session.get('admin'): return redirect(url_for('login'))
    conn = get_db_connection()
    conn.execute('DELETE FROM materials WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

# --- LOGS ---
@app.route('/logs')
def view_logs():
    if not session.get('admin'): return redirect(url_for('login'))
    conn = get_db_connection()
    try:
        logs = conn.execute('SELECT * FROM activity_logs ORDER BY timestamp DESC').fetchall()
    except:
        logs = []
    conn.close()
    return render_template('logs.html', logs=logs)

if __name__ == '__main__':
    app.run(debug=True)