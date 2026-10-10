from flask import Blueprint, render_template, request, redirect, url_for, session, flash, g
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash
from database.db import query_db, execute_db, get_db

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        if session.get('role') != 'student':
            flash('Unauthorized access: Student role required.', 'danger')
            return redirect(url_for('teacher.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def teacher_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        if session.get('role') != 'teacher':
            flash('Unauthorized access: Teacher role required.', 'danger')
            return redirect(url_for('student.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        if session.get('role') == 'teacher':
            return redirect(url_for('teacher.dashboard'))
        return redirect(url_for('student.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        user = query_db("SELECT * FROM users WHERE username = ? OR email = ?", (username, username), one=True)
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['full_name'] = user['full_name']
            
            if user['role'] == 'student':
                student = query_db("SELECT id FROM students WHERE user_id = ?", (user['id'],), one=True)
                if student:
                    session['student_id'] = student['id']
                flash(f"Welcome back, {user['full_name']}!", 'success')
                return redirect(url_for('student.dashboard'))
            else:
                teacher = query_db("SELECT id FROM teachers WHERE user_id = ?", (user['id'],), one=True)
                if teacher:
                    session['teacher_id'] = teacher['id']
                flash(f"Welcome back, {user['full_name']}!", 'success')
                return redirect(url_for('teacher.dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')
            
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        full_name = request.form.get('full_name', '').strip()
        role = request.form.get('role', 'student').strip()
        
        existing = query_db("SELECT id FROM users WHERE username = ? OR email = ?", (username, email), one=True)
        if existing:
            flash('Username or email already exists.', 'warning')
            return redirect(url_for('auth.register'))
            
        pw_hash = generate_password_hash(password)
        with get_db() as conn:
            cur = conn.execute("""
                INSERT INTO users (username, password_hash, role, full_name, email)
                VALUES (?, ?, ?, ?, ?)
            """, (username, pw_hash, role, full_name, email))
            uid = cur.lastrowid
            
            if role == 'student':
                conn.execute("""
                    INSERT INTO students (user_id, student_code, branch, semester)
                    VALUES (?, ?, 'CSE', 'Semester 4')
                """, (uid, f"STU{uid:04d}"))
            else:
                conn.execute("""
                    INSERT INTO teachers (user_id, department, designation)
                    VALUES (?, 'Computer Science', 'Lecturer')
                """, (uid,))
                
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('login.html', is_register=True)

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))
