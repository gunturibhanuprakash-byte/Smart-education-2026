from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
from routes.auth_routes import student_required
from database.db import query_db
from services.performance_service import calculate_student_performance
from services.recommendation_service import generate_recommendations

student_bp = Blueprint('student', __name__)

@student_bp.route('/dashboard')
@student_required
def dashboard():
    student_id = session.get('student_id')
    analytics = calculate_student_performance(student_id)
    if not analytics:
        flash('Student record not found.', 'danger')
        return redirect(url_for('auth.logout'))

    recommendations = generate_recommendations(student_id)[:3]
    subjects = query_db("""
        SELECT s.*, 
            COALESCE(sm.internal_marks + sm.quiz_marks + sm.assignment_marks, 0) as total_marks,
            COALESCE(sm.grade, 'N/A') as grade,
            COUNT(DISTINCT t.id) as topic_count
        FROM subjects s
        LEFT JOIN student_marks sm ON s.id = sm.subject_id AND sm.student_id = ?
        LEFT JOIN topics t ON s.id = t.subject_id
        GROUP BY s.id
    """, (student_id,))

    return render_template('student/dashboard.html',
                           analytics=analytics,
                           subjects=subjects,
                           recommendations=recommendations)

@student_bp.route('/subjects')
@student_required
def subjects():
    student_id = session.get('student_id')
    subjects_list = query_db("""
        SELECT s.*, 
            COALESCE(sm.internal_marks + sm.quiz_marks + sm.assignment_marks, 0) as total_marks,
            COALESCE(sm.grade, 'N/A') as grade,
            COUNT(DISTINCT t.id) as topic_count,
            COUNT(DISTINCT q.id) as question_count
        FROM subjects s
        LEFT JOIN student_marks sm ON s.id = sm.subject_id AND sm.student_id = ?
        LEFT JOIN topics t ON s.id = t.subject_id
        LEFT JOIN questions q ON s.id = q.subject_id
        GROUP BY s.id
    """, (student_id,))

    return render_template('student/subjects.html', subjects=subjects_list)

@student_bp.route('/subject/<int:subject_id>')
@student_required
def subject_detail(subject_id):
    student_id = session.get('student_id')
    subject = query_db("SELECT * FROM subjects WHERE id = ?", (subject_id,), one=True)
    if not subject:
        flash('Subject not found.', 'warning')
        return redirect(url_for('student.subjects'))

    marks = query_db("SELECT * FROM student_marks WHERE student_id = ? AND subject_id = ?", (student_id, subject_id), one=True)
    
    # Topic masteries for this specific subject
    topics = query_db("""
        SELECT t.*, 
            COALESCE(stm.mastery_percentage, 50.0) as mastery_percentage,
            COALESCE(stm.status_band, 'Average') as status_band,
            COALESCE(stm.total_attempted, 0) as total_attempted,
            COALESCE(stm.total_correct, 0) as total_correct
        FROM topics t
        LEFT JOIN student_topic_mastery stm ON t.id = stm.topic_id AND stm.student_id = ?
        WHERE t.subject_id = ?
        ORDER BY t.order_index ASC
    """, (student_id, subject_id))

    recommendations = generate_recommendations(student_id, subject_id=subject_id)
    materials = query_db("""
        SELECT lm.*, t.name as topic_name
        FROM learning_materials lm
        JOIN topics t ON lm.topic_id = t.id
        WHERE lm.subject_id = ?
        ORDER BY lm.id DESC
        LIMIT 6
    """, (subject_id,))

    # Quiz statistics for this subject
    quiz_stats = query_db("""
        SELECT COUNT(id) as attempts, COALESCE(AVG(percentage), 0) as avg_score
        FROM quiz_attempts
        WHERE student_id = ? AND subject_id = ?
    """, (student_id, subject_id), one=True)

    return render_template('student/subject_detail.html',
                           subject=subject,
                           marks=marks,
                           topics=topics,
                           recommendations=recommendations,
                           materials=materials,
                           quiz_stats=quiz_stats)

@student_bp.route('/marks')
@student_required
def marks():
    student_id = session.get('student_id')
    marks_list = query_db("""
        SELECT sm.*, sub.code as subject_code, sub.name as subject_name, sub.color_theme,
               (sm.internal_marks + sm.quiz_marks + sm.assignment_marks) as total_marks,
               ROUND(((sm.internal_marks + sm.quiz_marks + sm.assignment_marks) / sm.max_marks) * 100, 1) as percentage
        FROM student_marks sm
        JOIN subjects sub ON sm.subject_id = sub.id
        WHERE sm.student_id = ?
    """, (student_id,))

    if marks_list:
        total_obtained = sum(m['total_marks'] for m in marks_list)
        total_max = sum(m['max_marks'] for m in marks_list)
        overall_pct = round((total_obtained / total_max) * 100, 1) if total_max > 0 else 0.0
    else:
        total_obtained, total_max, overall_pct = 0, 0, 0.0

    return render_template('student/marks.html',
                           marks=marks_list,
                           total_obtained=total_obtained,
                           total_max=total_max,
                           overall_pct=overall_pct)

@student_bp.route('/performance')
@student_required
def performance():
    student_id = session.get('student_id')
    analytics = calculate_student_performance(student_id)
    recommendations = generate_recommendations(student_id)
    return render_template('student/performance.html', analytics=analytics, recommendations=recommendations)

@student_bp.route('/learning')
@student_required
def learning():
    student_id = session.get('student_id')
    subject_filter = request.args.get('subject_id')
    type_filter = request.args.get('type')

    query = """
        SELECT lm.*, t.name as topic_name, sub.name as subject_name, sub.color_theme
        FROM learning_materials lm
        JOIN topics t ON lm.topic_id = t.id
        JOIN subjects sub ON lm.subject_id = sub.id
        WHERE 1=1
    """
    args = []
    if subject_filter:
        query += " AND lm.subject_id = ?"
        args.append(subject_filter)
    if type_filter:
        query += " AND lm.resource_type = ?"
        args.append(type_filter)

    query += " ORDER BY lm.id DESC"
    materials = query_db(query, tuple(args))
    subjects = query_db("SELECT id, name FROM subjects")
    recommendations = generate_recommendations(student_id)[:2]

    return render_template('student/learning.html',
                           materials=materials,
                           subjects=subjects,
                           recommendations=recommendations,
                           current_sub=subject_filter,
                           current_type=type_filter)

@student_bp.route('/ai-tutor')
@student_required
def ai_tutor():
    student_id = session.get('student_id')
    analytics = calculate_student_performance(student_id)
    topics = query_db("SELECT id, name FROM topics ORDER BY name ASC")
    return render_template('student/ai_tutor.html', analytics=analytics, topics=topics)
