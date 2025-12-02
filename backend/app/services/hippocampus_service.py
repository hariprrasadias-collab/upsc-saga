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
        self.memory_path = os.path.join(os.path.dirname(__file__), '..', '..', LESSONS_FILE)
        self._load_memory()
        
    def _load_memory(self):
        if os.path.exists(self.memory_path):
            try:
                with open(self.memory_path, 'r') as f:
                    self.memory = json.load(f)
            except:
                self.memory = {"lessons": []}
        else:
            self.memory = {"lessons": []}
            
    def _save_memory(self):
        try:
            with open(self.memory_path, 'w') as f:
                json.dump(self.memory, f, indent=2)
        except Exception as e:
            print(f"❌ Hippocampus Write Error: {e}")

    def remember_lesson(self, context: str, lesson: str, source: str = "Hephaestus"):
        """
        Stores a new lesson.
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "context": context, # e.g., "AttributeError in BrainService"
            "lesson": lesson,   # e.g., "Always check if datetime is imported as class or module"
            "source": source
        }
        self.memory["lessons"].append(entry)
        self._save_memory()
        print(f"🧠 Hippocampus: Lesson Learned -> {lesson}")

    def recall_lessons(self, current_context: str = "") -> list:
        """
        Retrieves relevant lessons.
        For now, returns the last 5 lessons to keep context fresh.
        Future: Use semantic search/embeddings.
        """
        # Return last 5 lessons
        return [l['lesson'] for l in self.memory["lessons"][-5:]]

hippocampus = HippocampusService()
