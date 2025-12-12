from app.db import get_db
from datetime import datetime

class GoalService:
    """
    Service to manage user goals.
    """
    
    @staticmethod
    def create_goal(user_id, title, type, target_value, deadline=None):
        conn = get_db()
        cursor = conn.execute('''
            INSERT INTO brain_goals (user_id, title, type, target_value, deadline)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, title, type, target_value, deadline))
        conn.commit()
        return cursor.lastrowid

    @staticmethod
    def get_goals(user_id, status='active'):
        conn = get_db()
        goals = conn.execute('''
            SELECT * FROM brain_goals
            WHERE user_id = ? AND status = ?
            ORDER BY deadline ASC
        ''', (user_id, status)).fetchall()
        return [dict(g) for g in goals]

    @staticmethod
    def update_progress(goal_id, increment_by=0, set_value=None):
        conn = get_db()
        
        # Get current goal
        goal = conn.execute('SELECT * FROM brain_goals WHERE id = ?', (goal_id,)).fetchone()
        if not goal:
            return None
            
        new_value = goal['current_value']
        if set_value is not None:
            new_value = set_value
        else:
            new_value += increment_by
            
        # Check completion
        status = goal['status']
        if new_value >= goal['target_value']:
            status = 'completed'
            
        conn.execute('''
            UPDATE brain_goals
            SET current_value = ?, status = ?
            WHERE id = ?
        ''', (new_value, status, goal_id))
        conn.commit()
        
        return {'id': goal_id, 'new_value': new_value, 'status': status}

    @staticmethod
    def check_goals_status(user_id):
        """
        Checks all active goals and returns alerts for overdue or at-risk goals.
        """
        goals = GoalService.get_goals(user_id, 'active')
        alerts = []
        
        for goal in goals:
            if goal['deadline']:
                deadline = datetime.fromisoformat(goal['deadline'])
                if datetime.now() > deadline:
                    alerts.append(f"Goal Overdue: {goal['title']}")
                    # Mark as failed? Or just overdue?
                    
        return alerts

    @staticmethod
    def break_down_goal(goal_text):
        """
        Uses AI to deconstruct a vague goal into a SMART checklist.
        """
        from app.services.model_manager import model_manager

        if not model_manager.is_configured:
            return {"error": "AI Offline"}

        prompt = f"""
        # MISSION: GOAL DECONSTRUCTION (SMARTIFY)
        **Input Goal:** "{goal_text}"

        **DIRECTIVE:**
        Break this down into a 4-week execution plan for a UPSC aspirant.

        **OUTPUT SCHEMA (JSON):**
        {{
            "refined_title": "Specific SMART Goal Title",
            "milestones": [
                {{ "week": 1, "task": "..." }},
                {{ "week": 2, "task": "..." }},
                {{ "week": 3, "task": "..." }},
                {{ "week": 4, "task": "..." }}
            ]
        }}
        """

        try:
            response = model_manager.generate_content(prompt, model_type='pro')
            import json
            text = response.text.strip().replace('```json', '').replace('```', '')
            return json.loads(text)
        except Exception as e:
            return {"error": str(e)}
