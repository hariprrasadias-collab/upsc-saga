import json
import os
from datetime import datetime

LESSONS_FILE = "brain_lessons.json"

class HippocampusService:
    """
    The Hippocampus: Responsible for Long-Term Memory and Learning.
    Stores 'Lessons' derived from failures and successes.
    """
    
    def __init__(self):
        # Determine backend root (assuming this file is in backend/app/services/)
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.memory_path = os.path.join(base_dir, LESSONS_FILE)
        self._load_memory()
        
    def _load_memory(self):
        try:
            if os.path.exists(self.memory_path):
                with open(self.memory_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        self.memory = json.loads(content)
                    else:
                        self.memory = {"lessons": []}
            else:
                self.memory = {"lessons": []}
        except Exception as e:
            print(f"⚠️ Hippocampus Load Error: {e}")
            self.memory = {"lessons": []}
            
    def _save_memory(self):
        try:
            with open(self.memory_path, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, indent=2)
        except Exception as e:
            print(f"❌ Hippocampus Write Error: {e}")

    def remember_lesson(self, context: str, lesson: str, source: str = "Hephaestus"):
        """
        Stores a new lesson.
        """
        if not lesson: return

        try:
            entry = {
                "timestamp": datetime.now().isoformat(),
                "context": context,
                "lesson": lesson,
                "source": source
            }
            if "lessons" not in self.memory:
                self.memory["lessons"] = []

            self.memory["lessons"].append(entry)
            self._save_memory()
            # print(f"🧠 Hippocampus: Lesson Learned -> {lesson}") # Reduced spam
        except Exception as e:
            print(f"Hippocampus Memory Error: {e}")

    def recall_lessons(self, current_context: str = "") -> list:
        """
        Retrieves relevant lessons.
        """
        try:
            if "lessons" not in self.memory or not self.memory["lessons"]:
                return []
            # Return last 5 lessons
            return [l.get('lesson', '') for l in self.memory["lessons"][-5:]]
        except Exception:
            return []

hippocampus = HippocampusService()
