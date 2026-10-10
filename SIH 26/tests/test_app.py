import unittest
import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from database.db import get_db, query_db
from database.seed import seed_database
from services.performance_service import calculate_student_performance, get_performance_band
from services.adaptive_quiz_service import AdaptiveQuizEngine
from services.recommendation_service import generate_recommendations
from services.ai_service import ask_ai_tutor, generate_questions_ai

class SmartEducationTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        seed_database()
        cls.client = app.test_client()
        app.config['TESTING'] = True

    def setUp(self):
        # Fetch dynamic IDs
        student = query_db("SELECT id FROM students WHERE student_code='STU202601'", one=True)
        self.student_id = student['id']
        subject = query_db("SELECT id FROM subjects WHERE code='CS101'", one=True)
        self.subject_id = subject['id']

    def test_performance_band_classification(self):
        """Test grade & performance classification bands."""
        self.assertEqual(get_performance_band(95.0)[0], 'Excellent')
        self.assertEqual(get_performance_band(82.0)[0], 'Good')
        self.assertEqual(get_performance_band(65.0)[0], 'Average')
        self.assertEqual(get_performance_band(45.0)[0], 'Needs Improvement')
        self.assertEqual(get_performance_band(30.0)[0], 'Very Weak')

    def test_student_performance_analytics(self):
        """Verify performance calculations for student1."""
        perf = calculate_student_performance(self.student_id)
        self.assertIsNotNone(perf)
        self.assertEqual(perf['student']['username'], 'student1')
        self.assertGreater(len(perf['subject_marks']), 0)
        self.assertGreater(len(perf['topic_masteries']), 0)
        
        # Verify weak topics are identified
        weak_topic_names = [t['topic_name'] for t in perf['weak_topics']]
        self.assertTrue('Pointers' in weak_topic_names or 'Recursion' in weak_topic_names)

    def test_adaptive_quiz_engine_flow(self):
        """Verify dynamic difficulty adjustment logic."""
        session = AdaptiveQuizEngine.initialize_session(student_id=self.student_id, subject_id=self.subject_id, total_questions=3)
        self.assertEqual(session['current_difficulty'], 'easy')

        # Get first question
        q1 = AdaptiveQuizEngine.get_next_question(session)
        self.assertIsNotNone(q1)

        # Answer correctly in easy -> should advance to medium
        q_row = query_db("SELECT correct_option FROM questions WHERE id = ?", (q1['id'],), one=True)
        res = AdaptiveQuizEngine.submit_answer(session, q1['id'], q_row['correct_option'])
        self.assertTrue(res['is_correct'])
        self.assertEqual(session['current_difficulty'], 'medium')

        # Get next question and answer incorrectly -> should downgrade or stay balanced
        q2 = AdaptiveQuizEngine.get_next_question(session)
        self.assertIsNotNone(q2)
        q2_row = query_db("SELECT correct_option FROM questions WHERE id = ?", (q2['id'],), one=True)
        wrong_opt = 'B' if q2_row['correct_option'] == 'A' else 'A'
        res2 = AdaptiveQuizEngine.submit_answer(session, q2['id'], wrong_opt)
        self.assertFalse(res2['is_correct'])


    def test_personalized_recommendations(self):
        """Verify personalized learning resources are generated for student's weak areas."""
        recs = generate_recommendations(self.student_id)
        self.assertGreater(len(recs), 0)
        rec_names = [r['topic_name'] for r in recs]
        self.assertTrue('Pointers' in rec_names or 'Recursion' in rec_names)

    def test_ai_tutor_fallback_knowledge(self):
        """Verify AI Tutor works reliably even without external API keys."""
        resp_beginner = ask_ai_tutor(self.student_id, "I don't understand pointers in C", user_level='beginner')
        self.assertIn("Pointers", resp_beginner)

        resp_recursion = ask_ai_tutor(self.student_id, "Explain recursion simply", user_level='beginner')
        self.assertIn("Recursion", resp_recursion)

    def test_ai_question_generation(self):
        """Verify AI question generator creates structured multiple-choice questions."""
        questions = generate_questions_ai("C Programming", "Pointers", "medium", num_questions=2)
        self.assertEqual(len(questions), 2)
        self.assertIn("question_text", questions[0])
        self.assertIn("correct_option", questions[0])
        self.assertIn(questions[0]['correct_option'], ['A', 'B', 'C', 'D'])

    def test_auth_login_endpoints(self):
        """Verify HTTP login redirects and session management."""
        client = app.test_client()
        # 1. Test student login
        resp = client.post('/login', data={'username': 'student1', 'password': 'student123'}, follow_redirects=False)
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/student/dashboard', resp.headers['Location'])

        # 2. Test teacher login with fresh client
        teacher_client = app.test_client()
        resp2 = teacher_client.post('/login', data={'username': 'teacher1', 'password': 'teacher123'}, follow_redirects=False)
        self.assertEqual(resp2.status_code, 302)
        self.assertIn('/teacher/dashboard', resp2.headers['Location'])

if __name__ == '__main__':
    unittest.main()
