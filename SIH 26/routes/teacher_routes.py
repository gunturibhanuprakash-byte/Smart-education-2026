from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
from routes.auth_routes import teacher_required
from database.db import query_db, get_db, execute_db
from services.performance_service import calculate_student_performance, get_performance_band

teacher_bp = Blueprint('teacher', __name__)

@teacher_bp.route('/dashboard')
@teacher_required
def dashboard():
    # 1. Class-wide aggregate stats
    total_students = query_db("SELECT COUNT(id) as count FROM students", one=True)['count']
    
    # Calculate average performance across all students
    avg_perf_row = query_db("""
        SELECT AVG(COALESCE(sm.internal_marks + sm.quiz_marks + sm.assignment_marks, 0)) as avg_score
        FROM student_marks sm
    """, one=True)
    class_average = round(avg_perf_row['avg_score'], 1) if avg_perf_row and avg_perf_row['avg_score'] else 72.4

    # 2. Identify students needing urgent support (performance < 60%)
    students = query_db("""
        SELECT s.*, u.full_name, u.email, u.username,
               ROUND(AVG(COALESCE(sm.internal_marks + sm.quiz_marks + sm.assignment_marks, 0)), 1) as avg_marks
        FROM students s
        JOIN users u ON s.user_id = u.id
        LEFT JOIN student_marks sm ON s.id = sm.student_id
        GROUP BY s.id
        ORDER BY avg_marks ASC
    """)

    for st in students:
        band_name, band_badge, band_color = get_performance_band(st['avg_marks'] or 0)
        st['performance_band'] = band_name
        st['band_badge'] = band_badge
        st['band_color'] = band_color

    students_needing_support = [s for s in students if (s['avg_marks'] or 0) < 60.0]
    top_students = [s for s in students if (s['avg_marks'] or 0) >= 75.0]

    # 3. Lowest scoring topic across the entire class
    lowest_topic = query_db("""
        SELECT t.name as topic_name, sub.name as subject_name, ROUND(AVG(stm.mastery_percentage), 1) as avg_mastery
        FROM student_topic_mastery stm
        JOIN topics t ON stm.topic_id = t.id
        JOIN subjects sub ON t.subject_id = sub.id
        GROUP BY t.id
        ORDER BY avg_mastery ASC
        LIMIT 1
    """, one=True)

    # 4. Recent quiz activity across all students
    recent_activity = query_db("""
        SELECT qa.*, u.full_name, sub.name as subject_name, t.name as topic_name
        FROM quiz_attempts qa
        JOIN students s ON qa.student_id = s.id
        JOIN users u ON s.user_id = u.id
        JOIN subjects sub ON qa.subject_id = sub.id
        LEFT JOIN topics t ON qa.topic_id = t.id
        ORDER BY qa.id DESC
        LIMIT 5
    """)

    # 5. Subject performance comparison for chart
    subject_stats = query_db("""
        SELECT sub.name, ROUND(AVG(sm.internal_marks + sm.quiz_marks + sm.assignment_marks), 1) as avg_score
        FROM subjects sub
        LEFT JOIN student_marks sm ON sub.id = sm.subject_id
        GROUP BY sub.id
    """)

    return render_template('teacher/dashboard.html',
                           total_students=total_students,
                           class_average=class_average,
                           students_needing_support=students_needing_support,
                           top_students=top_students,
                           lowest_topic=lowest_topic,
                           recent_activity=recent_activity,
                           subject_stats=subject_stats)

@teacher_bp.route('/students')
@teacher_required
def students():
    students_list = query_db("""
        SELECT s.*, u.full_name, u.email, u.username,
               ROUND(AVG(COALESCE(sm.internal_marks + sm.quiz_marks + sm.assignment_marks, 0)), 1) as avg_marks,
               COUNT(DISTINCT qa.id) as quiz_count
        FROM students s
        JOIN users u ON s.user_id = u.id
        LEFT JOIN student_marks sm ON s.id = sm.student_id
        LEFT JOIN quiz_attempts qa ON s.id = qa.student_id
        GROUP BY s.id
        ORDER BY s.id ASC
    """)

    for st in students_list:
        band_name, band_badge, band_color = get_performance_band(st['avg_marks'] or 0)
        st['performance_band'] = band_name
        st['band_badge'] = band_badge
        st['band_color'] = band_color

    return render_template('teacher/students.html', students=students_list)

@teacher_bp.route('/student/<int:student_id>')
@teacher_required
def student_detail(student_id):
    analytics = calculate_student_performance(student_id)
    if not analytics:
        flash('Student record not found.', 'danger')
        return redirect(url_for('teacher.students'))

    return render_template('teacher/student_detail.html', analytics=analytics)

