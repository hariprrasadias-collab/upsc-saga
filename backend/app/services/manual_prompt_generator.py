import json
import os
from datetime import datetime
from app.db import get_db

class ManualPromptGenerator:
    """
    Generates a comprehensive 'Mega Prompt' for manual Gemini interaction.
    Aggregates logic from various services to ensure quality matches automated API calls.
    """

    @staticmethod
    def generate_comprehensive_prompt(task_data: dict) -> str:
        topic = task_data.get('topic')
        subject = task_data.get('subject')

        if not topic:
            return "Error: Topic is missing in task data."

        # 1. Gather Context (Pre-computation)
        # -----------------------------------

        # A. PYQs
        pyqs_context = ManualPromptGenerator._get_pyqs_context(topic, subject)

        # B. Syllabus Node Context (simulated or fetched if we had a method, mostly just the topic name is enough)

        # C. Recent Current Affairs
        current_affairs_context = ManualPromptGenerator._get_current_affairs_context(topic)

        # D. Weak Areas (Simulated or fetched)
        weak_areas_context = "Focus on conceptual clarity as this is a high-yield topic."

        # 2. Construct the Mega Prompt
        # ----------------------------
        prompt = f"""
You are the Brain of a UPSC Preparation App.
An aspirant has just completed the topic: "{topic}" ({subject}).

Your task is to generate comprehensive study artifacts for this topic in a SINGLE JSON response.
You must maintain the highest quality, strict UPSC relevance, and academic depth.

CONTEXT:
- Topic: {topic}
- Subject: {subject}
- Relevant PYQs:
{pyqs_context}
- Current Affairs Linkages:
{current_affairs_context}
- Strategy: {weak_areas_context}

--- INSTRUCTIONS ---

Please generate the following artifacts. return a SINGLE VALID JSON object.

1. **flashcards**: Generate 5 high-quality flashcards.
   Format: [{{ "front": "Question...", "back": "Answer..." }}]

2. **revision_note**: Explain the topic concisely (Definition, Relevance, Key Sub-topics). Max 200 words.
   Format: "String text..."

3. **mindmap**: Create a hierarchical mind map structure (at least 3 levels deep).
   Format: {{ "name": "{topic}", "children": [ {{ "name": "...", "children": [...] }} ] }}

4. **mock_test**: Create a 5-question MCQ test (UPSC Standard).
   Format: {{ "title": "Test: {topic}", "questions": [ {{ "question_text": "...", "option_a": "...", "option_b": "...", "option_c": "...", "option_d": "...", "correct_answer": "A", "explanation": "..." }} ] }}

5. **pyq_analysis**: Analyze the provided PYQs for trends, difficulty, and high-yield areas.
   Format: "String text..."

6. **foresight_predictions**: Predict 3 future questions based on trends/interdisciplinary links.
   Format: [ {{ "question": "...", "type": "MCQ", "reasoning": "..." }} ]

7. **socratic_dialogue**: Generate a 6-turn philosophical debate on this topic between a Skeptic (Socrates) and an Idealist.
   Format: {{ "dialogue": [ {{ "speakerId": "skeptic", "text": "..." }}, ... ], "verdict": {{ "winner": "...", "synthesis": "..." }} }}

8. **triangulation**: Triangulate the topic with Theory, Precedents/Case Laws, and Data.
   Format: {{ "synthesis": "...", "scholars": [{{ "name": "...", "quote": "..." }}], "data_bank": [{{ "statistic": "...", "source": "..." }}], "way_forward": {{ "immediate": "...", "long_term": "..." }} }}

9. **neural_hash**: Decode the "Examiner's Pattern" for this topic. Core themes and keywords.
   Format: {{ "core_themes": ["..."], "examiner_pattern": "...", "cross_linkages": ["..."] }}

10. **pitfalls**: List 3 common mistakes students make in this topic.
    Format: ["Mistake 1", "Mistake 2", "Mistake 3"]

11. **podcast_script**: A short 'Coffee Chat' style script (Host vs Guest) explaining the topic simply.
    Format: "Host: ... \\nGuest: ..."

12. **essay_prompt**: A philosophical or analytical Mains Essay Prompt + Thesis Hint.
    Format: "Prompt: ... \\nThesis: ..."

13. **visual_prompt**: A text-to-image prompt to visualize the concept (for Stable Diffusion).
    Format: "String..."

14. **roleplay_scenario**: A District Collector (IAS) scenario involving this topic.
    Format: "String..."

15. **map_work**: (Only if Geography/History/IR/Env) Identify 3 locations. Else return empty list.
    Format: [ {{ "name": "...", "lat": 0.0, "lon": 0.0, "reason": "...", "question": "..." }} ]

16. **topic_linkages**: Connect this topic to 3 other syllabus topics (inter-subject).
    Format: ["Linkage 1...", "Linkage 2..."]

17. **cheat_sheet**: A structured cheat sheet (Facts, Articles, Dates, Mnemonics).
    Format: {{ "title": "{topic}", "tabs": [ {{ "id": "facts", "label": "Quick Facts", "content": "..." }}, {{ "id": "mnemonics", "label": "Mnemonics", "content": "..." }} ] }}

18. **quote_bank**: 2 Quotes and 2 Data points.
    Format: "Quotes: ... \\nData: ..."

19. **timeline**: (If History) Chronological timeline. Else "N/A".
    Format: "Year - Event..."

20. **ethics_dilemma**: (If Ethics/Polity) A case study. Else "N/A".
    Format: "String..."

21. **eli5**: Explain at 3 levels (5yo, 15yo, Expert) + Analogy.
    Format: {{ "eli5": "...", "eli15": "...", "eli_expert": "...", "analogy": "...", "visual_analogy_prompt": "...", "quiz": [...] }}

--- RESPONSE FORMAT ---

Return **ONLY** the JSON object. Do not include markdown formatting (like ```json).
Ensure the JSON is valid.

{{
  "flashcards": [...],
  "revision_note": "...",
  "mindmap": {{...}},
  "mock_test": {{...}},
  "pyq_analysis": "...",
  "foresight_predictions": [...],
  "socratic_dialogue": {{...}},
  "triangulation": {{...}},
  "neural_hash": {{...}},
  "pitfalls": [...],
  "podcast_script": "...",
  "essay_prompt": "...",
  "visual_prompt": "...",
  "roleplay_scenario": "...",
  "map_work": [...],
  "topic_linkages": [...],
  "cheat_sheet": {{...}},
  "quote_bank": "...",
  "timeline": "...",
  "ethics_dilemma": "...",
  "eli5": {{...}}
}}
"""
        return prompt

    @staticmethod
    def _get_pyqs_context(topic, subject) -> str:
        try:
            conn = get_db()
            query = "SELECT year, question_text FROM pyq_questions WHERE 1=1"
            params = []

            if subject:
                query += " AND subject = ?"
                params.append(subject)

            if topic:
                query += " AND topic LIKE ?"
                params.append(f"%{topic}%")

            query += " ORDER BY year DESC LIMIT 10"

            questions = conn.execute(query, params).fetchall()
            if not questions:
                return "No specific PYQs found for this topic."

            return "\n".join([f"[{q['year']}] {q['question_text']}" for q in questions])
        except Exception as e:
            return f"Error fetching PYQs: {str(e)}"

    @staticmethod
    def _get_current_affairs_context(topic) -> str:
        try:
            from app.services.ravens_service import RavensService
            articles = RavensService.search_articles(topic)
            if not articles:
                return "No direct current affairs found."

            summary = ""
            for art in articles[:3]:
                summary += f"- {art.get('title')}: {art.get('summary', '')[:100]}...\n"
            return summary
        except Exception:
            return "Current Affairs service unavailable."
