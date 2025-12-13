"""
The Scholar - Deep Synthesis Engine
Generates comprehensive "Micro-Books" by synthesizing all available knowledge.
"""
from app.services.model_manager import model_manager
from app.db import get_db
import json
from datetime import datetime

class ScholarService:
    def __init__(self):
        pass

    def generate_micro_book(self, topic, subject):
        """
        Authors a cohesive "Micro-Book" on a topic.
        Synthesizes: Static Theory + Dynamic News + Neural Lace + PYQs.
        """
        print(f"🎓 Scholar: Authoring Micro-Book for '{topic}'...")

        try:
            # 1. Gather Source Material
            # A. Neural Lace (External Knowledge)
            from app.db import get_db
            conn = get_db()
            lace_data = conn.execute('''
                SELECT title, content FROM mind_palace_artifacts
                WHERE title LIKE ? OR content LIKE ?
                LIMIT 5
            ''', (f"%{topic}%", f"%{topic}%")).fetchall()

            # B. Newsroom (Current Affairs)
            news_data = conn.execute('''
                SELECT summary FROM night_watchman_briefings
                ORDER BY id DESC LIMIT 5
            ''').fetchall()

            # C. PYQs
            pyq_data = conn.execute('''
                SELECT question_text FROM pyq_questions
                WHERE topic LIKE ? LIMIT 5
            ''', (f"%{topic}%",)).fetchall()

            context = f"""
            **EXTERNAL KNOWLEDGE (Neural Lace):**
            {json.dumps([r['content'][:500] for r in lace_data])}

            **RECENT NEWS (Newsroom):**
            {json.dumps([r['summary'][:500] for r in news_data])}

            **EXAM PATTERN (PYQs):**
            {json.dumps([r['question_text'] for r in pyq_data])}
            """

            # 2. Structure the Book
            outline_prompt = f"""
            # MISSION: BOOK ARCHITECTURE
            **Title:** {topic}
            **Subject:** {subject}

            **DIRECTIVE:**
            Design a 5-Chapter Table of Contents for a high-density "Micro-Book" for UPSC.
            Flow: Origin -> Theory -> Current Relevance -> Debates -> Way Forward.

            **OUTPUT JSON:**
            [ "Chapter 1: ...", "Chapter 2: ...", ... ]
            """

            response = model_manager.generate_content(outline_prompt, model_type='pro')
            chapters = self._parse_json(response.text)

            book_content = {
                "title": f"The {topic} Manifesto",
                "subject": subject,
                "author": "The Scholar (AI)",
                "generated_at": datetime.now().isoformat(),
                "chapters": []
            }

            # 3. Write Chapters (Parallel or Sequential)
            # Sequential for coherence
            for i, chapter_title in enumerate(chapters):
                print(f"  ✍️ Writing {chapter_title}...")
                chapter_prompt = f"""
                # MISSION: CHAPTER AUTHORING
                **Book:** {topic}
                **Chapter:** {chapter_title}

                **CONTEXT:**
                {context}

                **DIRECTIVE:**
                Write a rich, academic, and exam-oriented chapter (300 words).
                Use Markdown. Include case laws, data, and scholar quotes if relevant.
                """

                chap_response = model_manager.generate_content(chapter_prompt, model_type='pro')
                book_content['chapters'].append({
                    "title": chapter_title,
                    "content": chap_response.text,
                    "key_concepts": self._extract_keywords(chap_response.text)
                })

            # 4. Save Artifact
            # We save it as a 'Subject Book' type content in 'ai_generated_content' table?
            # Or use 'subject_books' table if it exists?
            # Let's check `backend/app/db_models/autonomous_brain.py`...
            # Actually, `SubjectBookRenderer` expects a certain format.

            # We'll save to `ai_generated_content` with `content_type='subject_book'`
            # This aligns with `BrainVault`

            conn.execute('''
                INSERT INTO ai_generated_content (content_type, topic, content, metadata)
                VALUES (?, ?, ?, ?)
            ''', ('subject_book', topic, json.dumps(book_content), json.dumps({'subject': subject})))
            conn.commit()

            return {"success": True, "book": book_content}

        except Exception as e:
            print(f"Scholar Failed: {e}")
            return {"success": False, "error": str(e)}

    def _parse_json(self, text):
        try:
            if "```" in text: text = text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
        except:
            return []

    def _extract_keywords(self, text):
        # Simple heuristic or AI? AI for quality.
        try:
            p = f"Extract 3 technical keywords from: {text[:500]}"
            r = model_manager.generate_content(p, model_type='fast')
            return [k.strip() for k in r.text.split(',')]
        except:
            return ["Concept"]

scholar_service = ScholarService()
