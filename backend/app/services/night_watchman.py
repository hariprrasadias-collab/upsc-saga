"""
The Night Watchman - Autonomous Research Service
"""
import os
import feedparser
import google.generativeai as genai
from datetime import datetime
from app.db_models.night_watchman import save_briefing

class NightWatchman:
    def __init__(self):
        self.api_key = os.environ.get('GEMINI_API_KEY')
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro-latest')
        
        self.feeds = [
            'https://www.thehindu.com/news/national/feeder/default.rss',
            'https://pib.gov.in/RSS/RssFeed.aspx?ModId=2',
            'https://indianexpress.com/section/india/feed/',
            'https://www.thehindu.com/opinion/editorial/feeder/default.rss'
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
            'articles_count': len(articles)
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
        """Use AI to create a cohesive morning report"""
        if not self.model:
            return {
                "summary": "AI Offline. Raw Intelligence gathered.",
                "quote": "Knowledge is power."
            }
            
        # Prepare context
        articles_text = "\n\n".join([
            f"- {a['title']} ({a['source']}): {a['summary'][:200]}..." 
            for a in articles[:15] # Limit to top 15 to fit context
        ])
        
        prompt = f"""
        You are 'The Night Watchman', an autonomous research agent for a UPSC aspirant.
        While the user slept, you gathered the following intelligence (News):
        
        {articles_text}
        
        TASK:
        Create a "Morning Briefing" (Markdown format).
        1. **Executive Summary**: 3-4 bullet points of the MOST important UPSC-relevant news.
        2. **Deep Dive**: Pick ONE topic that is highly relevant to UPSC Syllabus and explain its significance (connect to Static syllabus).
        3. **Quote of the Day**: A stoic or motivational quote for a student.
        
        OUTPUT FORMAT (JSON):
        {{
            "summary": "Markdown string...",
            "quote": "Quote text..."
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            import json
            import re
            
            text = response.text.strip()
            # Extract JSON
            json_match = re.search(r"\{.*\}", text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            else:
                return {"summary": text, "quote": "Carpe Diem."}
                
        except Exception as e:
            print(f"❌ Watchman Synthesis Error: {e}")
            return {
                "summary": "Failed to synthesize briefing due to interference.",
                "quote": "Perseverance is key."
            }

night_watchman = NightWatchman()
