from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # for sessions

# Database connection
def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Home page
@app.route('/')
def index():
    return render_template('index.html')

# Sign Up
@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        conn = get_db()
        conn.execute(
            "INSERT INTO users (name,email,password,role) VALUES (?,?,?,?)",
            (name,email,password,'volunteer')
        )
        conn.commit()
        conn.close()
        return redirect('/login')
    return render_template('signup.html')

# Login
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE email=? AND password=?", (email,password)
        ).fetchone()
        conn.close()
        if user:
            session['user'] = user['id']
            session['role'] = user['role']
            return redirect('/dashboard')
    return render_template('login.html')

# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    return render_template('dashboard.html')

# Chat
@app.route('/chat', methods=['GET','POST'])
def chat():
    conn = get_db()
    if request.method == 'POST':
        message = request.form['message']
        user_id = session['user']
        timestamp = datetime.now()
        conn.execute(
            "INSERT INTO messages (user_id,content,timestamp) VALUES (?,?,?)",
            (user_id,message,timestamp)
        )
        conn.commit()
    messages = conn.execute(
        "SELECT m.content, u.name, m.timestamp FROM messages m "
        "JOIN users u ON m.user_id=u.id ORDER BY m.timestamp ASC"
    ).fetchall()
    conn.close()
    return render_template('chat.html', messages=messages)

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)

