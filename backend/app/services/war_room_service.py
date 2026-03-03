import json
from datetime import datetime
from app.services.model_manager import ModelManager

class WarRoomService:
    def __init__(self):
        self.model_manager = ModelManager()

    def generate_morning_brief(self, user_id, today_tasks):
        """
        Generates a highly-tactical, God-Level "Morning Briefing" using Gemini 3.0 / NIM.
        Cross-references today's tasks with UPSC PYQ weightage and common traps.
        """
        if not today_tasks:
            return {
                "success": True,
                "brief": {
                    "title": "A Day of Rest",
                    "directive": "No active battlefronts today. Recover and prepare for the next deployment.",
                    "primary_target": None,
                    "threat_level": "LOW",
                    "tactical_breakdown": [],
                    "quote": "Victorious warriors win first and then go to war, while defeated warriors go to war first and then seek to win. - Sun Tzu"
                }
            }

        # Format tasks for the AI Prompt
        task_strings = []
        for t in today_tasks:
            st = t.get('study_tasks')
            if st:
                task_strings.append(f"[{st.get('subject', 'Unknown')}] {st.get('topic', 'Unknown')}")
        
        task_list_str = "\n".join(task_strings)

        prompt = f"""
        You are the Supreme Commander AI of a UPSC aspirant's "War Room". 
        Your job is to provide a highly tactical, intense "Morning Briefing" for today's study targets.

        TODAY'S TARGETS:
        {task_list_str}

        YOUR MISSION:
        1. Analyze these targets against actual UPSC Civil Services Examination trends (PYQs, Prelims/Mains weightage).
        2. Identify the single most critical 'Primary Target' among them.
        3. Define the 'Threat Level' (e.g., CRITICAL, ELEVATED, STANDARD) based on how notoriously tricky the UPSC makes questions from these areas (e.g., Art & Culture or core Economy is CRITICAL).
        4. Provide a 'Tactical Breakdown' (3-4 bullet points) detailing specific sub-topics they MUST focus on, common traps/exceptions examiners use, and the angle they should take (e.g., 'Focus on mapping rivers for this Geography topic').
        5. Provide a motivational quote fitting for a commander.

        RESPOND STRICTLY IN VALID JSON FORMAT matching this exact structure:
        {{
            "title": "[A badass title for today's briefing, e.g., 'Operation Sovereign']",
            "directive": "[A 2-sentence overarching command/summary of the day's meta-goal]",
            "primary_target": "[The most crucial task from the list]",
            "threat_level": "[CRITICAL, ELEVATED, STANDARD, or LOW]",
            "tactical_breakdown": [
                "[Specific actionable advice 1]",
                "[Specific actionable advice 2]",
                "[Specific actionable advice 3]"
            ],
            "quote": "[Quote]"
        }}
        """

        try:
            # 1. Primary Request using Fast Models (Since this needs to load on the dashboard quickly)
            response_json = self.model_manager.generate_content(prompt, provider_preference="google_fast", expect_json=True)
            
            if response_json:
                # Fallback responses are objects, we need to extract their text via stringification if necessary
                if hasattr(response_json, 'text'):
                     raw_str = response_json.text
                else:
                     raw_str = str(response_json)
                     
                # Minor cleanup in case the AI added markdown backticks
                raw_str = raw_str.strip()
                if raw_str.startswith('```json'):
                     raw_str = raw_str[7:]
                if raw_str.endswith('```'):
                     raw_str = raw_str[:-3]
                     
                data = json.loads(raw_str)
                return {"success": True, "brief": data}
            else:
                 return {
                    "success": False,
                    "message": "AI failed to generate brief."
                }
        except Exception as e:
             return {
                "success": False,
                "message": f"Error parsing brief: {str(e)}"
            }
