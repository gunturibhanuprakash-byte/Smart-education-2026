from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
import json
from routes.auth_routes import student_required
from database.db import query_db
from services.adaptive_quiz_service import AdaptiveQuizEngine
from services.recommendation_service import generate_recommendations

quiz_bp = Blueprint('quiz', __name__)

@quiz_bp.route('/start')
@student_required
def start():
    student_id = session.get('student_id')
    pre_sub = request.args.get('subject_id')
    pre_topic = request.args.get('topic_id')
    
    subjects = query_db("SELECT * FROM subjects")
    topics = query_db("""
        SELECT t.*, sub.name as subject_name, sub.id as subject_id,
               COALESCE(stm.mastery_percentage, 50.0) as mastery_percentage
        FROM topics t
        JOIN subjects sub ON t.subject_id = sub.id
        LEFT JOIN student_topic_mastery stm ON t.id = stm.topic_id AND stm.student_id = ?
        ORDER BY t.subject_id, t.order_index
    """, (student_id,))
    
    return render_template('student/quiz_start.html',
                           subjects=subjects,
                           topics=topics,
                           pre_sub=pre_sub,
                           pre_topic=pre_topic)

@quiz_bp.route('/initiate', methods=['POST'])
@student_required
def initiate():
    student_id = session.get('student_id')
    subject_id = request.form.get('subject_id')
    topic_id = request.form.get('topic_id')
    
    if not subject_id and topic_id:
        topic = query_db("SELECT subject_id FROM topics WHERE id = ?", (topic_id,), one=True)
        if topic:
            subject_id = topic['subject_id']
            
    if not subject_id:
        flash('Please select a subject to start the quiz.', 'warning')
        return redirect(url_for('quiz.start'))
        
    session_data = AdaptiveQuizEngine.initialize_session(
        student_id=student_id,
        subject_id=subject_id,
        topic_id=topic_id if topic_id else None,
        total_questions=5
    )
    
    first_question = AdaptiveQuizEngine.get_next_question(session_data)
    if not first_question:
        flash('No questions found for the selected subject/topic.', 'danger')
        return redirect(url_for('quiz.start'))
        
    session['active_quiz'] = session_data
    return redirect(url_for('quiz.active'))

@quiz_bp.route('/active')
@student_required
def active():
    quiz_session = session.get('active_quiz')
    if not quiz_session:
        flash('No active quiz in progress. Please start a new quiz.', 'info')
        return redirect(url_for('quiz.start'))
        
    next_question = AdaptiveQuizEngine.get_next_question(quiz_session)
    if not next_question:
        # Fallback if question pool exhausted
        result = AdaptiveQuizEngine.finalize_quiz(quiz_session)
        session.pop('active_quiz', None)
        return redirect(url_for('quiz.result', attempt_id=result['attempt_id']))

    subject = query_db("SELECT name FROM subjects WHERE id = ?", (quiz_session['subject_id'],), one=True)
    topic = query_db("SELECT name FROM topics WHERE id = ?", (quiz_session['topic_id'],), one=True) if quiz_session['topic_id'] else None

    return render_template('student/quiz_active.html',
                           question=next_question,
                           session=quiz_session,
                           subject=subject,
                           topic=topic)

@quiz_bp.route('/submit-answer', methods=['POST'])
@student_required
def submit_answer():
    quiz_session = session.get('active_quiz')
    if not quiz_session:
        return jsonify({'error': 'No active quiz session'}), 400

    data = request.get_json() or {}
    question_id = data.get('question_id')
    student_answer = data.get('student_answer')
    time_taken = data.get('time_taken', 0)

    if not question_id or not student_answer:
        return jsonify({'error': 'Missing question ID or answer'}), 400

    eval_result = AdaptiveQuizEngine.submit_answer(quiz_session, question_id, student_answer, time_taken)
    session['active_quiz'] = quiz_session  # Save updated state to session
    
    return jsonify(eval_result)

@quiz_bp.route('/finish', methods=['POST'])
@student_required
def finish():
    quiz_session = session.get('active_quiz')
    if not quiz_session:
        return jsonify({'error': 'No active quiz session'}), 400

    result = AdaptiveQuizEngine.finalize_quiz(quiz_session)
    session.pop('active_quiz', None)
    return jsonify({'redirect_url': url_for('quiz.result', attempt_id=result['attempt_id'])})

@quiz_bp.route('/result/<int:attempt_id>')
@student_required
def result(attempt_id):
    student_id = session.get('student_id')
    attempt = query_db("""
        SELECT qa.*, sub.name as subject_name, t.name as topic_name
        FROM quiz_attempts qa
        JOIN subjects sub ON qa.subject_id = sub.id
        LEFT JOIN topics t ON qa.topic_id = t.id
        WHERE qa.id = ? AND qa.student_id = ?
    """, (attempt_id, student_id), one=True)

    if not attempt:
        flash('Quiz attempt not found.', 'warning')
        return redirect(url_for('student.dashboard'))

    answers = query_db("""
        SELECT qans.*, q.question_text, q.correct_option, q.explanation,
               q.option_a, q.option_b, q.option_c, q.option_d,
               t.name as topic_name
        FROM quiz_answers qans
        JOIN questions q ON qans.question_id = q.id
        LEFT JOIN topics t ON q.topic_id = t.id
        WHERE qans.attempt_id = ?
        ORDER BY qans.id ASC
    """, (attempt_id,))

    diff_progression = json.loads(attempt['difficulty_progression']) if attempt['difficulty_progression'] else []
    recommendations = generate_recommendations(student_id, subject_id=attempt['subject_id'])

    return render_template('student/quiz_result.html',
                           attempt=attempt,
                           answers=answers,
                           diff_progression=diff_progression,
                           recommendations=recommendations)
