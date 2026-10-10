from flask import Blueprint, request, jsonify, session
from database.db import query_db, get_db
from services.ai_service import ask_ai_tutor, generate_questions_ai

api_bp = Blueprint('api', __name__)

@api_bp.route('/ai/chat', methods=['POST'])
def ai_chat():
    data = request.get_json() or {}
    message = data.get('message', '').strip()
    topic_hint = data.get('topic_hint')
    user_level = data.get('level', 'beginner')
    student_id = session.get('student_id', 1)

    if not message:
        return jsonify({'error': 'Message cannot be empty'}), 400

    reply = ask_ai_tutor(student_id, message, topic_hint=topic_hint, user_level=user_level)

    # Store in chat history
    try:
        with get_db() as conn:
            conn.execute("""
                INSERT INTO ai_chat_history (student_id, role, message, topic, difficulty_level)
                VALUES (?, 'user', ?, ?, ?)
            """, (student_id, message, topic_hint, user_level))
            conn.execute("""
                INSERT INTO ai_chat_history (student_id, role, message, topic, difficulty_level)
                VALUES (?, 'assistant', ?, ?, ?)
            """, (student_id, reply, topic_hint, user_level))
    except Exception as e:
        print(f"Error logging chat: {e}")

    return jsonify({'reply': reply})

@api_bp.route('/ai/generate-questions', methods=['POST'])
def api_generate_questions():
    data = request.get_json() or {}
    subject_id = data.get('subject_id')
    topic_id = data.get('topic_id')
    difficulty = data.get('difficulty', 'medium')
    count = int(data.get('count', 3))

    sub = query_db("SELECT name FROM subjects WHERE id = ?", (subject_id,), one=True) if subject_id else None
    top = query_db("SELECT name FROM topics WHERE id = ?", (topic_id,), one=True) if topic_id else None

    sub_name = sub['name'] if sub else 'Computer Science'
    top_name = top['name'] if top else 'Core Concepts'

    questions = generate_questions_ai(sub_name, top_name, difficulty, num_questions=count)
    return jsonify({'questions': questions})

@api_bp.route('/topics-by-subject/<int:subject_id>')
def topics_by_subject(subject_id):
    topics = query_db("SELECT id, name FROM topics WHERE subject_id = ? ORDER BY order_index ASC", (subject_id,))
    return jsonify(topics)

@api_bp.route('/offline-data')
def offline_data():
    """Provides a light payload of questions, topics, and materials for offline PWA sync."""
    subjects = query_db("SELECT * FROM subjects")
    topics = query_db("SELECT * FROM topics")
    materials = query_db("SELECT * FROM learning_materials LIMIT 20")
    questions = query_db("SELECT id, subject_id, topic_id, question_text, option_a, option_b, option_c, option_d, difficulty FROM questions LIMIT 40")
    
    return jsonify({
        'subjects': subjects,
        'topics': topics,
        'materials': materials,
        'questions': questions
    })
