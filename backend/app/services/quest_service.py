import json
import random
from app.db import get_db

class QuestService:
    def generate_daily_quests(self, user_id=1):
        """
        Generates daily quests for the user.
        For now, returns a static set or simple randomized set.
        """
        quests = [
            {
                "title": "The Historian's Trial",
                "description": "Complete 2 History Mock Tests",
                "xp_reward": 150,
                "type": "Training",
                "difficulty": "Medium"
            },
            {
                "title": "Polity Governance",
                "description": "Read 1 Chapter of Laxmikanth",
                "xp_reward": 100,
                "type": "Study",
                "difficulty": "Easy"
            },
            {
                "title": "Current Affairs Update",
                "description": "Read today's editorial",
                "xp_reward": 50,
                "type": "Knowledge",
                "difficulty": "Easy"
            }
        ]
        
        # In a real implementation, we would save these to a 'quests' table
        # For now, we return them to be displayed or processed by the Brain
        return quests

quest_service = QuestService()
