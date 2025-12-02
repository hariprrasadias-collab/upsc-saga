"""
Project Foresight - Predictive Question Engine
Analyzes PYQs and current affairs to predict probable future questions
"""

from typing import List, Dict
import google.generativeai as genai
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

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
            self.model = None
        else:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-pro-latest')
                print("🔮 ForesightEngine Online: Oracle Activated")
            except Exception as e:
                print(f"❌ ForesightEngine Error: {e}")
                self.model = None
    
    def predict_questions(
        self, 
        subject: str = "All", 
        timeframe_days: int = 90
    ) -> List[Dict]:
        """
        Generate predicted questions based on recent trends.
        
        Args:
            subject: Target subject (e.g., "Polity", "Geography")
            timeframe_days: Look back period for current affairs
            
        Returns:
            List of predictions with probability scores
        """
        if not self.model:
            return []
        
        # 1. Gather PYQ patterns
        pyq_patterns = self._analyze_pyq_patterns(subject)
        
        # 2. Gather recent current affairs
        current_affairs = self._get_recent_affairs(timeframe_days)
        
        # 3. Generate predictions using AI
        predictions = self._generate_predictions(
            subject, 
            pyq_patterns, 
            current_affairs
        )
        
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
        """Get recent current affairs from Ravens using raw SQL"""
        try:
            from app.db import get_db
            conn = get_db()
            
            # Calculate cutoff date
            # SQLite doesn't have easy date math in all versions, so we do it in Python
            # Assuming published_date is stored as string YYYY-MM-DD
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            query = """
                SELECT title, upsc_summary 
                FROM current_affairs 
                WHERE published_date >= ? 
                ORDER BY published_date DESC 
                LIMIT 20
            """
            
            articles = conn.execute(query, (cutoff_date,)).fetchall()
            
            if not articles:
                return "No recent current affairs data"
            
            affairs_summary = "Recent Current Affairs (Top 20):\n"
            for article in articles:
                affairs_summary += f"- {article['title']}\n"
                if article['upsc_summary']:
                    affairs_summary += f"  Summary: {article['upsc_summary'][:100]}...\n"
            
            return affairs_summary
            
        except Exception as e:
            print(f"Current Affairs Error: {e}")
            return "No current affairs data available"
    
    def _generate_predictions(
        self, 
        subject: str, 
        pyq_patterns: str, 
        current_affairs: str
    ) -> List[Dict]:
        """Use AI to generate question predictions"""
        
        prompt = f"""
        You are Project Foresight - a predictive oracle for UPSC exam questions.
        
        SUBJECT FOCUS: {subject}
        
        HISTORICAL PATTERNS (PYQs):
        {pyq_patterns}
        
        RECENT CURRENT AFFAIRS:
        {current_affairs}
        
        Based on the above data, predict 10 most probable questions for UPSC Prelims/Mains.
        
        For each prediction:
        1. Formulate a realistic UPSC-style question
        2. Assign a probability score (0.0 to 1.0)
        3. Provide brief reasoning
        4. Suggest preparation strategy
        
        OUTPUT FORMAT (JSON Array):
        [
            {{
                "question": "Which of the following statements...",
                "type": "MCQ" or "Essay",
                "probability": 0.85,
                "reasoning": "This topic appeared 3 times in PYQs and has recent policy changes",
                "subject": "Polity",
                "topic": "Fundamental Rights",
                "preparation_tip": "Focus on recent amendments and landmark judgments"
            }}
        ]
        
        Return ONLY the JSON array, no additional text.
        """
        
        try:
            response = self.model.generate_content(prompt)
            
            # Parse JSON response
            import json
            import re
            
            text = response.text.strip()
            
            # Extract JSON array
            json_match = re.search(r'\[.*\]', text, re.DOTALL)
            if json_match:
                predictions = json.loads(json_match.group(0))
                
                # Add metadata
                for pred in predictions:
                    pred['generated_at'] = datetime.now().isoformat()
                    pred['id'] = hash(pred['question']) % 10000
                
                return predictions
            else:
                print("Failed to parse predictions JSON")
                return []
                
        except Exception as e:
            print(f"Prediction Generation Error: {e}")
            import traceback
            traceback.print_exc()
            return []

# Singleton instance
foresight_engine = ForesightEngine()
