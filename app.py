from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'supersecretkey'

#  database
def init_db():
    with sqlite3.connect('users.db') as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )''')

init_db()

# Home Page - list users
@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect('users.db')
    users = conn.execute("SELECT id, name, email FROM users").fetchall()
    conn.close()
    return render_template('index.html', users=users)

# Register New User
@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        try:
            with sqlite3.connect('users.db') as conn:
                conn.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                             (name, email, password))
                flash('User registered successfully!', 'success')
                return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already exists!', 'danger')

    return render_template('create.html')

# Update User
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    with sqlite3.connect('users.db') as conn:
        user = conn.execute("SELECT * FROM users WHERE id = ?", (id,)).fetchone()

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        with sqlite3.connect('users.db') as conn:
            conn.execute("UPDATE users SET name = ?, email = ? WHERE id = ?", (name, email, id))
            flash('User updated successfully!', 'info')
            return redirect(url_for('index'))

    return render_template('update.html', user=user)

# Delete User
@app.route('/delete/<int:id>')
def delete(id):
    with sqlite3.connect('users.db') as conn:
        conn.execute("DELETE FROM users WHERE id = ?", (id,))
        flash('User deleted!', 'warning')
    return redirect(url_for('index'))

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        with sqlite3.connect('users.db') as conn:
            user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
            if user and check_password_hash(user[3], password):
                session['user'] = user[1]
                flash('Login successful!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid credentials!', 'danger')

    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))

# Handle 404 errors
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
