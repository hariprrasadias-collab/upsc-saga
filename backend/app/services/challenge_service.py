from app.db import get_db
from datetime import datetime, date, timedelta
import random

class ChallengeService:
    """
    Service for managing daily challenges and streak tracking.
    """
    
    def __init__(self):
        pass
    
    def get_daily_challenge(self, user_id):
        """
        Get today's challenge for the user. Assigns one if not already assigned.
        """
        conn = get_db()
        today = date.today().isoformat()
        
        # Check if challenge already assigned for today
        existing = conn.execute('''
            SELECT uc.*, c.title, c.description, c.type, c.target_value, c.xp_reward
            FROM user_challenges uc
            JOIN challenges c ON uc.challenge_id = c.id
            WHERE uc.user_id = ? AND uc.assigned_date = ?
        ''', (user_id, today)).fetchone()
        
        if existing:
            return dict(existing)
        
        # Assign a new random challenge
        all_challenges = conn.execute('SELECT * FROM challenges').fetchall()
        if not all_challenges:
            return None
            
        # Pick a random challenge
        challenge = random.choice(all_challenges)
        
        # Assign it to user
        conn.execute('''
            INSERT INTO user_challenges (user_id, challenge_id, assigned_date, progress)
            VALUES (?, ?, ?, 0)
        ''', (user_id, challenge['id'], today))
        conn.commit()
        
        # Fetch and return the assigned challenge
        assigned = conn.execute('''
            SELECT uc.*, c.title, c.description, c.type, c.target_value, c.xp_reward
            FROM user_challenges uc
            JOIN challenges c ON uc.challenge_id = c.id
            WHERE uc.user_id = ? AND uc.assigned_date = ?
        ''', (user_id, today)).fetchone()
        
        return dict(assigned) if assigned else None
    
    def complete_challenge(self, user_id):
        """
        Mark today's challenge as complete and award XP.
        Also updates streak.
        """
        conn = get_db()
        today = date.today().isoformat()
        
        # Get today's challenge
        challenge = conn.execute('''
            SELECT uc.*, c.xp_reward, c.target_value
            FROM user_challenges uc
            JOIN challenges c ON uc.challenge_id = c.id
            WHERE uc.user_id = ? AND uc.assigned_date = ? AND uc.completed = 0
        ''', (user_id, today)).fetchone()
        
        if not challenge:
            return {'success': False, 'message': 'No active challenge found'}
        
        # Mark as complete
        conn.execute('''
            UPDATE user_challenges
            SET completed = 1, completed_at = CURRENT_TIMESTAMP, progress = ?
            WHERE id = ?
        ''', (challenge['target_value'], challenge['id']))
        
        # Award XP
        xp_reward = challenge['xp_reward']
        conn.execute('''
            UPDATE users
            SET current_xp = current_xp + ?
            WHERE id = ?
        ''', (xp_reward, user_id))
        
        # Update streak
        self._update_streak(user_id, conn)
        
        conn.commit()
        
        return {
            'success': True,
            'xp_awarded': xp_reward,
            'message': 'Challenge completed!'
        }
    
    def get_streak(self, user_id):
        """
        Get current streak information for user.
        """
        conn = get_db()
        
        # Ensure streak record exists
        conn.execute('''
            INSERT OR IGNORE INTO streaks (user_id, current_streak, longest_streak)
            VALUES (?, 0, 0)
        ''', (user_id,))
        conn.commit()
        
        streak = conn.execute('''
            SELECT * FROM streaks WHERE user_id = ?
        ''', (user_id,)).fetchone()
        
        if not streak:
            return None
        
        # Check if streak should be broken
        streak_dict = dict(streak)
        if streak_dict['last_activity_date']:
            last_date = datetime.fromisoformat(streak_dict['last_activity_date']).date()
            today = date.today()
            days_diff = (today - last_date).days
            
            # Break streak if more than 1 day gap
            if days_diff > 1:
                conn.execute('''
                    UPDATE streaks
                    SET current_streak = 0
                    WHERE user_id = ?
                ''', (user_id,))
                conn.commit()
                streak_dict['current_streak'] = 0
        
        return streak_dict
    
    def _update_streak(self, user_id, conn):
        """
        Update user's streak after completing a challenge.
        """
        today = date.today().isoformat()
        
        streak = conn.execute('''
            SELECT * FROM streaks WHERE user_id = ?
        ''', (user_id,)).fetchone()
        
        if not streak:
            # Create new streak
            conn.execute('''
                INSERT INTO streaks (user_id, current_streak, longest_streak, last_activity_date)
                VALUES (?, 1, 1, ?)
            ''', (user_id, today))
            return
        
        last_date_str = streak['last_activity_date']
        
        # If no previous activity, start streak
        if not last_date_str:
            conn.execute('''
                UPDATE streaks
                SET current_streak = 1, longest_streak = 1, last_activity_date = ?
                WHERE user_id = ?
            ''', (today, user_id))
            return
        
        last_date = datetime.fromisoformat(last_date_str).date()
        today_date = date.today()
        days_diff = (today_date - last_date).days
        
        # Same day - don't update
        if days_diff == 0:
            return
        
        # Next day - increment streak
        if days_diff == 1:
            new_streak = streak['current_streak'] + 1
            new_longest = max(new_streak, streak['longest_streak'])
            
            conn.execute('''
                UPDATE streaks
                SET current_streak = ?, longest_streak = ?, last_activity_date = ?
                WHERE user_id = ?
            ''', (new_streak, new_longest, today, user_id))
        
        # Streak broken - reset
        else:
            conn.execute('''
                UPDATE streaks
                SET current_streak = 1, last_activity_date = ?
                WHERE user_id = ?
            ''', (today, user_id))
    
    def get_challenge_history(self, user_id, days=30):
        """
        Get user's challenge completion history.
        """
        conn = get_db()
        
        history = conn.execute('''
            SELECT uc.*, c.title, c.description, c.xp_reward
            FROM user_challenges uc
            JOIN challenges c ON uc.challenge_id = c.id
            WHERE uc.user_id = ?
            ORDER BY uc.assigned_date DESC
            LIMIT ?
        ''', (user_id, days)).fetchall()
        
        return [dict(row) for row in history]
    
    def update_challenge_progress(self, user_id, progress_value):
        """
        Update progress for today's challenge.
        Auto-complete if target reached.
        """
        conn = get_db()
        today = date.today().isoformat()
        
        challenge = conn.execute('''
            SELECT uc.*, c.target_value, c.xp_reward
            FROM user_challenges uc
            JOIN challenges c ON uc.challenge_id = c.id
            WHERE uc.user_id = ? AND uc.assigned_date = ? AND uc.completed = 0
        ''', (user_id, today)).fetchone()
        
        if not challenge:
            return False
        
        # Update progress
        conn.execute('''
            UPDATE user_challenges
            SET progress = ?
            WHERE id = ?
        ''', (progress_value, challenge['id']))
        
        # Auto-complete if target reached
        if progress_value >= challenge['target_value']:
            conn.execute('''
                UPDATE user_challenges
                SET completed = 1, completed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (challenge['id'],))
            
            # Award XP
            conn.execute('''
                UPDATE users
                SET current_xp = current_xp + ?
                WHERE id = ?
            ''', (challenge['xp_reward'], user_id))
            
            # Update streak
            self._update_streak(user_id, conn)
        
        conn.commit()
        return True

challenge_service = ChallengeService()
