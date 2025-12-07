"""
Project Foresight - Predictive Question Engine
Analyzes PYQs and current affairs to predict probable future questions
"""

from typing import List, Dict
import google.generativeai as genai
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import json
import re
from app.db_models.automation_storage import save_foresight_prediction
from app.services.model_manager import model_manager

load_dotenv()

class ForesightEngine:
    """
    RAG Pipeline for question prediction.
    Combines Previous Year Questions + Recent Current Affairs
    to generate probability-scored question predictions.
    """
    
    def __init__(self):
        self.api_key = os.environ.get('GEMINI_API_KEY')
        if not self.api_key:
            print("⚠️ ForesightEngine Warning: GEMINI_API_KEY not found")
        elif model_manager.is_configured:
            print("🔮 ForesightEngine Online: Oracle Activated via ModelManager")
        else:
            print("❌ ForesightEngine Error: ModelManager not configured")
    
    def predict_questions(
        self, 
        subject: str = "All", 
        timeframe_days: int = 90,
        topic: str = None
    ) -> List[Dict]:
        """
        Generate predicted questions based on recent trends.
        
        Args:
            subject: Target subject (e.g., "Polity", "Geography")
            timeframe_days: Look back period for current affairs
            topic: Specific topic to focus on (optional)
            
        Returns:
            List of predictions with probability scores
        """
        if not model_manager.is_configured:
            return []
        
        # 1. Gather PYQ patterns
        pyq_patterns = self._analyze_pyq_patterns(subject)
        
        # 2. Gather recent current affairs
        current_affairs = self._get_recent_affairs(timeframe_days)
        
        # 3. Generate predictions using AI
        predictions = self._generate_predictions(
            subject, 
            pyq_patterns, 
            current_affairs,
            topic=topic
        )
        
        # 4. Save predictions to DB
        for pred in predictions:
            try:
                save_foresight_prediction(pred)
            except Exception as e:
                print(f"Failed to save prediction: {e}")

        return predictions
    
    def _analyze_pyq_patterns(self, subject: str) -> str:
        """Analyze historical PYQ patterns using raw SQL"""
        try:
            from app.db import get_db
            conn = get_db()
            
            # Get recent PYQs (last 5 years)
            query = "SELECT topic, subject FROM pyq_questions WHERE year >= 2019"
            params = []
            
            if subject != "All":
                query += " AND subject LIKE ?"
                params.append(f"%{subject}%")
            
            questions = conn.execute(query, params).fetchall()
            
            # Extract topics
            topics = {}
            for q in questions:
                topic = q['topic'] or "General"
                topics[topic] = topics.get(topic, 0) + 1
            
            # Format as analysis
            pattern_summary = "PYQ Topic Frequency:\n"
            for topic, count in sorted(topics.items(), key=lambda x: x[1], reverse=True)[:10]:
                pattern_summary += f"- {topic}: {count} questions\n"
            
            return pattern_summary
            
        except Exception as e:
            print(f"PYQ Analysis Error: {e}")
            return "No PYQ data available"
    
    def _get_recent_affairs(self, days: int) -> str:
        """Get recent current affairs with Momentum Analysis"""
        try:
            from app.db import get_db
            conn = get_db()
            
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            query = """
                SELECT title, upsc_summary, tags 
                FROM current_affairs 
                WHERE published_date >= ? 
                ORDER BY published_date DESC 
                LIMIT 50
            """
            
            articles = conn.execute(query, (cutoff_date,)).fetchall()
            
            if not articles:
                return "No recent current affairs data"
            
            # Momentum Analysis (Keyword Frequency)
            keywords = {}
            affairs_summary = "Recent Current Affairs & Momentum:\n"
            
            for article in articles:
                # Simple keyword extraction from title
                words = article['title'].split()
                for w in words:
                    if len(w) > 4:
                        keywords[w] = keywords.get(w, 0) + 1
            
            # Top Momentum Keywords
            top_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:5]
            affairs_summary += f"🔥 High Momentum Topics: {', '.join([k[0] for k in top_keywords])}\n\n"
            
            for article in articles[:20]:
                affairs_summary += f"- {article['title']}\n"
                if article['upsc_summary']:
                    affairs_summary += f"  Summary: {article['upsc_summary'][:100]}...\n"
            
            return affairs_summary
            
        except Exception as e:
            print(f"Current Affairs Error: {e}")
            return "No current affairs data available"

    def _critic_review(self, candidates: List[Dict]) -> List[Dict]:
        """
        The Devil's Advocate:
        Critiques candidates for Ambiguity, Relevance, and Difficulty.
        Filters out weak questions.
        """
        if not candidates:
            return []
            
        prompt = f"""
        You are the 'Devil's Advocate', a ruthless UPSC Examiner.
        Review these {len(candidates)} candidate questions.
        
        CRITERIA FOR SELECTION:
        1. **Ambiguity**: Is the question clear? (Reject if vague)
        2. **Difficulty**: Is it too easy? (Reject if trivial)
        3. **Relevance**: Is it actually examinable? (Reject if niche/irrelevant)
        4. **Structure**: Does it follow UPSC format? (Multi-statement preferred)
        
        CANDIDATES:
        {json.dumps(candidates, indent=2)}
        
        TASK:
        Select the Top 10 questions that strictly meet the criteria.
        Refine their wording if necessary to increase difficulty.
        
        OUTPUT FORMAT (JSON Array):
        [
            {{
                "question": "Refined Question...",
                "type": "MCQ",
                "probability": 0.9,
                "reasoning": "Strong correlation with [Topic]",
                "subject": "Polity",
                "topic": "Fundamental Rights",
                "preparation_tip": "Study [Source]"
            }}
        ]
        """
        
        try:
            response = model_manager.generate_content(prompt, model_type='pro')
            text = response.text.strip()
            json_match = re.search(r'\[.*\]', text, re.DOTALL)
            
            if json_match:
                refined = json.loads(json_match.group(0))
                return refined
            else:
                print("Critic failed to return JSON, returning originals")
                return candidates[:10]
                
        except Exception as e:
            print(f"Critic Error: {e}")
            return candidates[:10]

    def _get_saved_favorites(self) -> List[Dict]:
        """Fetch user's favorite predictions to use as few-shot examples"""
        try:
            from app.db import get_db
            conn = get_db()
            # Check if table exists first
            table_check = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='foresight_predictions'").fetchone()
            if not table_check:
                return []
                
            rows = conn.execute('SELECT question, type, reasoning FROM foresight_predictions WHERE is_favorite = 1 ORDER BY id DESC LIMIT 3').fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error fetching favorites: {e}")
            return []

    def _get_weak_areas(self) -> str:
        """Get user's weak areas to prioritize in predictions"""
        try:
            from app.services.weak_area_service import WeakAreaAnalyzer
            # Default user_id=1 for now
            weak_areas = WeakAreaAnalyzer.analyze_user_performance(user_id=1, days=30)
            
            if not weak_areas:
                return "No specific weak areas identified."
                
            summary = "USER WEAK AREAS (PRIORITIZE THESE TOPICS):\n"
            for area in weak_areas[:5]:
                summary += f"- {area['topic']} ({area['subject']}) - Accuracy: {area['accuracy_rate']}%\n"
            return summary
        except Exception as e:
            print(f"Weak Area Fetch Error: {e}")
            return ""

    def _generate_predictions(
        self, 
        subject: str, 
        pyq_patterns: str, 
        current_affairs: str,
        topic: str = None
    ) -> List[Dict]:
        """Use AI to generate question predictions with Critic Loop"""
        
        favorites = self._get_saved_favorites()
        weak_areas = self._get_weak_areas()
        
        # Format weak areas text
        weak_area_text = ""
        if weak_areas:
            weak_area_text = f"\n\nUSER WEAK AREAS (PRIORITIZE THESE TOPICS):\n" + weak_areas

        # Format favorites text
        examples_text = ""
        if favorites:
            examples_text = "\n\nEXAMPLES OF HIGH-QUALITY PREDICTIONS (MIMIC THIS STYLE):\n"
            for fav in favorites:
                examples_text += f"- Q: {fav['question']}\n  Type: {fav['type']}\n  Reasoning: {fav['reasoning']}\n"

        topic_directive = f"TOPIC FOCUS: {topic}" if topic else ""

        # Phase 1: Generator (High Creativity)
        prompt = f"""
        You are Project Foresight - a predictive oracle for UPSC exam questions.
        
        SUBJECT FOCUS: {subject}
        {topic_directive}
        
        HISTORICAL PATTERNS (PYQs):
        {pyq_patterns}
        
        RECENT CURRENT AFFAIRS:
        {current_affairs}
        
        {weak_area_text}
        
        {examples_text}
        
        Generate 20 CANDIDATE questions for UPSC Prelims/Mains.
        Focus on "Interdisciplinary" questions (e.g., Economy + Environment).
        Prioritize topics listed in USER WEAK AREAS.
        If a specific TOPIC FOCUS is provided, ensure at least 50% of questions relate to it.
        
        OUTPUT FORMAT (JSON Array):
        [
            {{
                "question": "...",
                "type": "MCQ",
                "probability": 0.8,
                "reasoning": "...",
                "subject": "...",
                "topic": "...",
                "preparation_tip": "...",
                "source_citation": "The Hindu (24th Nov) / NCERT Class XI"
            }}
        ]
        """
        
        try:
            # Predictions require deep analysis
            response = model_manager.generate_content(prompt, model_type='pro')
            
            text = response.text.strip()
            json_match = re.search(r'\[.*\]', text, re.DOTALL)
            
            if json_match:
                candidates = json.loads(json_match.group(0))
                
                # Phase 2: The Critic (High Rigor)
                final_predictions = self._critic_review(candidates)
                
                # Add metadata
                for pred in final_predictions:
                    pred['generated_at'] = datetime.now().isoformat()
                    pred['id'] = hash(pred['question']) % 10000
                
                return final_predictions
            else:
                print("No JSON found in response")
                return []
                
        except Exception as e:
            print(f"Prediction Generation Error: {e}")
            import traceback
            traceback.print_exc()
            return []

# Singleton instance
foresight_engine = ForesightEngine()
