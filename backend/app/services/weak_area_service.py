# Weak Area Analyzer Service
from app.db import get_db
from datetime import datetime, timedelta
import json

class WeakAreaAnalyzer:
    
    @staticmethod
    def analyze_user_performance(user_id, days=30):
        """
        Analyze user's performance over the last N days to identify weak areas.
        Returns topics sorted by priority (weakest first).
        """
        conn = get_db()
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Get weak areas ordered by priority
        weak_areas = conn.execute('''
            SELECT 
                topic,
                subject,
                total_attempts,
                correct_attempts,
                accuracy_rate,
                trend,
                priority_score,
                last_attempt_date
            FROM weak_area_analysis
            WHERE user_id = ? AND updated_at >= ?
            ORDER BY priority_score DESC
            LIMIT 10
        ''', (user_id, cutoff_date)).fetchall()
        
        return [dict(row) for row in weak_areas]

    @staticmethod
    def analyze_strong_areas(user_id, days=30):
        """
        Analyze user's strong areas (high accuracy).
        """
        conn = get_db()
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        strong_areas = conn.execute('''
            SELECT 
                topic,
                subject,
                total_attempts,
                correct_attempts,
                accuracy_rate,
                trend,
                priority_score,
                last_attempt_date
            FROM weak_area_analysis
            WHERE user_id = ? AND updated_at >= ?
            ORDER BY accuracy_rate DESC
            LIMIT 5
        ''', (user_id, cutoff_date)).fetchall()
        
        return [dict(row) for row in strong_areas]
    
    @staticmethod
    def update_topic_performance(user_id, subject, topic, is_correct):
        """
        Update performance metrics for a specific topic after a question attempt.
        """
        conn = get_db()
        
        # Get current stats
        current = conn.execute('''
            SELECT * FROM weak_area_analysis
            WHERE user_id = ? AND topic = ? AND subject = ?
        ''', (user_id, topic, subject)).fetchone()
        
        if current:
            # Update existing record
            new_total = current['total_attempts'] + 1
            new_correct = current['correct_attempts'] + (1 if is_correct else 0)
            new_accuracy = (new_correct / new_total * 100) if new_total > 0 else 0
            
            # Calculate trend
            old_accuracy = current['accuracy_rate']
            trend = 'improving' if new_accuracy > old_accuracy else \
                   'declining' if new_accuracy < old_accuracy else 'stable'
            
            # Calculate priority (inverse of accuracy, weighted by attempts)
            priority = (100 - new_accuracy) * (new_total / 10)
            
            conn.execute('''
                UPDATE weak_area_analysis
                SET total_attempts = ?,
                    correct_attempts = ?,
                    accuracy_rate = ?,
                    trend = ?,
                    priority_score = ?,
                    last_attempt_date = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ? AND topic = ? AND subject = ?
            ''', (new_total, new_correct, new_accuracy, trend, priority,
                  datetime.now().isoformat(), user_id, topic, subject))
        else:
            # Create new record
            accuracy = 100.0 if is_correct else 0.0
            priority = (100 - accuracy) * 0.1
            
            conn.execute('''
                INSERT INTO weak_area_analysis
                (user_id, topic, subject, total_attempts, correct_attempts, 
                 accuracy_rate, priority_score, trend, last_attempt_date)
                VALUES (?, ?, ?, 1, ?, ?, ?, 'stable', ?)
            ''', (user_id, topic, subject, 1 if is_correct else 0, 
                  accuracy, priority, datetime.now().isoformat()))
        
        conn.commit()
    
    @staticmethod
    def generate_practice_set(user_id, num_questions=10):
        """
        Generate a targeted practice set focusing on user's weak areas.
        """
        conn = get_db()
        
        # Get top 3 weak topics
        weak_topics = conn.execute('''
            SELECT topic, subject FROM weak_area_analysis
            WHERE user_id = ?
            ORDER BY priority_score DESC
            LIMIT 3
        ''', (user_id,)).fetchall()
        
        if not weak_topics:
            # Fallback: Generate random practice set from all topics
            questions = conn.execute(f'''
                SELECT id, question_text, subject, topic
                FROM questions_master
                ORDER BY RANDOM()
                LIMIT ?
            ''', (num_questions,)).fetchall()
            
            if not questions:
                return None
                
            question_ids = [str(q['id']) for q in questions]
            focus_topics = "General Practice (Random)"
            
            cursor = conn.execute('''
                INSERT INTO targeted_practice_sets
                (user_id, set_name, focus_topics, question_ids, total_questions)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, "General Practice Set", 
                  focus_topics, json.dumps(question_ids), len(questions)))
            
            conn.commit()
            
            return {
                'practice_set_id': cursor.lastrowid,
                'set_name': "General Practice Set",
                'focus_topics': focus_topics,
                'questions': [dict(q) for q in questions],
                'total_questions': len(questions)
            }

        # Get questions from these topics
        topic_list = [wt['topic'] for wt in weak_topics]
        placeholders = ','.join('?' * len(topic_list))
        
        questions = conn.execute(f'''
            SELECT id, question_text, subject, topic
            FROM questions_master
            WHERE topic IN ({placeholders})
            ORDER BY RANDOM()
            LIMIT ?
        ''', (*topic_list, num_questions)).fetchall()
        
        if not questions:
            return None
        
        # Create practice set
        question_ids = [str(q['id']) for q in questions]
        focus_topics = ', '.join(set([q['topic'] for q in questions]))
        
        cursor = conn.execute('''
            INSERT INTO targeted_practice_sets
            (user_id, set_name, focus_topics, question_ids, total_questions)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, f"Focus: {focus_topics[:50]}...", 
              focus_topics, json.dumps(question_ids), len(questions)))
        
        conn.commit()
        
        return {
            'practice_set_id': cursor.lastrowid,
            'set_name': f"Focus: {focus_topics[:50]}...",
            'focus_topics': focus_topics,
            'questions': [dict(q) for q in questions],
            'total_questions': len(questions)
        }
    
    @staticmethod
    def submit_practice_result(practice_set_id, question_id, is_correct, time_taken):
        """
        Record a practice set question result.
        """
        conn = get_db()
        
        # Record the result
        conn.execute('''
            INSERT INTO practice_set_results
            (practice_set_id, question_id, is_correct, time_taken)
            VALUES (?, ?, ?, ?)
        ''', (practice_set_id, question_id, 1 if is_correct else 0, time_taken))
        
        # Update practice set completion
        conn.execute('''
            UPDATE targeted_practice_sets
            SET completed = completed + 1
            WHERE id = ?
        ''', (practice_set_id,))
        
        # Get question details to update weak area analysis
        question = conn.execute('''
            SELECT subject, topic FROM questions_master WHERE id = ?
        ''', (question_id,)).fetchone()
        
        # Get user_id from practice set
        practice_set = conn.execute('''
            SELECT user_id FROM targeted_practice_sets WHERE id = ?
        ''', (practice_set_id,)).fetchone()
        
        if question and practice_set:
            WeakAreaAnalyzer.update_topic_performance(
                practice_set['user_id'],
                question['subject'],
                question['topic'],
                is_correct
            )
        
        conn.commit()
    
    @staticmethod
    def get_practice_sets(user_id, completed=None):
        """
        Get user's practice sets, optionally filtered by completion status.
        """
        conn = get_db()
        
        if completed is None:
            sets = conn.execute('''
                SELECT * FROM targeted_practice_sets
                WHERE user_id = ?
                ORDER BY created_at DESC
            ''', (user_id,)).fetchall()
        else:
            sets = conn.execute('''
                SELECT * FROM targeted_practice_sets
                WHERE user_id = ? AND 
                      (CASE WHEN completed >= total_questions THEN 1 ELSE 0 END) = ?
                ORDER BY created_at DESC
            ''', (user_id, 1 if completed else 0)).fetchall()
        
        return [dict(s) for s in sets]

weak_area_analyzer = WeakAreaAnalyzer()
