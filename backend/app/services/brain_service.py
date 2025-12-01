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
                print("🧠 BrainService Online: Connected to Gemini Cortex.")
            except Exception as e:
                print(f"❌ BrainService Error: Failed to initialize Gemini: {e}")
                self.model = None
            
        self.registry = SynapseRegistry.get_instance()
        self.autonomy = autonomy_manager  # Autonomous execution manager
        self.context_window = [] # Short-term memory

    def think(self, user_input: str, context_override: dict = None) -> dict:
        """
        Core reasoning loop.
        1. Gathers context from relevant synapses (if needed).
        2. Processes user input.
        3. Returns a structured response with thoughts and actions.
        """
        if not self.model:
            return {"response_text": "I am offline. Please check my API key.", "actions": []}

        # 1. Gather Global Context (Brief scan)
        system_status = self._get_system_status_summary()
        
        # 2. Resolve Specific Context based on Intent
        specific_context = self._resolve_context(user_input)
        
        # 3. Construct Prompt
        prompt = f"""
        You are the CENTRAL NERVOUS SYSTEM (The Brain) of a UPSC Preparation App.
        Your goal is to be an Omniscient Guide for the user.
        
        CURRENT SYSTEM STATUS:
        {json.dumps(system_status, indent=2)}
        
        SPECIFIC CONTEXT (Real-time Data):
        {specific_context}
        
        USER INPUT: "{user_input}"
        
        RESPONSE FORMAT (JSON only):
        {{
            "thought_process": "Brief reasoning about what the user needs...",
            "response_text": "Natural language response to the user...",
            "suggested_actions": [
                {{
                    "type": "ACTION_TYPE",
                    "payload": {{ ...params... }},
                    "label": "Button Label"
                }}
            ]
        }}
        
        Available Action Types:
        - CREATE_FLASHCARDS (payload: topic, count)
        - CREATE_MOCK_TEST (payload: subject)
        - SCHEDULE_REVISION (payload: subject, time)
        - START_MOCK_TEST (payload: subject)
        - ANALYZE_WEAK_AREAS (payload: subject)
        - GENERATE_STUDY_PLAN (payload: duration_days, focus_areas)
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
            executed_by='manual', # Default to manual for now, updated if auto
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
                # Handle both 'subject' and 'topic' keys for robustness
                subject = payload.get('subject') or payload.get('topic') or 'General'
                result = MockTestService.generate_from_topic(subject, count=10)
                
            elif action_type == "START_MOCK_TEST":
                result = {"success": True, "message": f"Starting mock test: {payload.get('subject')}"}

            elif action_type == "COMPLETE_MOCK_TEST":
                # In real app, this would save results to DB
                result = {"success": True, "message": f"Completed mock test for {payload.get('subject')}"}
                
            else:
                result = {"success": False, "message": f"Action {action_type} not implemented yet"}
                
            # 3. Update outcome
            self.autonomy.update_action_outcome(
                action_id=action_id,
                outcome_status='success' if result['success'] else 'failure',
                impact_score=0.5 if result['success'] else -0.1 # Placeholder impact
            )
            
            # 4. Update Syllabus Progress (if applicable)
            if result['success']:
                try:
                    syllabus_updates = SyllabusTracker.auto_update_from_action(action_type, payload)
                    if syllabus_updates:
                        print(f"📚 Syllabus Updated: {syllabus_updates}")
                except Exception as e:
                    print(f"⚠️ Syllabus Update Failed: {e}")

            # 5. Log A/B Test Result (if applicable)
            if result['success'] and payload.get('ab_test_id'):
                try:
                    ab_tester.log_result(
                        test_name=payload['ab_test_id'],
                        metric_name='completion',
                        value=1.0
                    )
                    print(f"🧪 A/B Test '{payload['ab_test_id']}' logged.")
                except Exception as e:
                    print(f"⚠️ A/B Logging Failed: {e}")
            
            return result
            
        except Exception as e:
            print(f"Action Execution Error: {e}")
            self.autonomy.update_action_outcome(
                action_id=action_id,
                outcome_status='failure',
                reasoning=str(e)
            )
            return {"success": False, "message": str(e)}

    def _get_system_status_summary(self) -> dict:
        """Gather high-level status from all synapses"""
        synapses = self.registry.get_all_synapses()
        return {
            "connected_synapses": sum(len(v) for v in synapses.values()),
            "time": datetime.now().isoformat(),
            "active_modules": list(synapses.keys())
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
