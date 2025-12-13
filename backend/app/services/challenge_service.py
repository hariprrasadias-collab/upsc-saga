from app.db import get_db
from datetime import datetime, date, timedelta
import random
import traceback
from app.services.game_engine import calculate_and_apply_rewards

class ChallengeService:
    """
    Service for managing daily challenges and streak tracking.
    """
    
    def __init__(self):
        pass
    
    def get_daily_challenge(self, user_id):
        """
        Get today's challenge for the user. Assigns one if not already assigned.
        PHASE 9: AI GENERATED RAIDS
        """
        try:
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

            # PHASE 9: GENERATE DYNAMIC BOSS RAID
            from app.services.model_manager import model_manager

            if model_manager.is_configured:
                try:
                    # Generate a unique challenge based on recent context
                    prompt = """
                    # MISSION: GENERATE DAILY UPSC CHALLENGE (BOSS RAID)
                    **Directive:** Create a gamified 1-day challenge.

                    **Examples:**
                    - "The Inflation Dragon": Answer 50 MCQs on Economy.
                    - "The Polity Siege": Read 3 Chapters of Laxmikanth.

                    **OUTPUT SCHEMA (JSON):**
                    {
                        "title": "Creative Boss Name",
                        "description": "Lore description of the challenge.",
                        "type": "quiz_count" or "study_hours",
                        "target_value": 50 or 4 (hours),
                        "xp_reward": 200
                    }
                    """
                    response = model_manager.generate_content(prompt, model_type='fast')
                    import json
                    raid_data = json.loads(response.text.strip().replace('```json', '').replace('```', ''))

                    # Save new challenge to DB
                    cursor = conn.execute('''
                        INSERT INTO challenges (title, description, type, target_value, xp_reward)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (raid_data['title'], raid_data['description'], raid_data['type'], raid_data['target_value'], raid_data['xp_reward']))
                    challenge_id = cursor.lastrowid

                    # Assign
                    conn.execute('''
                        INSERT INTO user_challenges (user_id, challenge_id, assigned_date, progress)
                        VALUES (?, ?, ?, 0)
                    ''', (user_id, challenge_id, today))
                    conn.commit()

                    # Fetch and return
                    assigned = conn.execute('''
                        SELECT uc.*, c.title, c.description, c.type, c.target_value, c.xp_reward
                        FROM user_challenges uc
                        JOIN challenges c ON uc.challenge_id = c.id
                        WHERE uc.id = ?
                    ''', (cursor.lastrowid,)).fetchone()
                    return dict(assigned)

                except Exception as e:
                    print(f"AI Raid Generation Failed: {e}")
                    # Fallback to standard logic below

            # Assign a new random challenge (Fallback)
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
        except Exception as e:
            print(f"Daily Challenge Error: {e}")
            return None
    
    def complete_challenge(self, user_id):
        """
        Mark today's challenge as complete and award XP.
        Also updates streak.
        """
        conn = get_db()
        try:
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
            calculate_and_apply_rewards(user_id, xp_reward, 0, ['challenge', 'daily'])

            # Update streak
            self._update_streak(user_id, conn)

            conn.commit()

            return {
                'success': True,
                'xp_awarded': xp_reward,
                'message': 'Challenge completed!'
            }
        except Exception as e:
            conn.rollback()
            print(f"Complete Challenge Error: {e}")
            return {'success': False, 'message': 'Error completing challenge'}
    
    def get_streak(self, user_id):
        """
        Get current streak information for user.
        """
        conn = get_db()
        try:
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
                try:
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
                except ValueError:
                    pass # Ignore date parse errors

            return streak_dict
        except Exception as e:
            print(f"Get Streak Error: {e}")
            return None
    
    def _update_streak(self, user_id, conn):
        """
        Update user's streak after completing a challenge.
        """
        try:
            today = date.today().isoformat()
            
            streak = conn.execute('''
                SELECT * FROM streaks WHERE user_id = ?
            ''', (user_id,)).fetchone()

            if not streak:
                conn.execute('''
                    INSERT INTO streaks (user_id, current_streak, longest_streak, last_activity_date)
                    VALUES (?, 1, 1, ?)
                ''', (user_id, today))
                return

            last_date_str = streak['last_activity_date']

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

            if days_diff == 0:
                return

            if days_diff == 1:
                new_streak = streak['current_streak'] + 1
                new_longest = max(new_streak, streak['longest_streak'])

                conn.execute('''
                    UPDATE streaks
                    SET current_streak = ?, longest_streak = ?, last_activity_date = ?
                    WHERE user_id = ?
                ''', (new_streak, new_longest, today, user_id))
            else:
                conn.execute('''
                    UPDATE streaks
                    SET current_streak = 1, last_activity_date = ?
                    WHERE user_id = ?
                ''', (today, user_id))
        except Exception as e:
            print(f"Update Streak Error: {e}")
    
    def get_challenge_history(self, user_id, days=30):
        """
        Get user's challenge completion history.
        """
        try:
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
        except Exception:
            return []
    
    def update_challenge_progress(self, user_id, progress_value):
        """
        Update progress for today's challenge.
        Auto-complete if target reached.
        """
        conn = get_db()
        try:
            today = date.today().isoformat()

            challenge = conn.execute('''
                SELECT uc.*, c.target_value, c.xp_reward
                FROM user_challenges uc
                JOIN challenges c ON uc.challenge_id = c.id
                WHERE uc.user_id = ? AND uc.assigned_date = ? AND uc.completed = 0
            ''', (user_id, today)).fetchone()

            if not challenge:
                return False

            conn.execute('''
                UPDATE user_challenges
                SET progress = ?
                WHERE id = ?
            ''', (progress_value, challenge['id']))
            
            if progress_value >= challenge['target_value']:
                conn.execute('''
                    UPDATE user_challenges
                    SET completed = 1, completed_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (challenge['id'],))

                calculate_and_apply_rewards(user_id, challenge['xp_reward'], 0, ['challenge', 'daily'])
                self._update_streak(user_id, conn)
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Update Progress Error: {e}")
            return False

challenge_service = ChallengeService()
