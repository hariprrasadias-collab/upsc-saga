"""
The Oracle - Psychometric Profiling Service
Analyzes user behavior to create a dynamic 'Cognitive Model' for AI personalization.
"""
import json
from app.db import get_db
from app.services.model_manager import model_manager

class PsychometricService:
    def __init__(self):
        self.profile_cache = None

    def build_user_profile(self, user_id=1):
        """
        Scans history to deduce learning style, weaknesses, and biorhythms.
        """
        print("🔮 Oracle: Building Psychometric Profile...")
        try:
            conn = get_db()

            # 1. Gather Data Points
            # A. Activity Time Distribution
            activity_times = conn.execute('''
                SELECT strftime('%H', executed_at) as hour, COUNT(*) as count
                FROM brain_action_log
                WHERE user_id = ?
                GROUP BY hour
            ''', (user_id,)).fetchall()

            # B. Success/Failure Patterns
            performance = conn.execute('''
                SELECT action_type,
                       SUM(CASE WHEN outcome_status='success' THEN 1 ELSE 0 END) as wins,
                       SUM(CASE WHEN outcome_status='failure' THEN 1 ELSE 0 END) as losses
                FROM brain_action_log
                WHERE user_id = ?
                GROUP BY action_type
            ''', (user_id,)).fetchall()

            # C. Recent Feedback (if any)
            # Assuming we had a feedback table, but we use action logs reasoning for now

            # 2. Synthesize with AI
            data_summary = {
                "activity_peaks": {row['hour']: row['count'] for row in activity_times},
                "performance": {row['action_type']: f"{row['wins']}W-{row['losses']}L" for row in performance}
            }

            prompt = f"""
            # MISSION: PSYCHOMETRIC PROFILING
            **Role:** Cognitive Psychologist.

            **USER DATA:**
            {json.dumps(data_summary, indent=2)}

            **DIRECTIVE:**
            Construct a 'Cognitive Persona' for this user.
            1. **Learning Style:** (Visual/Textual/Socratic?)
            2. **Peak Hours:** (Morning Lark / Night Owl?)
            3. **Cognitive Bias:** (Overconfident/Anxious?)
            4. **Instructional Preference:** (Direct/Metaphorical?)

            **OUTPUT JSON:**
            {{
                "learning_style": "...",
                "peak_hours": "...",
                "bias_tendency": "...",
                "prompt_instruction": "Always use..."
            }}
            """

            response = model_manager.generate_content(prompt, model_type='fast')
            text = response.text.strip()
            if text.startswith("```"):
                text = text.replace('```json', '').replace('```', '').strip()

            profile = json.loads(text)
            self.profile_cache = profile

            # Save to DB (Persistent Store - User Metadata)
            # Assuming a user_metadata table or similar. If not, we store in a file or generic key-value
            # We'll stick to in-memory/file cache if DB schema is rigid,
            # but let's try to update the 'users' table if it has a 'profile' column,
            # or just save to a JSON file for simplicity and robustness.

            with open("user_psychometrics.json", "w") as f:
                json.dump(profile, f)

            print(f"🔮 Oracle: Profile Updated -> {profile['learning_style']}")
            return profile

        except Exception as e:
            print(f"🔮 Profile Build Failed: {e}")
            return self.get_default_profile()

    def get_profile(self):
        """
        Retrieves current profile (cached or from disk).
        """
        if self.profile_cache:
            return self.profile_cache

        try:
            with open("user_psychometrics.json", "r") as f:
                self.profile_cache = json.load(f)
                return self.profile_cache
        except:
            return self.get_default_profile()

    def get_default_profile(self):
        return {
            "learning_style": "Balanced",
            "peak_hours": "Unknown",
            "prompt_instruction": "Be concise and clear."
        }

psychometric_service = PsychometricService()
