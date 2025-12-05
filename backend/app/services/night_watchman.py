"""
The Night Watchman - Autonomous Research Service
"""
import os
import json
import feedparser
import google.generativeai as genai
from datetime import datetime
from app.db_models.night_watchman import save_briefing
from dotenv import load_dotenv

load_dotenv()

class NightWatchman:
    def __init__(self):
        self.model = None # Initialize to None
        self.api_key = os.environ.get('GEMINI_API_KEY')
        
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-flash-latest')
                print("🦉 Night Watchman: Vision Online (Model Loaded)")
            except Exception as e:
                print(f"⚠️ Night Watchman Vision Error: {e}")
        else:
            print("⚠️ Night Watchman Warning: GEMINI_API_KEY not found in environment")
        
        self.feeds = [
            'https://www.thehindu.com/news/national/feeder/default.rss',
            'https://pib.gov.in/RSS/RssFeed.aspx?ModId=2',
            'https://indianexpress.com/section/india/feed/',
            'https://www.thehindu.com/opinion/editorial/feeder/default.rss',
            'https://www.downtoearth.org.in/rss/feed' # Environment
        ]

    def perform_nightly_watch(self):
        """
        Main execution method.
        1. Scrapes news.
        2. Synthesizes 'Morning Briefing'.
        3. Saves to DB.
        """
        print("🦉 Night Watchman: Beginning patrol...")
        
        # 1. Gather Intelligence
        articles = self._gather_intelligence()
        if not articles:
            return {"success": False, "message": "No intelligence gathered."}
            
        # 2. Synthesize Briefing
        briefing = self._synthesize_briefing(articles)
        
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
            Analyze the user's activity today to generate a strategic insight.
            
            ACTIVITY LOG:
            {action_summary}
            
            TASK:
            Generate ONE high-value insight or lesson for the user.
            Focus on patterns (e.g., "You failed 3 mock tests today, maybe rest?").
            """
            
            response = self.model.generate_content(prompt)
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
        """Fetch news from RSS feeds"""
        articles = []
        for url in self.feeds:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:5]: # Top 5 from each
                    articles.append({
                        'title': entry.title,
                        'summary': entry.get('summary', ''),
                        'link': entry.link,
                        'source': feed.feed.get('title', 'Unknown')
                    })
            except Exception as e:
                print(f"⚠️ Watchman failed to scout {url}: {e}")
        return articles

    def _synthesize_briefing(self, articles):
        """Use AI to create a cohesive morning report with Deep Analysis"""
        if not self.model:
            return {
                "summary": "AI Offline. Raw Intelligence gathered.",
                "quote": "Knowledge is power."
            }
            
        # Prepare context
        articles_text = "\n\n".join([
            f"- {a['title']} ({a['source']}): {a['summary'][:300]}..." 
            for a in articles[:20] # Increased limit
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
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                import json
                import re
                
                text = response.text.strip()
                # Extract JSON
                json_match = re.search(r"\{.*\}", text, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group(0))
                    
                    # If flashcards are present, we could save them to the DB here
                    # For now, we just return them in the briefing
                    if 'flashcards' in data:
                        self._save_auto_flashcards(data['flashcards'])
                        
                    return data
                else:
                    print(f"⚠️ Synthesis Attempt {attempt+1} Failed: No JSON found")
                    if attempt == max_retries - 1:
                        return {"summary": text, "quote": "Carpe Diem."}
            
            except Exception as e:
                print(f"⚠️ Synthesis Attempt {attempt+1} Error: {e}")
                if "429" in str(e) or "ResourceExhausted" in str(e):
                    if attempt < max_retries - 1:
                        import time
                        wait_time = retry_delay * (2 ** attempt)
                        print(f"⏳ Quota exceeded. Retrying in {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                
                if attempt == max_retries - 1:
                    return {
                        "summary": f"**Briefing Unavailable**\n\nThe Watchman encountered heavy interference (API Error: {str(e)}). Please try again later.",
                        "quote": "Perseverance is key."
                    }
        
        return None

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
