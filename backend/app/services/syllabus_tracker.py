from app.db import get_db
from datetime import datetime

class SyllabusTracker:
    """
    Service to track and update syllabus progress.
    """
    
    @staticmethod
    def update_topic_progress(topic, status):
        """
        Update the status of a syllabus topic.
        Status: 'Not Started', 'In Progress', 'Completed', 'Mastered'
        """
        conn = get_db()
        
        # Find the topic (fuzzy match or exact?)
        # For now, let's try exact match first, then LIKE
        
        # Check if topic exists exactly
        existing = conn.execute('SELECT * FROM syllabus_topics WHERE topic = ?', (topic,)).fetchone()
        
        if not existing:
            # Try LIKE match
            existing = conn.execute('SELECT * FROM syllabus_topics WHERE topic LIKE ?', (f'%{topic}%',)).fetchone()
            
        if existing:
            conn.execute('''
                UPDATE syllabus_topics 
                SET status = ?, last_updated = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (status, existing['id']))
            conn.commit()
            return {'success': True, 'topic': existing['topic'], 'new_status': status}
            
        return {'success': False, 'message': 'Topic not found'}

    @staticmethod
    def get_progress_summary():
        """
        Get overall syllabus progress.
        """
        conn = get_db()
        
        total = conn.execute('SELECT COUNT(*) as count FROM syllabus_topics').fetchone()['count']
        completed = conn.execute("SELECT COUNT(*) as count FROM syllabus_topics WHERE status IN ('Completed', 'Mastered')").fetchone()['count']
        in_progress = conn.execute("SELECT COUNT(*) as count FROM syllabus_topics WHERE status = 'In Progress'").fetchone()['count']
        
        return {
            'total_topics': total,
            'completed': completed,
            'in_progress': in_progress,
            'completion_rate': (completed / total * 100) if total > 0 else 0
        }

    @staticmethod
    def auto_update_from_action(action_type, payload):
        """
        Automatically update syllabus based on an action.
        """
        if action_type == 'COMPLETE_MOCK_TEST':
            # Payload might have 'topics' list
            topics = payload.get('topics', [])
            results = []
            for topic in topics:
                # If score is high, mark as Mastered?
                # For now, just mark as Completed
                res = SyllabusTracker.update_topic_progress(topic, 'Completed')
                results.append(res)
            return results
            
        elif action_type == 'READ_ARTICLE':
            topic = payload.get('topic')
            if topic:
                return SyllabusTracker.update_topic_progress(topic, 'In Progress')
                
        return []
