from database.db import query_db
from services.performance_service import calculate_student_performance

def generate_recommendations(student_id, subject_id=None):
    """
    Generates personalized recommendations based on student weaknesses and learning pace.
    - If a topic has mastery < 40% (Very Weak) -> recommends Beginner Notes & Foundational Videos.
    - If 40% <= mastery < 60% (Needs Improvement) -> recommends Step-by-Step Examples & Adaptive Quiz.
    - If mastery >= 75% (Strong) -> recommends Advanced Challenge Exercises & Projects.
    """
    perf = calculate_student_performance(student_id)
    if not perf:
        return []

    recommendations = []
    
    # Filter weak topics (optionally for a specific subject)
    target_topics = perf['weak_topics'] + perf['average_topics']
    if subject_id:
        target_topics = [t for t in target_topics if t['subject_id'] == int(subject_id)]
    
    # If student is doing well in everything, suggest advanced topics
    if not target_topics and perf['strong_topics']:
        target_topics = perf['strong_topics'][:2]

    for topic in target_topics:
        pct = topic['mastery_percentage']
        tid = topic['topic_id']
        sub_name = topic['subject_name']
        t_name = topic['topic_name']
        
        # Determine appropriate difficulty filter
        if pct < 40.0:
            rec_difficulty = 'beginner'
            action_text = f"Review foundational concepts in {t_name} (Current: {pct}%)"
            priority = 'High Priority'
            badge_color = 'danger'
        elif pct < 60.0:
            rec_difficulty = 'intermediate'
            action_text = f"Practice structured examples & exercises for {t_name} (Current: {pct}%)"
            priority = 'Medium Priority'
            badge_color = 'warning'
        else:
            rec_difficulty = 'advanced'
            action_text = f"Explore advanced challenges and edge cases in {t_name}"
            priority = 'Good Mastery'
            badge_color = 'success'

        # Fetch relevant learning materials
        materials = query_db("""
            SELECT lm.*, t.name as topic_name, sub.name as subject_name
            FROM learning_materials lm
            JOIN topics t ON lm.topic_id = t.id
            JOIN subjects sub ON lm.subject_id = sub.id
            WHERE lm.topic_id = ?
            ORDER BY CASE WHEN lm.difficulty = ? THEN 1 ELSE 2 END
            LIMIT 2
        """, (tid, rec_difficulty))

        recommendations.append({
            'topic_id': tid,
            'topic_name': t_name,
            'subject_name': sub_name,
            'mastery_percentage': pct,
            'status_band': topic['status_band'],
            'action_text': action_text,
            'priority': priority,
            'badge_color': badge_color,
            'materials': materials,
            'suggested_quiz_url': f"/quiz/start?topic_id={tid}"
        })

    return recommendations
