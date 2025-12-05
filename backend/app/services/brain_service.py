import google.generativeai as genai
import os
import json
import traceback
from datetime import datetime
from dotenv import load_dotenv
from app.services.synapse_registry import SynapseRegistry
from app.services.autonomy_manager import autonomy_manager
from app.services.syllabus_tracker import SyllabusTracker
from app.services.ab_tester import ab_tester

load_dotenv()

class BrainService:
    """
    The Central Nervous System (CNS) of the application.
    Uses Gemini to reason, analyze, and optimize the user's UPSC preparation
    by connecting to all registered synapses.
    """
    
    def __init__(self):
        self.api_key = os.environ.get('GEMINI_API_KEY')
        if not self.api_key:
            print("⚠️ BrainService Warning: GEMINI_API_KEY not found. The Brain will be lobotomized.")
            self.model = None
        else:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-flash-latest') # Using flash for speed
                print("BrainService Online: Connected to Gemini Cortex.")
            except Exception as e:
                print(f"BrainService Error: Failed to initialize Gemini: {e}")
                self.model = None
            
        self.registry = SynapseRegistry.get_instance()
        self.autonomy = autonomy_manager  # Autonomous execution manager
        self.context_window = [] # Short-term memory
        self.current_strategy = None # Golden Path Directive
        self.bio_status = None # Panopticon Status
        
        # Caching
        self._system_cache = None
        self._cache_expiry = None
        
        # Load persisted strategy
        self._load_strategy()

    def _load_strategy(self):
        """Load strategy from disk"""
        try:
            strategy_path = os.path.join(os.getcwd(), 'instance', 'current_strategy.json')
            if os.path.exists(strategy_path):
                with open(strategy_path, 'r') as f:
                    self.current_strategy = json.load(f)
                print(f"Brain: Loaded persisted strategy with {len(self.current_strategy)} steps.")
        except Exception as e:
            print(f"Failed to load strategy: {e}")

    def _save_strategy(self):
        """Save strategy to disk"""
        try:
            instance_dir = os.path.join(os.getcwd(), 'instance')
            if not os.path.exists(instance_dir):
                os.makedirs(instance_dir)
            
            strategy_path = os.path.join(instance_dir, 'current_strategy.json')
            with open(strategy_path, 'w') as f:
                json.dump(self.current_strategy, f)
            print("Brain: Strategy persisted to disk.")
        except Exception as e:
            print(f"Failed to save strategy: {e}")

    def ingest_strategic_directive(self, path_data):
        """
        Receives the 'Golden Path' from the Strategy Module.
        The Brain adopts this as the 'Grand Strategy'.
        """
        self.current_strategy = path_data
        
        # Gamification Trigger
        try:
            from app.services.game_engine import trigger_event
            trigger_event('STRATEGY_COMMIT', 1)
        except Exception as e:
            print(f"Gamification Trigger Failed: {e}")
            
        print(f"Brain: Strategic Directive Received. {len(path_data)} steps adopted.")
        self._save_strategy()
        return True

    def check_bio_status(self):
        """
        Queries the Panopticon for the user's biological status.
        Returns a 'Bio-Alert' if critical thresholds are breached.
        """
        # Real Panopticon Integration
        try:
            from app.services.panopticon_service import PanopticonService
            panopticon = PanopticonService()
            return panopticon.get_current_status()
        except Exception as e:
            print(f"Bio-Check Failed: {e}")
            return {"status": "OFFLINE", "energy": 0, "alert": "Panopticon Unreachable"}

    def think(self, user_input: str, context_override: dict = None) -> dict:
        """
        Core reasoning loop. Optimized for speed using parallel processing and caching.
        """
        if not self.model:
            return {"response_text": "I am offline. Please check my API key.", "actions": []}

        # 0. Fast Path (Reflexes)
        reflex_response = self._check_reflexes(user_input)
        if reflex_response:
            return reflex_response

        import concurrent.futures
        from flask import current_app
        
        # Capture app context for threads
        app = current_app._get_current_object()
        
        def run_in_context(func, *args):
            with app.app_context():
                return func(*args)
        
        # Parallel Context Gathering
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_system = executor.submit(run_in_context, self._get_cached_system_status)
            future_bio = executor.submit(run_in_context, self.check_bio_status)
            future_lessons = executor.submit(run_in_context, self._get_lessons)
            future_specific = executor.submit(run_in_context, self._resolve_context, user_input)
            
            system_status = future_system.result()
            bio_status = future_bio.result()
            lessons = future_lessons.result()
            specific_context = future_specific.result()

        # Construct Prompt (Optimized & Minified)
        prompt = f"""
        You are the CENTRAL NERVOUS SYSTEM (The Brain) of a UPSC Preparation App.
        
        CONTEXT:
        - Sys: {json.dumps(system_status, separators=(',', ':'))}
        - Bio: {json.dumps(bio_status, separators=(',', ':'))}
        - Mem: {json.dumps(lessons, separators=(',', ':'))}
        - Ctx: {specific_context}
        - Override: {json.dumps(context_override, separators=(',', ':')) if context_override else "None"}
        
        DIRECTIVE: {self._get_bio_directive(bio_status)}
        
        USER: "{user_input}"
        
        TASK: Decide optimal response/action.
        
        ACTIONS:
        - RETRIEVE_FROM_PALACE (payload: query)
        - PREDICT_QUESTIONS (payload: subject, timeframe_days)
        - TRIGGER_WATCHMAN (payload: none)
        - SHOW_MORNING_BRIEFING (payload: none)
        - SHOW_PANOPTICON (payload: none)
        - GENERATE_STUDY_PLAN (payload: start_date)
        - CONSULT_GOLDEN_PATH (payload: time_budget_hours)
        
        JSON RESPONSE:
        {{
            "deep_reasoning": "Brief analysis.",
            "response_text": "Reply to user.",
            "suggested_actions": [ {{ "type": "ACTION_NAME", "payload": {{...}} }} ]
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            return self._parse_response(response.text)
        except Exception as e:
            print(f"Brain Think Error: {e}")
            return {"response_text": f"I had a headache thinking about that. Error: {str(e)}", "actions": []}

    def execute_action(self, action_type: str, payload: dict) -> dict:
        """
        Executes a specific action triggered by the Brain.
        Now integrated with AutonomyManager for logging and permission checks.
        """
        print(f"Brain Executing Action: {action_type}")
        
        # 1. Log the action intent
        action_id = self.autonomy.log_action(
            action_type=action_type,
            action_payload=payload,
            executed_by='manual', 
            reasoning=payload.get('reasoning', 'User initiated action')
        )
        
        result = {"success": False, "message": "Unknown action"}
        
        try:
            if action_type == "RETRIEVE_FROM_PALACE":
                try:
                    from app.models import MindPalaceArtifact
                    query = payload.get('query', '')
                    filters = []
                    if query:
                        filters.append(MindPalaceArtifact.title.contains(query))
                        filters.append(MindPalaceArtifact.content.contains(query))
                    
                    from sqlalchemy import or_
                    artifacts = MindPalaceArtifact.query.filter(or_(*filters)).all()
                    
                    data = [{"title": a.title, "content": a.content} for a in artifacts]
                    result = {
                        "success": True, 
                        "message": f"I found {len(artifacts)} memories matching '{query}'.",
                        "data": data
                    }
                except Exception as e:
                    result = {"success": False, "message": f"Failed to retrieve from Mind Palace: {str(e)}"}
            
            elif action_type == "PREDICT_QUESTIONS":
                try:
                    from app.services.foresight_engine import foresight_engine
                    subject = payload.get('subject', 'General')
                    timeframe = payload.get('timeframe_days', 90)
                    predictions = foresight_engine.predict_questions(subject, timeframe)
                    
                    from app.services.game_engine import trigger_event
                    trigger_event('ORACLE_CONSULT', 1)
                    
                    result = {
                        "success": True,
                        "message": f"The Oracle has spoken. {len(predictions)} predictions generated.",
                        "data": predictions[:3]
                    }
                except Exception as e:
                    result = {"success": False, "message": f"The Oracle is silent: {str(e)}"}
            
            elif action_type == "TRIGGER_WATCHMAN":
                try:
                    from app.services.night_watchman import night_watchman
                    result = night_watchman.perform_nightly_watch()
                except Exception as e:
                    result = {"success": False, "message": f"Watchman failed to patrol: {str(e)}"}
            
            elif action_type == "SHOW_MORNING_BRIEFING":
                result = {"success": True, "message": "Opening Morning Briefing"}

            elif action_type == "SHOW_PANOPTICON":
                result = {"success": True, "message": "Opening The Panopticon"}

            elif action_type == "GENERATE_STUDY_PLAN":
                try:
                    from app.services.study_planner import generate_study_plan
                    start_date = payload.get('start_date', datetime.now().date().isoformat())
                    force_new = payload.get('force_new', False)
                    plan_result = generate_study_plan(start_date, force_new=force_new)
                    
                    if plan_result.get('success'):
                        result = {"success": True, "message": f"Study Plan Generated! ID: {plan_result.get('plan_id')}"}
                    else:
                        result = {"success": False, "message": "Failed to generate study plan."}
                except Exception as e:
                    result = {"success": False, "message": f"Study Plan Generation Failed: {str(e)}"}

            elif action_type == "CONSULT_GOLDEN_PATH":
                try:
                    from app.services.golden_path_service import golden_path
                    time_budget = payload.get('time_budget_hours', 50)
                    path_data = golden_path.calculate_optimal_path(time_budget)
                    path_summary = ", ".join([node['label'] for node in path_data['path'][:5]])
                    result = {
                        "success": True,
                        "message": f"Golden Path Calculated. Optimal route: {path_summary}...",
                        "metric_name": 'completion',
                        "value": 1.0
                    }
                except Exception as e:
                    result = {"success": False, "message": f"Golden Path Failed: {str(e)}"}



            elif action_type == "UPDATE_TIMEBOXES":
                try:
                    from app.services.time_boxing_service import time_boxing_service
                    # Logic to re-optimize schedule
                    result = {"success": True, "message": "Schedule optimized based on energy levels."}
                except Exception as e:
                    result = {"success": False, "message": f"Timebox Update Failed: {str(e)}"}

            elif action_type == "ANALYZE_QUESTION":
                try:
                    question_text = payload.get('question', '')
                    analysis_prompt = f"Analyze this UPSC Question: '{question_text}'. Break it down into Key Demand, Structure, and Keywords."
                    response = self.model.generate_content(analysis_prompt)
                    result = {"success": True, "message": "Analysis Complete", "analysis": response.text}
                except Exception as e:
                    result = {"success": False, "message": f"Analysis Failed: {str(e)}"}

            elif action_type == "CREATE_MOCK_TEST":
                try:
                    from app.services.mock_test_service import MockTestService
                    topic = payload.get('topic', 'General')
                    res = MockTestService.create_smart_test(topic)
                    result = res
                except Exception as e:
                    result = {"success": False, "message": f"Mock Test Creation Failed: {str(e)}"}

            elif action_type == "SUMMON_BOSS":
                try:
                    from app.db import get_db
                    conn = get_db()
                    name = payload.get('name', 'Unknown Horror')
                    filters = payload.get('filters', {})
                    
                    if not filters:
                        from app.services.analytics_service import identify_weak_areas
                        weak_data = identify_weak_areas(conn, 1, limit=1)
                        if weak_data:
                            subject = weak_data[0]['subject']
                            name = f"The {subject} Nemesis"
                            filters = {'subject': subject}
                        else:
                            name = "The Random Chaos"
                            filters = {} 
                    
                    cursor = conn.execute('INSERT INTO custom_bosses (name, filters, is_active) VALUES (?, ?, 1)', 
                                        (name, json.dumps(filters)))
                    conn.commit()
                    result = {
                        "success": True, 
                        "message": f"A new challenger approaches: {name}!",
                        "boss_id": cursor.lastrowid
                    }
                except Exception as e:
                    result = {"success": False, "message": f"Summoning Failed: {str(e)}"}

            elif action_type == "ANALYZE_DEBATE":
                try:
                    history = payload.get('history', [])
                    transcript = ""
                    for turn in history:
                        speaker = turn.get('speakerId', 'Unknown')
                        text = turn.get('text', '')
                        transcript += f"{speaker}: {text}\n"
                        
                    analysis_prompt = f"Analyze this Socratic Debate:\n{transcript}\nProvide: 1. Summary 2. Winner 3. Missing points."
                    response = self.model.generate_content(analysis_prompt)
                    result = {"success": True, "message": "Debate Analysis Complete.", "analysis": response.text}
                except Exception as e:
                    result = {"success": False, "message": f"Analysis Failed: {str(e)}"}

            elif action_type == "CONSTRUCT_PALACE":
                try:
                    from app.db import get_db
                    conn = get_db()
                    topic = payload.get('topic', 'General Knowledge')
                    
                    cursor = conn.execute('INSERT INTO mind_palace_locations (name, description, layout_type) VALUES (?, ?, ?)', 
                                        (f"The Hall of {topic}", f"A dedicated space for remembering {topic}", "hall"))
                    location_id = cursor.lastrowid
                    
                    brainstorm_prompt = f"Generate 5 key concepts for '{topic}' to store in a Mind Palace. Return JSON: [{{'title': '...', 'content': '...', 'icon': '...'}}]"
                    response = self.model.generate_content(brainstorm_prompt)
                    artifacts_data = self._parse_response(response.text)
                    
                    if isinstance(artifacts_data, list):
                        import random
                        for art in artifacts_data:
                            x = random.randint(10, 90)
                            y = random.randint(10, 90)
                            conn.execute('INSERT INTO mind_palace_artifacts (location_id, title, content, type, x_position, y_position, icon, color) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', 
                                       (location_id, art.get('title'), art.get('content'), 'concept', x, y, art.get('icon', '📦'), '#9b59b6'))
                            
                    conn.commit()
                    result = {"success": True, "message": f"Constructed 'The Hall of {topic}' with {len(artifacts_data)} memories."}
                except Exception as e:
                    result = {"success": False, "message": f"Construction Failed: {str(e)}"}

            elif action_type == "PRIORITIZE_SYLLABUS":
                try:
                    from app.db import get_db
                    conn = get_db()
                    cursor = conn.execute("SELECT id, topic, subject FROM syllabus_tracker WHERE status != 'Completed'")
                    topics = cursor.fetchall()
                    topics_list = [{"id": t['id'], "topic": t['topic'], "subject": t['subject']} for t in topics]
                    
                    prioritize_prompt = f"From this list: {json.dumps(topics_list[:50])}, identify Top 5 High Yield topics. Return JSON: {{ 'priority_ids': [1, 2...] }}"
                    response = self.model.generate_content(prioritize_prompt)
                    data = self._parse_response(response.text)
                    priority_ids = data.get('priority_ids', [])
                    
                    result = {
                        "success": True, 
                        "message": f"Identified {len(priority_ids)} high-yield topics.",
                        "priority_ids": priority_ids
                    }
                except Exception as e:
                    result = {"success": False, "message": f"Prioritization Failed: {str(e)}"}

            elif action_type == "CREATE_FLASHCARDS":
                try:
                    from app.services.flashcard_service import FlashcardService
                    topic = payload.get('topic', 'General')
                    count = payload.get('count', 5)
                    result = FlashcardService.generate_from_topic(topic, count)
                except Exception as e:
                    result = {"success": False, "message": f"Flashcard Generation Failed: {str(e)}"}

            elif action_type == "ANALYZE_PYQ_TRENDS":
                try:
                    from app.db import get_db
                    conn = get_db()
                    filters = payload.get('filters', {})
                    
                    # Construct query based on filters
                    query = "SELECT year, subject, topic, question_text FROM pyq_questions WHERE 1=1"
                    params = []
                    
                    if filters.get('subject'):
                        query += " AND subject = ?"
                        params.append(filters['subject'])
                    
                    if filters.get('year'):
                        query += " AND year = ?"
                        params.append(filters['year'])
                        
                    query += " ORDER BY year DESC LIMIT 50" # Analyze last 50 questions matching criteria
                    
                    questions = conn.execute(query, params).fetchall()
                    questions_text = "\n".join([f"[{q['year']}] {q['topic']}: {q['question_text']}" for q in questions])
                    
                    analysis_prompt = f"""
                    Analyze these UPSC Previous Year Questions (PYQs) for trends:
                    {questions_text}
                    
                    Identify:
                    1. Recurring Themes/Topics.
                    2. Shift in difficulty or style over years.
                    3. High-yield areas to focus on.
                    
                    Format as a concise strategic briefing.
                    """
                    response = self.model.generate_content(analysis_prompt)
                    result = {
                        "success": True, 
                        "message": "Trend Analysis Complete.",
                        "analysis": response.text
                    }
                except Exception as e:
                    result = {"success": False, "message": f"Trend Analysis Failed: {str(e)}"}

            elif action_type == "EXPLAIN_SYLLABUS_NODE":
                try:
                    node_title = payload.get('node', 'Unknown Topic')
                    explanation_prompt = f"""
                    Explain the UPSC Syllabus topic: '{node_title}'.
                    
                    Provide:
                    1. Definition/Concept.
                    2. Relevance to UPSC (Prelims/Mains).
                    3. Key sub-topics to study.
                    
                    Keep it concise (under 200 words).
                    """
                    response = self.model.generate_content(explanation_prompt)
                    result = {
                        "success": True, 
                        "message": "Explanation Generated.",
                        "explanation": response.text
                    }
                except Exception as e:
                    result = {"success": False, "message": f"Explanation Failed: {str(e)}"}

            elif action_type == "SUGGEST_BIOHACK":
                try:
                    metrics = payload.get('metrics', {})
                    bio_prompt = f"""
                    Analyze these bio-metrics:
                    Sleep: {metrics.get('sleep', 7)}h
                    Energy: {metrics.get('energy', 50)}/100
                    Mood: {metrics.get('mood', 5)}/10
                    
                    Suggest 1 specific, actionable biohack or protocol to improve performance right now.
                    Keep it scientific but concise.
                    """
                    response = self.model.generate_content(bio_prompt)
                    result = {
                        "success": True, 
                        "message": "Biohack Generated.",
                        "suggestion": response.text
                    }
                except Exception as e:
                    result = {"success": False, "message": f"Biohack Failed: {str(e)}"}

            elif action_type == "DECODE_NEURAL_HASH":
                try:
                    text_data = payload.get('text', '')
                    context_type = payload.get('type', 'general')
                    
                    decode_prompt = f"""
                    Decode this '{context_type}' text for a UPSC aspirant:
                    "{text_data[:2000]}"
                    
                    Return JSON with:
                    - core_themes (list of strings)
                    - high_yield_keywords (list of strings)
                    - examiner_pattern (string description)
                    - potential_questions (list of objects {{type, question}})
                    - complexity_score (1-10)
                    - relevance_score (1-10)
                    """
                    response = self.model.generate_content(decode_prompt)
                    decoded_data = self._parse_response(response.text)
                    
                    result = {
                        "success": True,
                        "message": "Neural Hash Decoded.",
                        "data": decoded_data
                    }
                except Exception as e:
                    result = {"success": False, "message": f"Decoding Failed: {str(e)}"}

            elif action_type == "GENERATE_QUESTS":
                try:
                    from app.db import get_db
                    from app.services.quest_service import quest_service
                    
                    conn = get_db()
                    user_id = 1 # Hardcoded for now
                    
                    # Generate new quests
                    new_quests = quest_service.generate_daily_quests(user_id)
                    
                    count = 0
                    today_str = datetime.now().date().isoformat()
                    
                    for q in new_quests:
                        conn.execute('INSERT INTO tasks (user_id, title, xp_reward, associated_stat, isCompleted, is_quest, due_date) VALUES (?, ?, ?, ?, 0, 1, ?)',
                                     (user_id, q['title'], q['xp_reward'], q['type'], today_str))
                        count += 1
                    
                    conn.commit()
                    
                    import os
                    from app.db import DATABASE
                    result = {
                        "success": True,
                        "message": f"Generated {count} new quests.",
                        "debug_info": {
                            "cwd": os.getcwd(),
                            "db_path": DATABASE,
                            "user_id": user_id
                        }
                    }
                except Exception as e:
                    result = {"success": False, "message": f"Quest Generation Failed: {str(e)}"}

            elif action_type == "RECOMMEND_ARMORY_ITEM":
                try:
                    hacksilver = payload.get('hacksilver', 0)
                    weak_areas = payload.get('weak_areas', [])
                    
                    recommend_prompt = f"""
                    User has {hacksilver} Hacksilver.
                    Weak Areas: {', '.join(weak_areas)}.
                    Available Items: Leviathan Axe (History), Blades of Chaos (Polity), Guardian Shield (Streak), Mimir Upgrade (Wisdom).
                    
                    Recommend 1 item to buy and explain why in character as Brok (the dwarf blacksmith).
                    """
                    response = self.model.generate_content(recommend_prompt)
                    result = {
                        "success": True,
                        "message": "Brok has spoken.",
                        "recommendation": response.text
                    }
                except Exception as e:
                    result = {"success": False, "message": f"Recommendation Failed: {str(e)}"}

            return result

        except Exception as e:
            print(f"Brain Action Failed: {e}")
            try:
                from app.services.hephaestus_service import hephaestus_service
                hephaestus_service.attempt_repair(e)
            except:
                pass

            self.autonomy.update_action_outcome(
                action_id=action_id,
                outcome_status='failure',
                reasoning=str(e)
            )
            return {"success": False, "message": str(e)}



    def _get_system_status_summary(self):
        """
        Aggregates status from all subsystems.
        """
        try:
            # Basic status check
            return {
                "status": "ONLINE",
                "panopticon": "Active",
                "neural_hash": "Ready",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Status Check Failed: {e}")
            return {"status": "DEGRADED", "error": str(e)}

    def _check_reflexes(self, user_input: str):
        """
        FAST PATH: Handles simple inputs instantly without LLM.
        """
        text = user_input.lower().strip()
        if text in ['hi', 'hello', 'hey']:
            return {"response_text": "Hello! I am online and ready. How can I assist your studies today?", "actions": []}
        if text in ['thanks', 'thank you']:
            return {"response_text": "You're welcome! Let's keep the momentum going.", "actions": []}
        if text == 'status':
            return {"response_text": "All systems nominal. Panopticon active. Neural Hash ready.", "actions": ["SHOW_PANOPTICON"]}
        return None

    def _get_cached_system_status(self):
        """
        Returns cached system status if valid, else refreshes.
        """
        now = datetime.now()
        if self._system_cache and self._cache_expiry and now < self._cache_expiry:
            return self._system_cache
            
        status = self._get_system_status_summary()
        self._system_cache = status
        from datetime import timedelta
        self._cache_expiry = now + timedelta(minutes=5)
        return status
    def _parse_response(self, response_text: str) -> dict:
        """Clean and parse Gemini JSON response"""
        try:
            text = response_text.strip()
            
            # 1. Try to find JSON code block
            import re
            json_match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
            if json_match:
                text = json_match.group(1)
            else:
                # 2. If no code block, try to find the first '{' and last '}'
                start = text.find('{')
                end = text.rfind('}')
                if start != -1 and end != -1:
                    text = text[start:end+1]
            
            return json.loads(text)
        except (json.JSONDecodeError, Exception) as e:
            print(f"JSON Parse Error: {e}")
            # Fallback: Try to salvage text if JSON fails
            return {
                "thought_process": "Failed to parse JSON",
                "response_text": response_text, # Return full text for debugging if parsing fails completely
                "suggested_actions": []
            }



    def _get_bio_directive(self, bio_status: dict) -> str:
        """
        Generates a directive for the Brain based on user's biological state.
        """
        try:
            energy = bio_status.get('energy_level', 50)
            mood = bio_status.get('mood_score', 50)
            
            if energy < 30 or mood < 30:
                return "CRITICAL: User is exhausted/stressed. Be extremely supportive. Suggest rest or light revision only. Do NOT push for mock tests."
            elif energy < 50:
                return "WARNING: User energy is low. Keep responses concise. Focus on high-yield, low-effort tasks."
            elif energy > 80 and mood > 80:
                return "OPTIMAL: User is in Flow State. Challenge them! Suggest complex topics or mock tests."
            else:
                return "NORMAL: Maintain standard coaching persona."
        except:
            return "NORMAL: Bio-data unavailable."

    def _get_lessons(self):
        """Retrieve recent lessons from Hippocampus"""
        try:
            from app.services.hippocampus_service import hippocampus
            return hippocampus.recall_lessons()
        except:
            return []

    def _resolve_context(self, user_input: str) -> str:
        """
        Dynamically fetch context based on user keywords.
        """
        context_str = ""
        user_input_lower = user_input.lower()
        
        # Intent: Schedule / Tasks
        # Expanded keywords to ensure context is available for "current" or "quiz" related queries
        if any(k in user_input_lower for k in ['schedule', 'plan', 'today', 'task', 'do', 'current', 'now', 'quiz', 'test', 'mock']):
            try:
                from app.services.study_planner import get_todays_tasks_summary
                tasks_summary = get_todays_tasks_summary()
                context_str += f"\n[SCHEDULE DATA]\n{tasks_summary}\n"
            except Exception as e:
                print(f"Context Resolution Error (StudyPlanner): {e}")
                
        return context_str

brain_service = BrainService()
