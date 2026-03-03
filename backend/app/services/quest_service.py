import json
import random
from app.db import get_db
from app.services.model_manager import model_manager

class QuestService:
    def generate_daily_quests(self, user_id=1):
        """
        Generates daily missions categorized by difficulty: Vanguard, Standard, Epic.
        Uses ModelManager to generate contextual UPSC quests.
        """
        try:
            prompt = """
            You are the "Mission Control AI" for a gamified UPSC preparation app.
            Generate 3 unique, actionable daily study quests for the aspirant. 
            The quests MUST strictly follow these difficulty tiers:
            1. 'Vanguard' (Easy/Quick): 50 XP. E.g., read an editorial, review 10 flashcards.
            2. 'Standard' (Medium): 100 XP. E.g., Read 1 chapter of Polity, complete a mini mock test.
            3. 'Epic' (Hard/Time-Consuming): 250 XP. E.g., Write 2 full essays, complete a 3-hour PYQ session.

            Return ONLY valid JSON in this exact format, with no markdown formatting or extra text:
            [
              {
                "title": "Short catchy name (e.g., Vanguard: Daily Editorial)",
                "description": "Specific action to take.",
                "xp_reward": 50,
                "type": "intelligence",
                "difficulty": "Vanguard"
              },
              ...
            ]
            Note: "type" must be one of the RPG stats: 'intelligence', 'endurance', 'wisdom', 'charisma'.
            """
            
            response = model_manager.generate_content(prompt)
            # Find JSON block if wrapped in markdown
            text = response.text.replace("```json", "").replace("```", "").strip()
            quests = json.loads(text)
            
            return quests
        except Exception as e:
            print(f"Quest Generation Error: {e}")
            # Fallback safe quests
            return [
                {
                    "title": "Vanguard: Review",
                    "description": "Review yesterday's notes for 15 minutes.",
                    "xp_reward": 50,
                    "type": "wisdom",
                    "difficulty": "Vanguard"
                },
                {
                    "title": "Standard: Core Study",
                    "description": "Read 1 GS chapter and take notes.",
                    "xp_reward": 100,
                    "type": "intelligence",
                    "difficulty": "Standard"
                },
                {
                    "title": "Epic: Mock Test",
                    "description": "Complete a full 100-question GS mock test.",
                    "xp_reward": 250,
                    "type": "endurance",
                    "difficulty": "Epic"
                }
            ]

quest_service = QuestService()
