import json
from database.db import get_db, query_db
from services.performance_service import update_topic_mastery_after_quiz, get_performance_band

class AdaptiveQuizEngine:
    """Manages the state and dynamic question selection for an adaptive quiz session."""

    @staticmethod
    def initialize_session(student_id, subject_id, topic_id=None, total_questions=5):
        """Creates a new in-progress quiz session dictionary."""
        return {
            'student_id': student_id,
            'subject_id': int(subject_id),
            'topic_id': int(topic_id) if topic_id else None,
            'total_questions': total_questions,
            'current_index': 0,
            'current_difficulty': 'easy',
            'consecutive_correct': 0,
            'consecutive_incorrect': 0,
            'history': [], # list of answered question records
            'asked_question_ids': [],
            'score': 0
        }

    @staticmethod
    def get_next_question(session):
        """Fetches the next question matching the target difficulty that hasn't been asked yet."""
        subject_id = session['subject_id']
        topic_id = session['topic_id']
        target_diff = session['current_difficulty']
        asked_ids = session['asked_question_ids']

        placeholders = ','.join('?' for _ in asked_ids) if asked_ids else '0'
        
        # Build query for target difficulty
        query = f"""
            SELECT * FROM questions
            WHERE subject_id = ?
            {"AND topic_id = ?" if topic_id else ""}
            AND difficulty = ?
            AND id NOT IN ({placeholders})
            ORDER BY RANDOM()
            LIMIT 1
        """
        args = [subject_id]
        if topic_id:
            args.append(topic_id)
        args.append(target_diff)
        if asked_ids:
            args.extend(asked_ids)

        question = query_db(query, tuple(args), one=True)

        # Fallback: if no question at this specific difficulty, get any unasked question
        if not question:
            fallback_query = f"""
                SELECT * FROM questions
                WHERE subject_id = ?
                {"AND topic_id = ?" if topic_id else ""}
                AND id NOT IN ({placeholders})
                ORDER BY RANDOM()
                LIMIT 1
            """
            f_args = [subject_id]
            if topic_id:
                f_args.append(topic_id)
            if asked_ids:
                f_args.extend(asked_ids)
            question = query_db(fallback_query, tuple(f_args), one=True)

        if question:
            # Mask the correct answer when sending to client
            return {
                'id': question['id'],
                'question_text': question['question_text'],
                'option_a': question['option_a'],
                'option_b': question['option_b'],
                'option_c': question['option_c'],
                'option_d': question['option_d'],
                'difficulty': question['difficulty'],
                'subject_id': question['subject_id'],
                'topic_id': question['topic_id'],
                'question_num': session['current_index'] + 1,
                'total_questions': session['total_questions']
            }
        return None

    @staticmethod
    def submit_answer(session, question_id, student_answer, time_taken=0):
        """
        Processes student's answer, computes instant feedback, adjusts difficulty for next question,
        and updates mastery data.
        """
        q = query_db("SELECT * FROM questions WHERE id = ?", (question_id,), one=True)
        if not q:
            return {'error': 'Question not found'}

        is_correct = (student_answer.strip().upper() == q['correct_option'].strip().upper())
        prev_diff = session['current_difficulty']

        # Update difficulty adaptation logic
        if is_correct:
            session['score'] += 1
            session['consecutive_correct'] += 1
            session['consecutive_incorrect'] = 0

            # Advance difficulty on 2 consecutive correct or 1 correct in easy
            if prev_diff == 'easy' and session['consecutive_correct'] >= 1:
                session['current_difficulty'] = 'medium'
                session['consecutive_correct'] = 0
            elif prev_diff == 'medium' and session['consecutive_correct'] >= 2:
                session['current_difficulty'] = 'hard'
                session['consecutive_correct'] = 0
        else:
            session['consecutive_incorrect'] += 1
            session['consecutive_correct'] = 0

            # Demote difficulty on 2 consecutive incorrect or 1 incorrect in hard
            if prev_diff == 'hard' and session['consecutive_incorrect'] >= 1:
                session['current_difficulty'] = 'medium'
                session['consecutive_incorrect'] = 0
            elif prev_diff == 'medium' and session['consecutive_incorrect'] >= 2:
                session['current_difficulty'] = 'easy'
                session['consecutive_incorrect'] = 0

        # Record answer history
        answer_record = {
            'question_id': q['id'],
            'topic_id': q['topic_id'],
            'question_text': q['question_text'],
            'student_answer': student_answer,
            'correct_option': q['correct_option'],
            'is_correct': 1 if is_correct else 0,
            'difficulty_at_time': prev_diff,
            'next_difficulty': session['current_difficulty'],
            'explanation': q['explanation'],
            'time_taken_seconds': time_taken
        }

        session['history'].append(answer_record)
        session['asked_question_ids'].append(q['id'])
        session['current_index'] += 1

        # Real-time update of student topic mastery
        update_topic_mastery_after_quiz(session['student_id'], q['topic_id'], is_correct)

        is_finished = (session['current_index'] >= session['total_questions'])

        return {
            'is_correct': is_correct,
            'correct_option': q['correct_option'],
            'explanation': q['explanation'],
            'difficulty_used': prev_diff,
            'next_difficulty': session['current_difficulty'],
            'is_finished': is_finished,
            'current_score': session['score'],
            'current_index': session['current_index'],
            'total_questions': session['total_questions']
        }

    @staticmethod
    def finalize_quiz(session):
        """Persists the quiz attempt and answers into the database and generates scorecard."""
        student_id = session['student_id']
        subject_id = session['subject_id']
        topic_id = session['topic_id']
        total = session['total_questions']
        score = session['score']
        percentage = round((score / total) * 100.0, 1) if total > 0 else 0.0
        band_name, _, _ = get_performance_band(percentage)
        
        diff_progression = [h['difficulty_at_time'] for h in session['history']]

        with get_db() as conn:
            cur = conn.execute("""
                INSERT INTO quiz_attempts (student_id, subject_id, topic_id, total_questions, score, percentage, performance_band, difficulty_progression, completed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (student_id, subject_id, topic_id, total, score, percentage, band_name, json.dumps(diff_progression)))
            attempt_id = cur.lastrowid

            for ans in session['history']:
                conn.execute("""
                    INSERT INTO quiz_answers (attempt_id, question_id, student_answer, is_correct, difficulty_at_time, time_taken_seconds)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (attempt_id, ans['question_id'], ans['student_answer'], ans['is_correct'], ans['difficulty_at_time'], ans.get('time_taken_seconds', 0)))

        return {
            'attempt_id': attempt_id,
            'score': score,
            'total_questions': total,
            'percentage': percentage,
            'performance_band': band_name,
            'difficulty_progression': diff_progression,
            'history': session['history']
        }
