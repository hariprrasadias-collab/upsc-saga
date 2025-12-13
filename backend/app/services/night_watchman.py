"""
The Night Watchman - Autonomous Research Service
"""
import os
import json
import feedparser
from datetime import datetime
from app.db_models.night_watchman import save_briefing
from app.services.model_manager import model_manager
from dotenv import load_dotenv

load_dotenv()

class NightWatchman:
    def __init__(self):
        # API Config managed by model_manager
        
        self.feeds = [
            'https://www.thehindu.com/news/national/feeder/default.rss',
            'https://pib.gov.in/RSS/RssFeed.aspx?ModId=2',
            'https://indianexpress.com/section/india/feed/',
            'https://www.thehindu.com/opinion/editorial/feeder/default.rss',
            'https://www.downtoearth.org.in/rss/feed' # Environment
        ]

    def perform_nightly_watch(self, force=False):
        """
        Main execution method.
        1. Checks if already ran today (Idempotency).
        2. Scrapes news.
        3. Synthesizes 'Morning Briefing'.
        4. Saves to DB.
        """
        print("🦉 Night Watchman: Beginning patrol...")
        
        if not force:
            from app.db import get_db
            conn = get_db()
            today = datetime.now().strftime('%Y-%m-%d')
            existing = conn.execute('SELECT id FROM night_watchman_briefings WHERE date = ?', (today,)).fetchone()
            if existing:
                print(f"🦉 Night Watchman: Briefing for {today} already exists. Standing down.")
                return {"success": True, "briefing_id": existing['id'], "message": "Already completed today."}
        
        # 1. Gather Intelligence
        articles = self._gather_intelligence()
        if not articles:
            print("🦉 Night Watchman: No intel gathered. Aborting.")
            return {"success": False, "message": "No intelligence gathered."}
            
        # 2. Synthesize Briefing
        briefing = self._synthesize_briefing(articles)
        if not briefing:
             print("🦉 Night Watchman: Synthesis failed. Aborting.")
             return {"success": False, "message": "Synthesis failed."}
        
        # 3. Save Report
        briefing_id = save_briefing({
            'date': datetime.now().strftime('%Y-%m-%d'),
            'summary': briefing.get('summary', 'Analysis failed.'),
            'quote': briefing.get('quote', 'The early bird catches the worm.'),
            'articles_count': len(articles),
            'mind_map': briefing.get('mind_map', ''),
            'static_linkage': briefing.get('static_linkage', ''),
            'quiz': briefing.get('quiz', [])
        })
        
        print(f"🦉 Night Watchman: Patrol complete. Briefing #{briefing_id} filed.")
        
        # 4. Trigger REM Sleep (Autonomy)
        self.perform_rem_sleep_cycle()

        # 5. Weekly Self-Review (Sundays only)
        if datetime.now().weekday() == 6: # Sunday
            try:
                from app.services.self_review import self_review_service
                print("📅 Sunday Detected: Conducting Weekly Self-Review...")
                self_review_service.perform_review(lookback_days=7)
            except Exception as e:
                print(f"Weekly Review Failed: {e}")
        
        return {
            "success": True, 
            "briefing_id": briefing_id
        }

    def perform_rem_sleep_cycle(self):
        """
        REM SLEEP: Autonomous processing of the day's events.
        Builds insights and strengthens memory without user input.
        """
        print("🌙 Night Watchman: Entering REM Sleep...")
        try:
            from app.db import get_db
            from app.services.hippocampus_service import hippocampus
            
            conn = get_db()
            
            # 1. Fetch today's actions
            actions = conn.execute('''
                SELECT action_type, outcome_status, created_at 
                FROM brain_action_log 
                WHERE date(created_at) = date('now')
            ''').fetchall()
            
            if not actions:
                print("🌙 REM: No actions to process.")
                return

            action_summary = "\n".join([f"- {a['action_type']}: {a['outcome_status']}" for a in actions])
            
            # 2. Dream / Analyze
            prompt = f"""
            # MISSION: REM SLEEP ANALYSIS (META-COGNITION)
            **Role:** The Subconscious Strategist.
            
            **DAY'S ACTIVITY LOG:**
            {action_summary}
            
            **DIRECTIVE:**
            Synthesize a 'Lesson Learned' or 'Strategic Adjustment' based on performance.
            - If failures > successes: Suggest rest or foundational revision.
            - If rapid success: Suggest increasing difficulty level.
            - If idle: Suggest a motivation kick.

            **OUTPUT:**
            A concise, actionable insight (max 2 sentences).
            """
            
            # Use Pro model for insight
            response = model_manager.generate_content(prompt, model_type='pro')
            insight = response.text.strip()
            
            # 3. Store in Long-Term Memory
            hippocampus.remember_lesson(
                context="REM Sleep Analysis",
                lesson=insight,
                source="NightWatchman"
            )
            print(f"🌙 REM Insight Stored: {insight}")
            
        except Exception as e:
            print(f"🌙 REM Sleep Failed: {e}")


    def _gather_intelligence(self):
        """Fetch news from RSS feeds with Headers"""
        articles = []
        import socket
        # Set default timeout for socket operations
        socket.setdefaulttimeout(10)

        # Custom User Agent to avoid 403 Forbidden
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/rss+xml, application/xml, text/xml, */*'
        }

        for url in self.feeds:
            try:
                # Use feedparser with header support if possible, or request separately
                # Feedparser handles http/https but sometimes needs help with headers
                d = feedparser.parse(url, request_headers=headers)

                # Check for bozo bit (parsing error)
                if d.bozo:
                    print(f"⚠️ Feed parsing issue for {url}: {d.bozo_exception}")
                    # Continue anyway if entries exist

                if not d.entries:
                     print(f"⚠️ No entries found for {url} (Status: {d.get('status', 'Unknown')})")

                for entry in d.entries[:5]: # Top 5 from each
                    articles.append({
                        'title': entry.title,
                        'summary': entry.get('summary', ''),
                        'link': entry.link,
                        'source': d.feed.get('title', 'Unknown')
                    })
            except Exception as e:
                print(f"⚠️ Watchman failed to scout {url}: {e}")
        return articles

    def _synthesize_briefing(self, articles):
        """Use AI to create a cohesive morning report with Deep Analysis"""
        # Manager handles availability check
            
        # Prepare context
        articles_text = "\n\n".join([
            f"- {a['title']} ({a['source']}): {a['summary'][:300]}..." 
            for a in articles[:20] # Limit context size
        ])
        
        prompt = f"""
        You are 'The Night Watchman', an elite autonomous research agent for a UPSC Civil Services aspirant.
        While the user slept, you gathered the following intelligence (News):
        
        {articles_text}
        
        TASK:
        Create a "Morning Briefing" that is NOT just a summary, but a STRATEGIC ASSET.
        
        1. **Relevance Filter**: Ignore any news with < 7/10 relevance to UPSC.
        2. **Syllabus Mapping**: Map every selected story to a specific GS Paper (GS1/GS2/GS3/GS4).
        3. **Editorial Analysis**: For opinions/editorials, extract the Core Argument, Pros, and Cons.
        4. **Auto-Flashcards**: Generate 3 high-yield flashcards from today's news.
        5. **Visual Intelligence**: Create a Mermaid.js Mind Map syntax (graph TD) for the "Deep Dive" topic.
        6. **Static Linkage**: Connect the "Deep Dive" topic to a specific standard book chapter (e.g., "Laxmikanth Ch 10").
        7. **Daily Quiz**: Generate 5 MCQs based on the briefing to test retention.
        
        OUTPUT FORMAT (JSON):
        {{
            "summary": "Markdown string containing:\\n- **Executive Summary** (Top 3 stories with GS Tags)\\n- **Deep Dive** (Best Editorial Analysis)\\n- **Flashcards** (Front/Back format)",
            "quote": "Stoic/Motivational quote...",
            "flashcards": [
                {{"front": "...", "back": "...", "tags": ["GS2", "Polity"]}}
            ],
            "mind_map": "graph TD; A[Topic] --> B[Subtopic]; ...",
            "static_linkage": "Laxmikanth Chapter 10 (Parliament)",
            "quiz": [
                {{
                    "question": "Question text...",
                    "options": ["A", "B", "C", "D"],
                    "correct_answer": "A",
                    "explanation": "Brief explanation..."
                }},
                ... (5 questions)
            ]
        }}
        """
        
        
        
        # Retry logic for rate limits
        try:
            # Use Pro model for deep synthesis
            response = model_manager.generate_content(prompt, model_type='pro')
            import json
            import re
            
            text = response.text.strip()
            
            if text.startswith("```"):
                text = text.replace('```json', '').replace('```', '').strip()
                
            # Extract JSON
            start = text.find('{')
            end = text.rfind('}')
            
            if start != -1 and end != -1:
                data = json.loads(text[start:end+1])
                
                # If flashcards are present, we could save them to the DB here
                # For now, we just return them in the briefing
                if 'flashcards' in data:
                    self._save_auto_flashcards(data['flashcards'])
                    
                return data
            else:
                print(f"⚠️ Synthesis Failed: No JSON found")
                return {"summary": text, "quote": "Carpe Diem."}
        
        except Exception as e:
            print(f"⚠️ Synthesis Error: {e}")
            return {
                "summary": f"**Briefing Unavailable**\n\nThe Watchman encountered heavy interference (API Error: {str(e)}). Please try again later.",
                "quote": "Perseverance is key."
            }

    def _save_auto_flashcards(self, cards):
        """Save generated flashcards to the 'Current Affairs' deck"""
        try:
            from app.db import get_db
            conn = get_db()
            for card in cards:
                conn.execute('''
                    INSERT INTO flashcards (front, back, tags, review_status)
                    VALUES (?, ?, ?, 'new')
                ''', (card['front'], card['back'], json.dumps(card.get('tags', ['Current Affairs']))))
            conn.commit()
            print(f"⚡ Night Watchman: Created {len(cards)} auto-flashcards.")
        except Exception as e:
            print(f"⚡ Flashcard Save Error: {e}")

night_watchman = NightWatchman()