@teacher_bp.route('/questions', methods=['GET', 'POST'])
@teacher_required
def questions():
    if request.method == 'POST':
        subject_id = request.form.get('subject_id')
        topic_id = request.form.get('topic_id')
        question_text = request.form.get('question_text')
        option_a = request.form.get('option_a')
        option_b = request.form.get('option_b')
        option_c = request.form.get('option_c')
        option_d = request.form.get('option_d')
        correct_option = request.form.get('correct_option')
        difficulty = request.form.get('difficulty')
        explanation = request.form.get('explanation')

        with get_db() as conn:
            conn.execute("""
                INSERT INTO questions (subject_id, topic_id, question_text, option_a, option_b, option_c, option_d, correct_option, difficulty, explanation, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (subject_id, topic_id, question_text, option_a, option_b, option_c, option_d, correct_option, difficulty, explanation, session['user_id']))
        flash('Question created successfully!', 'success')
        return redirect(url_for('teacher.questions'))

    sub_filter = request.args.get('subject_id')
    diff_filter = request.args.get('difficulty')

    query = """
        SELECT q.*, sub.name as subject_name, t.name as topic_name
        FROM questions q
        JOIN subjects sub ON q.subject_id = sub.id
        JOIN topics t ON q.topic_id = t.id
        WHERE 1=1
    """
    args = []
    if sub_filter:
        query += " AND q.subject_id = ?"
        args.append(sub_filter)
    if diff_filter:
        query += " AND q.difficulty = ?"
        args.append(diff_filter)
    query += " ORDER BY q.id DESC"

    questions_list = query_db(query, tuple(args))
    subjects = query_db("SELECT * FROM subjects")
    topics = query_db("SELECT * FROM topics")

    return render_template('teacher/questions.html',
                           questions=questions_list,
                           subjects=subjects,
                           topics=topics,
                           current_sub=sub_filter,
                           current_diff=diff_filter)

@teacher_bp.route('/questions/delete/<int:question_id>', methods=['POST'])
@teacher_required
def delete_question(question_id):
    with get_db() as conn:
        conn.execute("DELETE FROM questions WHERE id = ?", (question_id,))
    flash('Question deleted successfully.', 'info')
    return redirect(url_for('teacher.questions'))

@teacher_bp.route('/materials', methods=['GET', 'POST'])
@teacher_required
def materials():
    if request.method == 'POST':
        title = request.form.get('title')
        subject_id = request.form.get('subject_id')
        topic_id = request.form.get('topic_id')
        resource_type = request.form.get('resource_type')
        difficulty = request.form.get('difficulty')
        description = request.form.get('description')
        content = request.form.get('content')
        link_url = request.form.get('link_url')

        with get_db() as conn:
            conn.execute("""
                INSERT INTO learning_materials (subject_id, topic_id, title, resource_type, difficulty, description, content, link_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (subject_id, topic_id, title, resource_type, difficulty, description, content, link_url))
        flash('Learning resource added successfully!', 'success')
        return redirect(url_for('teacher.materials'))

    materials_list = query_db("""
        SELECT lm.*, sub.name as subject_name, t.name as topic_name
        FROM learning_materials lm
        JOIN subjects sub ON lm.subject_id = sub.id
        JOIN topics t ON lm.topic_id = t.id
        ORDER BY lm.id DESC
    """)
    subjects = query_db("SELECT * FROM subjects")
    topics = query_db("SELECT * FROM topics")

    return render_template('teacher/materials.html',
                           materials=materials_list,
                           subjects=subjects,
                           topics=topics)

@teacher_bp.route('/materials/delete/<int:material_id>', methods=['POST'])
@teacher_required
def delete_material(material_id):
    with get_db() as conn:
        conn.execute("DELETE FROM learning_materials WHERE id = ?", (material_id,))
    flash('Learning resource deleted.', 'info')
    return redirect(url_for('teacher.materials'))

@teacher_bp.route('/marks-manage', methods=['GET', 'POST'])
@teacher_required
def marks_manage():
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        subject_id = request.form.get('subject_id')
        internal_marks = float(request.form.get('internal_marks', 0))
        quiz_marks = float(request.form.get('quiz_marks', 0))
        assignment_marks = float(request.form.get('assignment_marks', 0))
        
        total = internal_marks + quiz_marks + assignment_marks
        if total >= 90:
            grade = 'A+'
        elif total >= 80:
            grade = 'A'
        elif total >= 70:
            grade = 'B+'
        elif total >= 60:
            grade = 'B'
        elif total >= 50:
            grade = 'C'
        else:
            grade = 'F'

        with get_db() as conn:
            conn.execute("""
                INSERT INTO student_marks (student_id, subject_id, internal_marks, quiz_marks, assignment_marks, grade)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(student_id, subject_id) DO UPDATE SET
                    internal_marks = excluded.internal_marks,
                    quiz_marks = excluded.quiz_marks,
                    assignment_marks = excluded.assignment_marks,
                    grade = excluded.grade,
                    updated_at = CURRENT_TIMESTAMP
            """, (student_id, subject_id, internal_marks, quiz_marks, assignment_marks, grade))
        flash('Student marks updated successfully!', 'success')
        return redirect(url_for('teacher.marks_manage'))

    students = query_db("SELECT s.id, u.full_name, s.student_code FROM students s JOIN users u ON s.user_id = u.id")
    subjects = query_db("SELECT id, name FROM subjects")
    all_marks = query_db("""
        SELECT sm.*, u.full_name, s.student_code, sub.name as subject_name,
               (sm.internal_marks + sm.quiz_marks + sm.assignment_marks) as total_marks
        FROM student_marks sm
        JOIN students s ON sm.student_id = s.id
        JOIN users u ON s.user_id = u.id
        JOIN subjects sub ON sm.subject_id = sub.id
        ORDER BY s.id, sub.id
    """)

    return render_template('teacher/marks_manage.html',
                           students=students,
                           subjects=subjects,
                           all_marks=all_marks)
