"""
The Newsroom - Living Textbook Engine
Autonomously updates static study material with dynamic current affairs.
"""
from app.services.model_manager import model_manager
from app.db import get_db
from datetime import datetime
import json

class NewsroomService:
    def __init__(self):
        pass

    def broadcast_updates(self, news_items=None):
        """
        Scans news items and updates relevant static notes.
        """
        print("📰 Newsroom: Broadcasting updates to static notes...")

        if not news_items:
            # Fetch from NightWatchman logs or DB
            # For now, we simulate fetching the latest briefing
            from app.db import get_db
            conn = get_db()
            briefing = conn.execute('SELECT summary FROM night_watchman_briefings ORDER BY id DESC LIMIT 1').fetchone()
            if not briefing:
                return {"message": "No news to broadcast."}
            news_text = briefing['summary']
        else:
            news_text = json.dumps(news_items)

        try:
            # 1. Identify Relevant Static Topics
            conn = get_db()
            # Get all revision card titles
            cards = conn.execute('SELECT id, title FROM revision_cards').fetchall()
            titles = [c['title'] for c in cards]

            if not titles:
                return {"message": "No static notes to update."}

            prompt = f"""
            # MISSION: THE LIVING TEXTBOOK
            **NEWS FEED:**
            {news_text[:3000]}

            **STATIC CHAPTERS:**
            {json.dumps(titles)}

            **DIRECTIVE:**
            Identify which Static Chapter is *directly* impacted by this News.
            e.g., If news is about "Governor's Pardoing Power", match it to "Polity: Governor".

            **OUTPUT JSON:**
            [
                {{
                    "card_id": "(index from list or exact title match)",
                    "title": "Exact Title from list",
                    "update_content": "Markdown text explaining the news linkage..."
                }}
            ]
            """

            response = model_manager.generate_content(prompt, model_type='fast')
            import re
            text = response.text.strip()
            if text.startswith("```"): text = text.replace("```json", "").replace("```", "").strip()

            updates = json.loads(text)

            updated_count = 0
            for update in updates:
                target_title = update.get('title')
                content_add = update.get('update_content')

                # Verify match
                card = conn.execute('SELECT id, full_content FROM revision_cards WHERE title = ?', (target_title,)).fetchone()
                if card:
                    new_section = f"\n\n---\n### 📰 Living Update ({datetime.now().strftime('%Y-%m-%d')})\n{content_add}\n"

                    # Append to content
                    conn.execute('UPDATE revision_cards SET full_content = full_content || ? WHERE id = ?', (new_section, card['id']))

                    # Log
                    print(f"📰 Newsroom: Updated '{target_title}'")
                    updated_count += 1

            conn.commit()
            return {"success": True, "updated": updated_count}

        except Exception as e:
            print(f"Newsroom Error: {e}")
            return {"success": False, "error": str(e)}

newsroom_service = NewsroomService()
