"""
The Director - Strategic Intervention System.
Monitors user velocity and injects interventions.
"""
from datetime import datetime, timedelta
import json
from app.db import get_db
from app.services.model_manager import model_manager

class DirectorService:
    def __init__(self):
        pass

    def check_user_velocity(self, user_id=1):
        """
        Calculates tasks/hour and focus quality.
        Triggers intervention if velocity drops.
        """
        print("🎬 Director: Checking Velocity...")
        try:
            conn = get_db()

            # Get completed tasks for today
            today = datetime.now().strftime('%Y-%m-%d')

            # Check if any "Intervention" tasks are already pending (don't spam)
            pending_intervention = conn.execute('''
                SELECT COUNT(*) FROM tasks
                WHERE user_id = ? AND title LIKE '🚨%' AND isCompleted = 0
            ''', (user_id,)).fetchone()[0]

            if pending_intervention > 0:
                return {"status": "INTERVENTION_PENDING", "velocity": 0}

            # Count completed tasks
            completed = conn.execute('''
                SELECT COUNT(*) FROM tasks
                WHERE user_id = ? AND isCompleted = 1
                AND due_date = ?
            ''', (user_id, today)).fetchone()[0]

            now = datetime.now()

            # Heuristic: If it's past 10 AM and 0 tasks done -> STAGNATION
            if completed == 0 and now.hour >= 10:
                self._trigger_intervention("STAGNATION", user_id)
                return {"status": "STAGNATION", "velocity": 0, "intervention": "Triggered"}

            return {"status": "FLOW", "velocity": completed}

        except Exception as e:
            print(f"Director Error: {e}")
            return {"error": str(e)}

    def _trigger_intervention(self, type, user_id):
        print(f"🎬 Director: Triggering {type} Intervention!")

        try:
            # 1. Generate Content
            if type == "STAGNATION":
                prompt = """
                User has done NOTHING all morning.
                Generate a 'Micro-Intervention' task title (max 6 words).
                Type: QUICK_WIN (e.g., 'Read 1 page of notes', 'Do 5 MCQs').
                Tone: Drill Sergeant.
                """
                response = model_manager.generate_content(prompt, model_type='fast')
                task_title = response.text.strip().replace('"', '').replace("'", "")

                # 2. Inject into DB
                from app.db import get_db
                conn = get_db()
                conn.execute('''
                    INSERT INTO tasks (user_id, title, priority, is_quest, due_date, isCompleted, xp_reward)
                    VALUES (?, ?, 'HIGH', 1, ?, 0, 50)
                ''', (user_id, f"🚨 {task_title}", datetime.now().strftime('%Y-%m-%d')))
                conn.commit()
                print(f"🎬 Director: Injected task '{task_title}'")
        except Exception as e:
            print(f"Intervention Failed: {e}")

director_service = DirectorService()
