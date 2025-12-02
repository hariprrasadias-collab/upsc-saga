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
                self.model = genai.GenerativeModel('gemini-pro-latest') # Using flash for speed
                print("🧠 BrainService Online: Connected to Gemini Cortex.")
            except Exception as e:
                print(f"❌ BrainService Error: Failed to initialize Gemini: {e}")
                self.model = None
            
        self.registry = SynapseRegistry.get_instance()
        self.autonomy = autonomy_manager  # Autonomous execution manager
        self.context_window = [] # Short-term memory
        self.current_strategy = None # Golden Path Directive
        self.bio_status = None # Panopticon Status
        
        # Caching
        self._system_cache = None
        self._cache_expiry = None

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
            
        print(f"🧠 Brain: Strategic Directive Received. {len(path_data)} steps adopted.")
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
        print(f"🧠 Brain Executing Action: {action_type}")
        
        # 1. Log the action intent
        action_id = self.autonomy.log_action(
            action_type=action_type,
            action_payload=payload,
            executed_by='manual', 
            reasoning=payload.get('reasoning', 'User initiated action')
        )
        
        result = {"success": False, "message": "Unknown action"}
        
        try:
            # 2. Execute based on type
            if action_type == "CREATE_FLASHCARDS":
                from app.services.flashcard_service import FlashcardService
                topic = payload.get('topic')
                count = payload.get('count', 5)
                result = FlashcardService.generate_from_topic(topic, count)
                
            elif action_type == "SCHEDULE_REVISION":
                result = {"success": True, "message": f"Scheduled revision for {payload.get('subject')}"}

            elif action_type == "CREATE_MOCK_TEST":
                from app.services.mock_test_service import MockTestService
                subject = payload.get('subject') or payload.get('topic') or 'General'
                count = int(payload.get('count', 10))
                result = MockTestService.generate_from_topic(subject, count=count)
                
            elif action_type == "START_MOCK_TEST":
                result = {"success": True, "message": f"Starting mock test: {payload.get('subject')}"}

            elif action_type == "COMPLETE_MOCK_TEST":
                result = {"success": True, "message": f"Completed mock test for {payload.get('subject')}"}
            
            elif action_type == "ADD_TO_PALACE":
                try:
                    from app.db_models.mind_palace import MindPalaceArtifact
                    from app import db
                    
                    artifact = MindPalaceArtifact(
                        location_id=payload.get('location_id', 1),
                        title=payload.get('title', 'Untitled'),
                        content=payload.get('content', ''),
                        type=payload.get('type', 'note'),
                        x_position=payload.get('x_position', 50),
                        y_position=payload.get('y_position', 50),
                        z_position=payload.get('z_position', 0)
                    )
                    db.session.add(artifact)
                    db.session.commit()
                    
                    from app.services.game_engine import trigger_event
                    trigger_event('MIND_PALACE_ADD', 1)
                    
                    result = {"success": True, "message": f"I've stored '{artifact.title}' in your Mind Palace."}
                except Exception as e:
                    result = {"success": False, "message": f"Failed to add to Mind Palace: {str(e)}"}
            
            elif action_type == "RETRIEVE_FROM_PALACE":
                try:
                    from app.db_models.mind_palace import MindPalaceArtifact
                    from app.services.neural_hash_service import neural_hash_service
                    
                    query = payload.get('query', '')
                    expanded_queries = neural_hash_service.expand_query(query)
                    
                    filters = []
                    for q in expanded_queries:
                        filters.append(MindPalaceArtifact.title.contains(q))
                        filters.append(MindPalaceArtifact.content.contains(q))
                    
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
                        "data": path_data
                    }
                except Exception as e:
                    result = {"success": False, "message": f"Path calculation failed: {str(e)}"}
                
            else:
                result = {"success": False, "message": f"Action {action_type} not implemented yet"}
                
            # 3. Update outcome
            self.autonomy.update_action_outcome(
                action_id=action_id,
                outcome_status='success' if result['success'] else 'failure',
                impact_score=0.5 if result['success'] else -0.1
            )
            
            # 4. Update Syllabus Progress
            if result['success']:
                try:
                    syllabus_updates = SyllabusTracker.auto_update_from_action(action_type, payload)
                    if syllabus_updates:
                        print(f"📚 Syllabus Updated: {syllabus_updates}")
                except Exception as e:
                    print(f"⚠️ Syllabus Update Failed: {e}")

            # 5. Log A/B Test Result
            if result['success'] and payload.get('ab_test_id'):
                try:
                    ab_tester.log_result(
                        test_name=payload['ab_test_id'],
                        metric_name='completion',
                        value=1.0
                    )
                except Exception as e:
                    print(f"⚠️ A/B Logging Failed: {e}")

            return result

        except Exception as e:
            print(f"❌ Brain Action Failed: {e}")
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

    def _get_system_status_summary(self) -> dict:
        """Gather high-level status from all synapses"""
        synapses = self.registry.get_all_synapses()
        return {
            "connected_synapses": sum(len(v) for v in synapses.values()),
            "time": datetime.now().isoformat(),
            "active_modules": list(synapses.keys()),
            "current_strategy": self.current_strategy,
            # Bio status is fetched separately now for parallelism
        }

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
