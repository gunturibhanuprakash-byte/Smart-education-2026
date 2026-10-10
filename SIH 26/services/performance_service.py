from database.db import get_db, query_db

def get_performance_band(percentage):
    """Classify percentage into standard educational mastery bands."""
    if percentage >= 90.0:
        return 'Excellent', 'success', '#10b981'
    elif percentage >= 75.0:
        return 'Good', 'primary', '#4361ee'
    elif percentage >= 60.0:
        return 'Average', 'info', '#f59e0b'
    elif percentage >= 40.0:
        return 'Needs Improvement', 'warning', '#f97316'
    else:
        return 'Very Weak', 'danger', '#ef4444'

def calculate_student_performance(student_id):
    """Calculates overall student analytics, topic masteries, strengths, and weaknesses."""
    # 1. Fetch Student profile & marks
    student = query_db("""
        SELECT s.*, u.full_name, u.email, u.username
        FROM students s
        JOIN users u ON s.user_id = u.id
        WHERE s.id = ?
    """, (student_id,), one=True)
    
    if not student:
        return None

    # 2. Subject-wise marks summary
    subject_marks = query_db("""
        SELECT sm.*, sub.code as subject_code, sub.name as subject_name, sub.color_theme, sub.icon
        FROM student_marks sm
        JOIN subjects sub ON sm.subject_id = sub.id
        WHERE sm.student_id = ?
    """, (student_id,))
    
    # Calculate overall marks percentage
    if subject_marks:
        total_obtained = sum((sm['internal_marks'] + sm['quiz_marks'] + sm['assignment_marks']) for sm in subject_marks)
        total_max = sum(sm['max_marks'] for sm in subject_marks)
        overall_pct = round((total_obtained / total_max) * 100.0, 1) if total_max > 0 else 0.0
    else:
        overall_pct = student['overall_percentage'] or 0.0

    band_name, band_badge, band_color = get_performance_band(overall_pct)

    # 3. Topic mastery list
    topic_masteries = query_db("""
        SELECT stm.*, t.name as topic_name, t.difficulty_weight, sub.name as subject_name, sub.id as subject_id, sub.color_theme
        FROM student_topic_mastery stm
        JOIN topics t ON stm.topic_id = t.id
        JOIN subjects sub ON t.subject_id = sub.id
        WHERE stm.student_id = ?
        ORDER BY stm.mastery_percentage DESC
    """, (student_id,))

    strong_topics = [t for t in topic_masteries if t['mastery_percentage'] >= 75.0]
    weak_topics = [t for t in topic_masteries if t['mastery_percentage'] < 60.0]
    average_topics = [t for t in topic_masteries if 60.0 <= t['mastery_percentage'] < 75.0]

    # 4. Total questions answered & quiz attempts
    stats = query_db("""
        SELECT 
            COUNT(qa.id) as total_attempts,
            COALESCE(AVG(qa.percentage), 0) as avg_quiz_score,
            COALESCE(SUM(qa.total_questions), 0) as total_questions_solved
        FROM quiz_attempts qa
        WHERE qa.student_id = ?
    """, (student_id,), one=True)

    # 5. Recent quiz attempts
    recent_quizzes = query_db("""
        SELECT qa.*, sub.name as subject_name, t.name as topic_name
        FROM quiz_attempts qa
        JOIN subjects sub ON qa.subject_id = sub.id
        LEFT JOIN topics t ON qa.topic_id = t.id
        WHERE qa.student_id = ?
        ORDER BY qa.id DESC
        LIMIT 5
    """, (student_id,))

    return {
        'student': student,
        'overall_percentage': overall_pct,
        'performance_band': band_name,
        'band_badge': band_badge,
        'band_color': band_color,
        'subject_marks': subject_marks,
        'topic_masteries': topic_masteries,
        'strong_topics': strong_topics,
        'weak_topics': weak_topics,
        'average_topics': average_topics,
        'total_attempts': stats['total_attempts'],
        'avg_quiz_score': round(stats['avg_quiz_score'], 1),
        'total_questions_solved': stats['total_questions_solved'],
        'recent_quizzes': recent_quizzes
    }

def update_topic_mastery_after_quiz(student_id, topic_id, is_correct):
    """Incrementally updates mastery percentage when a question is answered."""
    with get_db() as conn:
        record = conn.execute("""
            SELECT * FROM student_topic_mastery WHERE student_id = ? AND topic_id = ?
        """, (student_id, topic_id)).fetchone()
        
        if record:
            total_att = record['total_attempted'] + 1
            total_corr = record['total_correct'] + (1 if is_correct else 0)
            new_pct = round((total_corr / total_att) * 100.0, 1)
            band_name, _, _ = get_performance_band(new_pct)
            
            conn.execute("""
                UPDATE student_topic_mastery
                SET total_attempted = ?, total_correct = ?, mastery_percentage = ?, status_band = ?, last_updated = CURRENT_TIMESTAMP
                WHERE student_id = ? AND topic_id = ?
            """, (total_att, total_corr, new_pct, band_name, student_id, topic_id))
        else:
            total_att = 1
            total_corr = 1 if is_correct else 0
            new_pct = 100.0 if is_correct else 0.0
            band_name, _, _ = get_performance_band(new_pct)
            conn.execute("""
                INSERT INTO student_topic_mastery (student_id, topic_id, total_attempted, total_correct, mastery_percentage, status_band)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (student_id, topic_id, total_att, total_corr, new_pct, band_name))
