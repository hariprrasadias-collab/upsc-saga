from app.db import get_db
from datetime import datetime

class BadgeService:
    """
    Service for managing achievement badges and tracking progress.
    """
    
    def __init__(self):
        pass
    
    def get_all_badges(self, user_id):
        """
        Get all badges with unlock status for a specific user.
        Returns list of badges with 'unlocked' and 'progress' info.
        """
        conn = get_db()
        
        # Get all badges
        badges = conn.execute('''
            SELECT b.*, 
                   ub.unlocked_at,
                   bp.current_value,
                   bp.target_value
            FROM badges b
            LEFT JOIN user_badges ub ON b.id = ub.badge_id AND ub.user_id = ?
            LEFT JOIN badge_progress bp ON b.id = bp.badge_id AND bp.user_id = ?
            ORDER BY b.category, b.rarity, b.id
        ''', (user_id, user_id)).fetchall()
        
        result = []
        for badge in badges:
            badge_dict = dict(badge)
            badge_dict['unlocked'] = badge_dict['unlocked_at'] is not None
            
            # Calculate progress percentage
            if badge_dict['current_value'] and badge_dict['target_value']:
                badge_dict['progress'] = min(100, int((badge_dict['current_value'] / badge_dict['target_value']) * 100))
            else:
                badge_dict['progress'] = 0
                
            result.append(badge_dict)
        
        return result
    
    def get_user_badges(self, user_id):
        """
        Get only unlocked badges for a user.
        """
        conn = get_db()
        
        badges = conn.execute('''
            SELECT b.*, ub.unlocked_at
            FROM badges b
            JOIN user_badges ub ON b.id = ub.badge_id
            WHERE ub.user_id = ?
            ORDER BY ub.unlocked_at DESC
        ''', (user_id,)).fetchall()
        
        return [dict(row) for row in badges]
    
    def check_and_unlock_badges(self, user_id):
        """
        Check all badge criteria and unlock any newly achieved badges.
        Returns list of newly unlocked badge IDs.
        """
        conn = get_db()
        newly_unlocked = []
        
        # Get user stats
        user_stats = self._get_user_stats(user_id)
        
        # Get all badges that aren't unlocked yet
        locked_badges = conn.execute('''
            SELECT b.* FROM badges b
            WHERE b.id NOT IN (
                SELECT badge_id FROM user_badges WHERE user_id = ?
            )
        ''', (user_id,)).fetchall()
        
        for badge in locked_badges:
            criteria = badge['unlock_criteria']
            
            if self._check_criteria(criteria, user_stats):
                # Unlock the badge
                conn.execute('''
                    INSERT INTO user_badges (user_id, badge_id)
                    VALUES (?, ?)
                ''', (user_id, badge['id']))
                
                # Award XP
                if badge['xp_reward'] > 0:
                    self._award_xp(user_id, badge['xp_reward'])
                
                newly_unlocked.append(badge['id'])
        
        if newly_unlocked:
            conn.commit()
        
        return newly_unlocked
    
    def update_badge_progress(self, user_id, badge_id, current_value, target_value):
        """
        Update progress for a specific badge.
        """
        conn = get_db()
        
        conn.execute('''
            INSERT INTO badge_progress (user_id, badge_id, current_value, target_value, last_updated)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id, badge_id) DO UPDATE SET
                current_value = ?,
                last_updated = CURRENT_TIMESTAMP
        ''', (user_id, badge_id, current_value, target_value, current_value))
        
        conn.commit()
    
    def _get_user_stats(self, user_id):
        """
        Gather all user statistics needed for badge checking.
        Returns dict with various stats.
        """
        conn = get_db()
        
        stats = {}
        
        # Get user level and XP
        user = conn.execute('SELECT level, current_xp FROM users WHERE id = ?', (user_id,)).fetchone()
        if user:
            stats['level'] = user['level']
            stats['total_xp'] = user['current_xp']  # This should ideally be cumulative XP
        
        # Count completed tasks
        stats['tasks_completed'] = conn.execute(
            'SELECT COUNT(*) as count FROM tasks WHERE user_id = ? AND isCompleted = 1',
            (user_id,)
        ).fetchone()['count']
        
        # Count answers written
        stats['answers_written'] = conn.execute(
            'SELECT COUNT(*) as count FROM answer_submissions WHERE user_id = ?',
            (user_id,)
        ).fetchone()['count']
        
        # Count essays written
        stats['essays_written'] = conn.execute(
            'SELECT COUNT(*) as count FROM essay_submissions WHERE user_id = ?',
            (user_id,)
        ).fetchone()['count']
        
        # Count mock tests taken
        stats['mock_tests'] = conn.execute(
            'SELECT COUNT(DISTINCT test_id) as count FROM test_results WHERE user_id = ?',
            (user_id,)
        ).fetchone()['count']
        
        # Count flashcards reviewed
        stats['flashcards_reviewed'] = conn.execute(
            'SELECT COUNT(*) as count FROM review_sessions WHERE user_id = ?',
            (user_id,)
        ).fetchone()['count']
        
        # Check for perfect mock test score
        perfect_test = conn.execute('''
            SELECT COUNT(*) as count FROM test_results 
            WHERE user_id = ? AND score = 100
        ''', (user_id,)).fetchone()['count']
        stats['mock_test_perfect'] = perfect_test
        
        # Count CSAT questions (if table exists)
        try:
            stats['csat_quant'] = conn.execute(
                'SELECT COUNT(*) as count FROM user_question_attempts WHERE user_id = ? AND topic LIKE "%Quant%"',
                (user_id,)
            ).fetchone()['count']
        except:
            stats['csat_quant'] = 0
        
        # TODO: Add streak_days, correct_answers, subject_complete, etc.
        stats['streak_days'] = 0  # Will implement with challenges feature
        stats['correct_answers'] = 0
        
        return stats
    
    def _check_criteria(self, criteria_str, user_stats):
        """
        Check if user meets the criteria for a badge.
        Criteria format: "stat_name:target_value"
        Example: "tasks_completed:100"
        """
        try:
            stat_name, target_str = criteria_str.split(':')
            target_value = int(target_str)
            
            current_value = user_stats.get(stat_name, 0)
            return current_value >= target_value
        except:
            return False
    
    def _award_xp(self, user_id, xp_amount):
        """
        Award XP to user (reuse existing XP system).
        """
        conn = get_db()
        
        # Add XP to user
        conn.execute('''
            UPDATE users 
            SET current_xp = current_xp + ?
            WHERE id = ?
        ''', (xp_amount, user_id))
        
        # Check for level up
        user = conn.execute('SELECT current_xp, max_xp, level FROM users WHERE id = ?', (user_id,)).fetchone()
        
        if user and user['current_xp'] >= user['max_xp']:
            new_level = user['level'] + 1
            new_max_xp = user['max_xp'] + 100  # Simple progression
            
            conn.execute('''
                UPDATE users
                SET level = ?, current_xp = 0, max_xp = ?
                WHERE id = ?
            ''', (new_level, new_max_xp, user_id))
        
        conn.commit()

badge_service = BadgeService()
