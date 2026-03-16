"""
Neural Lace - Knowledge Ingestion Engine
Autonomously expands the Mind Palace from external sources.
"""
from app.services.model_manager import model_manager
from app.db import get_db
from app.utils.security import is_safe_url
import requests
import json
import re

class NeuralLaceService:
    def __init__(self):
        pass

    def ingest_content(self, url=None, text_content=None, context_tag="General"):
        """
        Ingests content, summarizes it, extracts entities, and links to Syllabus.
        """
        print(f"🕸️ Neural Lace: Ingesting {url or 'Text Content'}...")

        content = text_content
        if url:
            if not is_safe_url(url):
                return {"success": False, "error": "Invalid or unsafe URL"}

            try:
                # Basic Fetch
                # In real prod, use a scraper service or headless browser
                # For now, we simulate success or use a simple fetch if possible
                # If running in a restricted env, this might fail.
                # We'll wrap it safely.
                resp = requests.get(url, timeout=10)
                content = resp.text[:15000] # Limit size

                # Simple HTML cleanup (strip tags)
                content = re.sub('<[^<]+?>', '', content)

            except Exception as e:
                return {"success": False, "error": f"Fetch Failed: {e}"}

        if not content:
            return {"success": False, "error": "No content"}

        try:
            # AI Processing
            prompt = f"""
            # MISSION: KNOWLEDGE ASSIMILATION (NEURAL LACE)
            **Source:** {url or 'Text'}
            **Context:** {context_tag}

            **CONTENT:**
            {content[:8000]}... (truncated)

            **DIRECTIVE:**
            1. **Summarize:** High-density notes (max 200 words).
            2. **Extract Entities:** Key Concepts, Persons, Articles.
            3. **Syllabus Mapping:** Which GS Paper/Topic does this belong to?

            **OUTPUT JSON:**
            {{
                "title": "Generated Title",
                "summary": "Summary text...",
                "entities": ["Concept 1", "Concept 2"],
                "syllabus_tag": "GS Paper Tag (e.g. GS3 - Economy)"
            }}
            """

            response = model_manager.generate_content(prompt, model_type='fast')
            text = response.text.strip()
            if text.startswith("```"): text = text.replace("```json", "").replace("```", "").strip()

            data = json.loads(text)

            # Save to Mind Palace
            conn = get_db()

            # Find or Create Location (Syllabus Tag)
            loc = conn.execute('SELECT id FROM mind_palace_locations WHERE name = ?', (data['syllabus_tag'],)).fetchone()
            if loc:
                loc_id = loc[0]
            else:
                cursor = conn.execute('INSERT INTO mind_palace_locations (name, description, layout_type) VALUES (?, ?, ?)',
                                    (data['syllabus_tag'], f"Auto-generated zone for {data['syllabus_tag']}", "network"))
                loc_id = cursor.lastrowid

            # Save Artifact
            conn.execute('''
                INSERT INTO mind_palace_artifacts
                (location_id, title, content, type, icon, color)
                VALUES (?, ?, ?, 'auto_ingest', '🕸️', '#3498db')
            ''', (loc_id, data['title'], data['summary']))

            conn.commit()

            return {"success": True, "message": f"Assimilated: {data['title']}", "tag": data['syllabus_tag']}

        except Exception as e:
            print(f"Neural Lace Failed: {e}")
            return {"success": False, "error": str(e)}

neural_lace = NeuralLaceService()
