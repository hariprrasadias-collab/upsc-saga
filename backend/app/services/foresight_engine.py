"""
Project Foresight - Predictive Question Engine
Analyzes PYQs and current affairs to predict probable future questions
"""

from typing import List, Dict
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
        # Config managed by model_manager
        pass
    
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
        print(f"Foresight: Saving {len(predictions)} predictions...")
        for pred in predictions:
            try:
                # Ensure fields exist
                pred.setdefault('subject', subject)
                pred.setdefault('topic', topic or "General")
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
        # MISSION: THE RUTHLESS SELECTION (DEVIL'S ADVOCATE)
        **Role:** Chief UPSC Examiner (Retired).
        **Task:** Filter and Polish these {len(candidates)} raw predictions.
        
        **CANDIDATES:**
        {json.dumps(candidates, indent=2)}
        
        **CRITERIA:**
        1. **Kill the Trivial:** If a Google search answers it in 1 second, DELETE IT.
        2. **Fix the Vague:** "What is democracy?" -> "Critically analyze the role of 'Constitutional Morality' in sustaining Indian Democracy."
        3. **Interdisciplinary:** Prioritize questions connecting multiple subjects (e.g., Environment + IR).
        4. **Black Swans:** Keep 2 "Wildcard" questions that are low probability but high impact.
        
        **OUTPUT SCHEMA (JSON):**
        [
            {{
                "question": "Refined Question (Multi-statement/Analytical)",
                "type": "MCQ" or "Mains",
                "probability": 0.1 to 0.9,
                "reasoning": "Why this? (e.g., 'Matches 2023 Trend of randomized options')",
                "subject": "Core Subject",
                "topic": "Sub-topic",
                "preparation_tip": "Specific source (e.g., 'ARC Report 2, Chapter 4')"
            }}
        ]
        """
        
        try:
            # Use FAST model for critique to save quota and speed up the loop
            response = model_manager.generate_content(prompt, model_type='fast')
            text = response.text.strip()

            if "Oracle is silent" in text:
                return candidates[:10]

            # Clean Markdown if present
            if text.startswith("```"):
                text = text.replace("```json", "").replace("```", "").strip()

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
        # MISSION: PREDICT THE FUTURE (PROJECT FORESIGHT)
        **Role:** An AI Oracle analyzing patterns in the chaos.
        
        **CONTEXT:**
        - **Subject:** {subject}
        - **Focus:** {topic_directive}
        - **Weaknesses:** {weak_area_text}
        - **PYQ Patterns:** {pyq_patterns}
        - **News:** {current_affairs}
        
        **DIRECTIVE:**
        Generate 20 "Black Swan" Candidate Questions.
        - **Avoid Obviousness:** No "Who is the President?" questions.
        - **Target:** "Grey Areas" where static syllabus meets dynamic current events.
        - **Structure:**
          - 50% Conceptual (Deep Theory).
          - 30% Applied (Current Affairs Linkage).
          - 20% "Bouncer" (Unexpected interdisciplinary connections).
        
        **OUTPUT SCHEMA (JSON):**
        [
            {{
                "question": "The Raw Question Candidate",
                "type": "MCQ" or "Mains",
                "probability": 0.7,
                "reasoning": "Derived from Pattern X + News Y",
                "subject": "Primary Subject",
                "topic": "Specific Topic",
                "preparation_tip": "Read X to solve this",
                "source_citation": "The Hindu / Yojana / NCERT"
            }}
        ]
        """
        
        try:
            # Predictions require deep analysis
            response = model_manager.generate_content(prompt, model_type='pro', max_output_tokens=4096)
            
            text = response.text.strip()
            
            # Clean Markdown
            if text.startswith("```"):
                text = text.replace("```json", "").replace("```", "").strip()

            print(f"DEBUG FORESIGHT RAW TEXT: {text[:200]}...")

            if "Oracle is silent" in text:
                return []

            # Robust JSON Extractor (Find first [ and last ])
            try:
                start = text.find('[')
                end = text.rfind(']')
                
                if start != -1 and end != -1 and end > start:
                    json_str = text[start : end + 1]
                    candidates = json.loads(json_str)
                    
                    # Phase 2: The Critic (High Rigor)
                    final_predictions = self._critic_review(candidates)

                    # Add metadata
                    for pred in final_predictions:
                        pred['generated_at'] = datetime.now().isoformat()
                        pred['id'] = hash(pred['question']) % 10000

                    return final_predictions
                else:
                    print("No JSON array found (brackets missing)")
                    return []
            except json.JSONDecodeError as e:
                print(f"JSON Decode Failed: {e}")
                return []
            except Exception as e:
                print(f"Extraction Error: {e}")
                return []

        except Exception as e:
            print(f"Prediction Generation Error: {e}")
            import traceback
            traceback.print_exc()
            return []

# Singleton instance
foresight_engine = ForesightEngine()
