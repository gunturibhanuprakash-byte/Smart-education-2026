import os
from flask import Flask, render_template, redirect, url_for, session
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from database.db import DB_PATH, init_db
from database.seed import seed_database
from routes.auth_routes import auth_bp
from routes.student_routes import student_bp
from routes.teacher_routes import teacher_bp
from routes.quiz_routes import quiz_bp
from routes.api_routes import api_bp

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'smart-education-hackathon-secret-key-2026')

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(student_bp, url_prefix='/student')
app.register_blueprint(teacher_bp, url_prefix='/teacher')
app.register_blueprint(quiz_bp, url_prefix='/quiz')
app.register_blueprint(api_bp, url_prefix='/api')

@app.context_processor
def inject_user_context():
    """Injects session and role context into all Jinja templates."""
    return {
        'current_user': {
            'user_id': session.get('user_id'),
            'username': session.get('username'),
            'role': session.get('role'),
            'full_name': session.get('full_name')
        },
        'is_student': session.get('role') == 'student',
        'is_teacher': session.get('role') == 'teacher'
    }

@app.route('/')
def index():
    """Root route redirecting based on authentication state."""
    if 'user_id' in session:
        if session.get('role') == 'teacher':
            return redirect(url_for('teacher.dashboard'))
        return redirect(url_for('student.dashboard'))
    return redirect(url_for('auth.login'))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('login.html', error_msg="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('login.html', error_msg="An internal server error occurred"), 500

if __name__ == '__main__':
    # Ensure database exists and is seeded on startup
    if not os.path.exists(DB_PATH):
        print("Database not found. Initializing and seeding...")
        seed_database()
        
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Smart Education Platform on http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
