import os
import json
import traceback
from datetime import datetime
from dotenv import load_dotenv
from app.services.model_manager import model_manager
from app.services.synapse_registry import SynapseRegistry
from app.services.autonomy_manager import autonomy_manager
from app.services.syllabus_tracker import SyllabusTracker
from app.services.ab_tester import ab_tester
from app.services.mindmap_service import MindMapService
from app.db_models.automation_storage import (
    save_socratic_dialogue, save_triangulation, 
    save_foresight_prediction, save_ai_content
)
from app.db_models.neural_hash import save_neural_hash_log

load_dotenv()

class BrainService:
    """
    The Central Nervous System (CNS) of the application.
    Uses Gemini to reason, analyze, and optimize the user's UPSC preparation
    by connecting to all registered synapses.
    """
    
    def __init__(self):
        # Initialize Brain Service - Core Logic
        self.api_key = os.environ.get('GEMINI_API_KEY')
        self.is_lobotomized = False
        self.manual_mode = False # AUTOMATION RESTORED (Safe via ModelManager)

        if not self.api_key:
            print("⚠️ BrainService Warning: GEMINI_API_KEY not found. The Brain will be lobotomized (Mock Mode).")
            self.is_lobotomized = True
        else:
            if model_manager.is_configured:
                print("BrainService Online: Connected to Gemini Cortex via ModelManager.")
            else:
                print("BrainService Warning: ModelManager not configured.")
                self.is_lobotomized = True
            
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
            from app.services.panopticon_service import panopticon
            return panopticon.get_current_status()
        except Exception as e:
            print(f"Bio-Check Failed: {e}")
            return {"status": "OFFLINE", "energy": 0, "alert": "Panopticon Unreachable"}

    def think(self, user_input: str, context_override: dict = None) -> dict:
        """
        Core reasoning loop. Optimized for speed using parallel processing and caching.
        """
        if self.is_lobotomized:
            return {"response_text": "I am offline (Lobotomized). Please check my API key.", "actions": []}

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
            # Complex reasoning requires Pro model
            response = model_manager.generate_content(prompt, model_type='pro')
            return self._parse_response(response.text)
        except Exception as e:
            print(f"Brain Think Error: {e}")
            return {"response_text": f"I had a headache thinking about that. Error: {str(e)}", "actions": []}

    def _add_flashcard(self, user_id, topic, subject, front, back, source, card_type='basic'):
        """Helper to create a deck if needed and add a flashcard."""
        try:
            from app.db import get_db
            conn = get_db()
            deck_name = f"Auto-Gen: {topic}"

            # Check for deck, if not exists create it.
            cursor = conn.execute("SELECT id FROM decks WHERE name = ? AND user_id = ?", (deck_name, user_id))
            row = cursor.fetchone()
            if row:
                deck_id = row[0]
            else:
                cursor = conn.execute("INSERT INTO decks (user_id, name, subject) VALUES (?, ?, ?)", (user_id, deck_name, subject))
                deck_id = cursor.lastrowid
                conn.commit()

            conn.execute('''
                INSERT INTO flashcards (deck_id, front, back, source, card_type)
                VALUES (?, ?, ?, ?, ?)
            ''', (deck_id, front, back, source, card_type))
            conn.commit()
        except Exception as e:
            print(f"Brain: Flashcard creation failed: {e}")

    def _get_topic_id(self, topic_name):
        """Helper to find topic_id from syllabus_topics."""
        try:
            from app.db import get_db
            conn = get_db()
            # Try exact match
            row = conn.execute("SELECT id FROM syllabus_topics WHERE topic = ?", (topic_name,)).fetchone()
            if not row:
                # Try LIKE match
                row = conn.execute("SELECT id FROM syllabus_topics WHERE topic LIKE ?", (f"%{topic_name}%",)).fetchone()
            return row[0] if row else None
        except:
            return None

    def _save_revision_note(self, topic, title, content):
        """Save revision note to revision_cards table."""
        try:
            from app.db import get_db
            topic_id = self._get_topic_id(topic)
            if not topic_id:
                topic_id = 0 # Default/Orphaned

            conn = get_db()
            # Generate a one-liner (first sentence)
            one_liner = content.split('.')[0] + "." if content else "Summary"
            conn.execute('''
                INSERT INTO revision_cards (topic_id, title, one_liner, full_content, created_at)
                VALUES (?, ?, ?, ?, datetime('now'))
            ''', (topic_id, title, one_liner, content))
            conn.commit()
            print(f"Brain: Saved Revision Note for {topic}")
        except Exception as e:
            print(f"Brain: Failed to save revision note: {e}")

    def _save_essay_prompt(self, topic, subject, prompt):
        """Save essay prompt to answer_writing_prompts table."""
        try:
            from app.db import get_db
            conn = get_db()
            conn.execute('''
                INSERT INTO answer_writing_prompts (question, subject, topic, difficulty, word_limit, created_at)
                VALUES (?, ?, ?, 'Hard', 250, datetime('now'))
            ''', (prompt, subject, topic))
            conn.commit()
            print(f"Brain: Saved Essay Prompt for {topic}")
        except Exception as e:
            print(f"Brain: Failed to save essay prompt: {e}")

    def _save_prediction(self, topic, subject, predictions):
        """Save predictions to foresight_predictions table."""
        try:
            from app.db import get_db
            conn = get_db()

            if isinstance(predictions, list):
                for p in predictions:
                    question = p.get('question', 'Unknown Question')
                    p_type = p.get('type', 'MCQ')
                    conn.execute('''
                        INSERT INTO foresight_predictions (question, subject, topic, type, probability, created_at)
                        VALUES (?, ?, ?, ?, 0.85, datetime('now'))
                    ''', (question, subject, topic, p_type))
                conn.commit()
                print(f"Brain: Saved {len(predictions)} predictions for {topic}")
        except Exception as e:
            print(f"Brain: Failed to save predictions: {e}")

    def _save_mnemonic(self, topic, mnemonic_text, m_type='visual'):
        """Save mnemonic to mnemonics_history table."""
        try:
            from app.db import get_db
            conn = get_db()
            conn.execute('''
                INSERT INTO mnemonics_history (mnemonic_text, original_text, mnemonic_type)
                VALUES (?, ?, ?)
            ''', (mnemonic_text, topic, m_type))
            conn.commit()
            print(f"Brain: Saved Mnemonic for {topic}")
        except Exception as e:
            print(f"Brain: Failed to save mnemonic: {e}")

    def generate_manual_completion_prompt(self, task_data: dict):
        """
        Generates a 'TITAN LEVEL' MEGA PROMPT for manual execution in Gemini.
        Saves context to pending_manual_task.json.
        """
        topic = task_data.get('topic')
        subject = task_data.get('subject')

        print(f"Brain: Generating 'Titan Level' Manual Prompt for {subject} - {topic}")

        # 1. Gather Context
        pyq_context = ""
        try:
            from app.db import get_db
            conn = get_db()
            questions = conn.execute(
                "SELECT year, question_text FROM pyq_questions WHERE topic LIKE ? OR subject = ? ORDER BY year DESC LIMIT 20",
                (f"%{topic}%", subject)
            ).fetchall()
            pyq_context = "\n".join([f"[{q['year']}] {q['question_text']}" for q in questions])
        except Exception as e:
            pyq_context = "No PYQ data available."

        recent_topics = []
        try:
            from app.services.syllabus_tracker import SyllabusTracker
            recent_data = SyllabusTracker.get_recently_completed(limit=5)
            recent_topics = [t['topic'] for t in recent_data if t['topic'] != topic]
        except:
            pass

        weak_areas_text = ""
        try:
            from app.services.weak_area_service import WeakAreaAnalyzer
            weak_areas = WeakAreaAnalyzer.analyze_user_performance(user_id=1, days=30)
            if weak_areas:
                weak_areas_text = "USER WEAK AREAS:\n" + "\n".join([f"- {area['topic']} ({area['subject']}) - Accuracy: {area['accuracy_rate']}%" for area in weak_areas[:5]])
        except:
            pass

        # 2. Construct Prompt - Section by Section

        prompt = f"""
# SYSTEM ROLE: THE OMNISCIENT UPSC ARCHITECT (TITAN MODE)
You are the "Brain" — the apex intelligence for Civil Services preparation. You combine the depth of an Oxford academic, the cynicism of a veteran UPSC examiner, and the pedagogical skill of Feynman.
Your output must be structurally perfect, intellectually dense, and strictly compliant with the JSON schema.

# MISSION PROFILE
- **Task:** Generate the ULTIMATE Study Artifact Bundle for the topic: "{topic}" ({subject}).
- **Standard:** "TITAN Level" quality. Surpass standard AI. BE EXHAUSTIVE AND DETAILED.
- **Tone:** Authoritative, Insightful, Nuanced, and Exam-Relevant. DO NOT SUMMARIZE. EXPAND.

# CRITICAL CONTEXT
## 1. Previous Year Question (PYQ) DNA:
(Use this to calibrate difficulty and identify recurring themes)
{pyq_context}

## 2. Neural Linkages (Recent History):
(Connect current topic to these concepts)
{', '.join(recent_topics)}

## 3. Targeted Weaknesses:
(Fortify these specific areas for the user)
{weak_areas_text}

---

# GENERATION GUIDELINES & ANTI-PATTERNS (CRITICAL)
- **NO FLUFF:** Ban words like "crucial", "pivotal", "significant role", "various". If it doesn't add marks, delete it.
- **NO GENERIC ADVICE:** Do not say "It is important to study this...". Instead, say "Examiners target this nuance in 2019/2021...".
- **FORMATTING:** Use Markdown bolding (**text**) for all keywords that would be underlined in an exam.
- **DEPTH OVER BREADTH:** Do not give 10 shallow points. Give 3 points with Case Laws, Articles, and Examples.

# INSTRUCTION PROTOCOLS (STRICT COMPLIANCE)

## A. META-COGNITION (Chain of Thought)
- **Strategy:** Before generating content, explain your pedagogical strategy for this specific topic in the `_meta` field. Why did you choose these specific flashcards? What is the core difficulty here?

## B. FLASHCARDS (Active Recall - SCENARIO BASED)
- **Rule:** No simple definitions. Use "Scenario-Based" questions.
- **Example:** Instead of "What is Article 21?", ask "If a citizen is denied travel abroad, which Case Law and Article protects them?"
- **Examiner's Lens:** Focus on confusing pairs and subtle exceptions.

## C. TRIANGULATION 4.0 (The Ultimate Synthesis)
- **Synthesis:** Write a COMPREHENSIVE and ANALYTICAL body of text (approx 250-300 words). Do not scrimp on details. Synthesize static theory with dynamic current events.
- **Critical Axis:** Provide strong, detailed Arguments FOR and AGAINST. Use a table format if possible (Markdown).
- **PESTLE:** Deep dive into Political, Economic, Sociological, Technological, Legal, Environmental angles.
- **GS Linkages:** Explicitly link to GS1, GS2, GS3, and GS4 papers with specific examples. Include Optional Subject linkages (e.g., PSIR, Sociology) if relevant.

## D. SOCRATIC DIALOGUE (The Arena - DRAMATIC STEEL-MANNING)
- **Simulation:** Simulate a high-stakes, multi-turn debate with **Dramatic Cues**.
- **Technique:** Use **Steel-Manning** (attacking the strongest version of the opponent's argument).
- **Scripting:** Use stage directions like `(slams table)`, `(whispering conspiratorially)`, `(interrupting)`.
- **Verbosity:** Each turn must be SUBSTANTIAL (50-100 words).
- **Personas:**
  - **Socrates (The Skeptic):** Questions definitions, exposes contradictions.
  - **Plato (The Idealist):** Focuses on moral 'oughts' and vision.
  - **Aristotle (The Realist):** Focuses on evidence, pragmatism, and feasibility.
  - **Machiavelli (The Strategist):** Focuses on power dynamics and outcome.
- **Goal:** Reach a profound synthesis or expose a deep dilemma.

## E. MOCK TEST (Trap Analysis)
- **Requirement:** For every question, explain not just why the correct answer is right, but specifically analyze the **TRAP** in the wrong options. Why would a student choose 'B' instead of 'A'? What cognitive bias is being exploited?

## F. VISUAL PROMPT (Cinematic)
- **Style:** Request specific camera angles, lighting, and style (e.g., "Cinematic lighting, 8k, Unreal Engine 5, Macro Shot").

---

# OUTPUT SCHEMA (JSON ONLY)

{{
  "_meta": "Pedagogical strategy explanation...",

  "flashcards": [
      {{ "front": "Scenario/Question...", "back": "Detailed Answer..." }} // 5 High Quality Cards
  ],

  "revision_note": "A Detailed Revision Module. Comprehensive coverage of the topic. Use bullet points, bold keywords, and explanatory text. Do not limit word count. Ensure full conceptual clarity.",

  "mind_map": {{
      "name": "{topic}",
      "children": [
          {{ "name": "Theme A", "children": [ {{ "name": "Detail A1" }} ] }}
      ]
  }},

  "mock_test": {{
      "title": "Test: {topic}",
      "questions": [
          {{
              "question_text": "...",
              "option_a": "...", "option_b": "...", "option_c": "...", "option_d": "...",
              "correct_answer": "A",
              "explanation": "Detailed explanation. TRAP ANALYSIS: Option B is a distractor because... Option C is incorrect due to..."
          }}
      ] // 10 Questions. UPSC Prelims 2024 Standard (Statement based, Pairs).
  }},

  "pyq_trends": "Strategic Intelligence Report. 1. Frequency Analysis 2. Thematic Evolution 3. Prediction for Next Year.",

  "predictions": [
      {{ "question": "...", "type": "MCQ", "probability": 0.85, "reasoning": "Based on recent trend X..." }} // 3 'Black Swan' Questions.
  ],

  "socratic_dialogue": {{
      "dialogue": [
          {{ "speakerId": "skeptic", "text": "(Raises an eyebrow) But surely...", "type": "ARGUMENT" }},
          {{ "speakerId": "idealist", "text": "(Passionately) You miss the point entirely!...", "type": "REBUTTAL" }}
      ], // 6 turns total. Use speakerId: skeptic, idealist, realist, strategist. ENSURE LONG, DETAILED RESPONSES.
      "verdict": {{ "winner": "...", "synthesis": "Hegelian Synthesis of the debate." }}
  }},

  "triangulation": {{
      "synthesis": "Comprehensive Mains Answer Body...",
      "scholars": [ {{ "name": "...", "quote": "...", "context": "..." }} ],
      "data_bank": [ {{ "statistic": "...", "source": "...", "relevance": "..." }} ],
      "critical_axis": {{ "arguments_for": ["..."], "arguments_against": ["..."] }},
      "pestle": {{ "political": "...", "economic": "...", "sociological": "...", "technological": "...", "legal": "...", "environmental": "..." }},
      "gs_linkages": {{ "gs1": "...", "gs2": "...", "gs3": "...", "gs4": "..." }},
      "optional_linkages": ["Link to PSIR...", "Link to Sociology..."],
      "way_forward": {{ "immediate": "...", "long_term": "..." }}
  }},

  "neural_hash": {{
      "core_themes": ["Theme 1", "Theme 2"],
      "examiner_pattern": "The specific mental model examiners use for this topic.",
      "cross_linkages": ["Link to Economy", "Link to Ethics"]
  }},

  "pitfalls": ["Trap 1 (Nuance often missed)", "Trap 2 (Common confusion)"],

  "podcast_script": "Host: ... \\n Guest: ... (Follow the 'Coffee Chat' style guide strictly)",

  "essay_prompt": "A prompt connecting {topic} to a broad philosophical theme. Include a Thesis Hint.",

  "visual_prompt": "Cinematic lighting, 8k, Unreal Engine 5, Macro Shot of...",

  "roleplay_scenario": "You are a District Magistrate. Crisis involving {topic}. 1. Incident 2. Stakeholders 3. The Dilemma 4. Options.",

  "map_work": [
      {{ "name": "Place", "lat": 0.0, "lon": 0.0, "reason": "Significance...", "question": "..." }}
  ],

  "linkages": ["Link 1 (How X affects Y)", "Link 2"],

  "cheat_sheet": {{
      "title": "{topic}",
      "tabs": [
          {{ "id": "facts", "label": "⚡ Facts", "content": "Detailed Markdown list" }},
          {{ "id": "mnemonics", "label": "🧠 Mnemonic", "content": "..." }},
          {{ "id": "judgments", "label": "⚖️ Law", "content": "..." }},
          {{ "id": "timeline", "label": "📅 Time", "content": "..." }},
          {{ "id": "examiner", "label": "🧐 Examiner's View", "content": "..." }},
          {{ "id": "concept_map", "label": "🗺️ Concept Map", "content": "Mermaid JS code", "type": "mermaid" }},
          {{ "id": "quiz", "label": "❓ Active Recall", "content": "JSON Array of Quiz Objects", "type": "quiz" }}
      ]
  }},

  "quote_bank": {{
      "quotes": "2 Quotes (Scholar/Leader).",
      "data": "2 Data Points (Official Sources)."
  }},

  "timeline": "Chronological list (Year - Event).",

  "ethics_dilemma": "Case Study. Conflict of interest/duty. End with 'What is the most ethical course of action?'.",

  "eli5": {{
      "eli5": "Simple analogy...",
      "eli15": "High School level...",
      "eli_expert": "Academic definition...",
      "analogy": "Concrete metaphor...",
      "visual_analogy_prompt": "Image prompt for the analogy...",
      "real_world_example": "...",
      "quiz": [ {{ "question": "...", "options": ["..."], "answer": "..." }} ]
  }}
}}
        """

        # 3. Save to Files
        try:
            # Determine backend root directory (app/services/../..)
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            prompt_path = os.path.join(base_dir, 'manual_prompt.txt')
            json_path = os.path.join(base_dir, 'pending_manual_task.json')

            # Save Prompt
            with open(prompt_path, 'w', encoding='utf-8') as f:
                f.write(prompt)

            # Save Context for Ingestion
            pending_data = {
                "topic": topic,
                "subject": subject,
                "user_id": task_data.get('user_id', 1),
                "plan_id": task_data.get('plan_id'),
                "task_id": task_data.get('id'),
                "timestamp": datetime.now().isoformat()
            }
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(pending_data, f, indent=2)

            print(f"Brain: 'Titan Level' Manual Prompt saved to {prompt_path}")
            print(f"Brain: Pending Task Context saved to {json_path}")

        except Exception as e:
            print(f"Brain: Failed to save manual prompt files: {e}")

    def process_manual_completion_artifact(self, json_data: dict, task_data: dict):
        """
        Ingests the manually generated JSON artifact and saves everything to DB.
        """
        topic = task_data.get('topic')
        subject = task_data.get('subject')
        user_id = task_data.get('user_id', 1)

        print(f"Brain: Ingesting Manual Artifact for {topic}...")

        try:
            # 1. Flashcards
            if 'flashcards' in json_data:
                for card in json_data['flashcards']:
                    self._add_flashcard(user_id, topic, subject, card['front'], card['back'], 'manual_ai_gen')

            # 2. Revision Note
            if 'revision_note' in json_data:
                content = json_data['revision_note']
                self._save_revision_note(topic, f"Revision Note: {topic}", content)
                self._add_flashcard(user_id, topic, subject, f"Revision Note: {topic}", content, 'manual_ai_summary')

            # 3. Mind Map
            if 'mind_map' in json_data:
                try:
                    from app.services.mindmap_service import MindMapService
                    MindMapService.save_mindmap(f"{topic} Mind Map", json_data['mind_map'])
                    save_ai_content('mind_map', topic, json.dumps(json_data['mind_map']))
                except Exception as e:
                    print(f"Ingest Error (MindMap): {e}")

            # 4. Mock Test
            if 'mock_test' in json_data:
                try:
                    data = json_data['mock_test']
                    from app.db import get_db
                    conn = get_db()
                    cursor = conn.execute('''
                        INSERT INTO mock_tests (title, subject, total_questions, duration_minutes, test_type, total_marks)
                        VALUES (?, ?, ?, ?, 'MOCK', ?)
                    ''', (data.get('title', f"Test: {topic}"), topic, len(data.get('questions', [])), len(data.get('questions', []))*2, len(data.get('questions', []))*2))
                    test_id = cursor.lastrowid

                    for i, q in enumerate(data.get('questions', []), 1):
                        conn.execute('''
                            INSERT INTO test_questions
                            (test_id, question_number, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (test_id, i, q['question_text'], q['option_a'], q['option_b'], q['option_c'], q['option_d'], q['correct_answer'], q['explanation']))
                    conn.commit()
                except Exception as e:
                    print(f"Ingest Error (MockTest): {e}")

            # 5. PYQ Trends
            if 'pyq_trends' in json_data:
                self._add_flashcard(user_id, topic, subject, f"PYQ Analysis: {topic}", json_data['pyq_trends'], 'manual_ai_pyq')

            # 6. Predictions
            if 'predictions' in json_data:
                self._save_prediction(topic, subject, json_data['predictions'])
                pred_text = "\n".join([f"- {p.get('question')} ({p.get('type')})" for p in json_data['predictions']])
                self._add_flashcard(user_id, topic, subject, f"Predicted Questions: {topic}", pred_text, 'manual_ai_foresight')
                save_ai_content('predictions', topic, pred_text)

            # 7. Socratic Dialogue
            if 'socratic_dialogue' in json_data:
                sd = json_data['socratic_dialogue']
                dialogue = sd.get('dialogue', [])
                verdict = sd.get('verdict', {})
                # Flatten dialogue to string for flashcard
                self._add_flashcard(user_id, topic, subject, f"Socratic Debate: {topic}", "See Socratic Archives.", 'manual_ai_socratic')
                save_socratic_dialogue(user_id, topic, json.dumps(dialogue), json.dumps(verdict))
                save_ai_content('socratic', topic, json.dumps(dialogue), verdict)

            # 8. Triangulation
            if 'triangulation' in json_data:
                tri = json_data['triangulation']
                synthesis = tri.get('synthesis', '')
                way_forward = json.dumps(tri.get('way_forward', {}), indent=2)
                content = f"Synthesis:\n{synthesis}\n\nWay Forward:\n{way_forward}"
                self._add_flashcard(user_id, topic, subject, f"Mains Strategy: {topic}", content, 'manual_ai_triangulation')
                save_triangulation(topic, synthesis, tri)
                save_ai_content('triangulation', topic, synthesis, tri)

            # 9. Neural Hash
            if 'neural_hash' in json_data:
                nh = json_data['neural_hash']
                themes = ", ".join(nh.get('core_themes', []))
                pattern = nh.get('examiner_pattern', '')
                content = f"Core Themes: {themes}\n\nExaminer Pattern: {pattern}\n\nCross Linkages: {', '.join(nh.get('cross_linkages', []))}"
                self._add_flashcard(user_id, topic, subject, f"Examiner's Lens: {topic}", content, 'manual_ai_neural_hash')
                # Log simplified
                save_neural_hash_log(topic, "upsc_topic", nh)
                save_ai_content('neural_hash', topic, json.dumps(nh))

            # 10. Pitfalls
            if 'pitfalls' in json_data:
                content = "\n".join([f"⚠️ {p}" for p in json_data['pitfalls']])
                self._add_flashcard(user_id, topic, subject, f"Common Pitfalls: {topic}", content, 'manual_ai_pitfalls')
                save_ai_content('pitfalls', topic, content, {'subject': subject})

            # 11. Podcast Script
            if 'podcast_script' in json_data:
                script = json_data['podcast_script']
                self._add_flashcard(user_id, topic, subject, f"Podcast Script: {topic}", script, 'manual_ai_podcast')
                save_ai_content('podcast', topic, script)

            # 12. Essay Prompt
            if 'essay_prompt' in json_data:
                prompt_text = json_data['essay_prompt']
                self._save_essay_prompt(topic, subject, prompt_text)
                self._add_flashcard(user_id, topic, subject, f"Essay Prompt: {topic}", prompt_text, 'manual_ai_essay')
                save_ai_content('essay', topic, prompt_text, {'subject': subject})

            # 13. Visual Prompt
            if 'visual_prompt' in json_data:
                prompt_text = json_data['visual_prompt']
                self._save_mnemonic(topic, prompt_text, 'visual')
                self._add_flashcard(user_id, topic, subject, f"Visual Mnemonic Prompt: {topic}", prompt_text, 'manual_ai_visual')
                save_ai_content('visual_prompt', topic, prompt_text)

            # 14. Roleplay
            if 'roleplay_scenario' in json_data:
                scenario = json_data['roleplay_scenario']
                self._add_flashcard(user_id, topic, subject, f"Roleplay Scenario: {topic}", scenario, 'manual_ai_roleplay')
                save_ai_content('roleplay', topic, scenario)

            # 15. Map Work
            if 'map_work' in json_data and json_data['map_work']:
                locations = json_data['map_work']
                content = json.dumps(locations)
                self._add_flashcard(user_id, topic, subject, f"Map Work Challenge: {topic}", content, 'manual_ai_mapwork', card_type='map_work')
                save_ai_content('map_work', topic, content, {'locations': locations})

            # 16. Linkages
            if 'linkages' in json_data and json_data['linkages']:
                linkages = json_data['linkages']
                content = "\n".join([f"🔗 {l}" for l in linkages])
                self._add_flashcard(user_id, topic, subject, f"Connect the Dots: {topic}", content, 'manual_ai_linkages')
                save_ai_content('topic_linkages', topic, content, {'linkages': linkages})

            # 17. Cheat Sheet
            if 'cheat_sheet' in json_data:
                content = json.dumps(json_data['cheat_sheet'])
                self._add_flashcard(user_id, topic, subject, f"Cheat Sheet: {topic}", content, 'manual_ai_cheatsheet')
                save_ai_content('cheat_sheet', topic, content)

            # 18. Quote Bank
            if 'quote_bank' in json_data:
                qb = json_data['quote_bank']
                content = f"Quotes:\n{qb.get('quotes')}\n\nData:\n{qb.get('data')}"
                self._add_flashcard(user_id, topic, subject, f"Mains Fodder: {topic}", content, 'manual_ai_fodder')
                save_ai_content('quote_bank', topic, content)

            # 19. Timeline
            if 'timeline' in json_data and json_data['timeline']:
                self._add_flashcard(user_id, topic, subject, f"Timeline: {topic}", json_data['timeline'], 'manual_ai_timeline')
                save_ai_content('timeline', topic, json_data['timeline'])

            # 20. Ethics Dilemma
            if 'ethics_dilemma' in json_data and json_data['ethics_dilemma']:
                self._add_flashcard(user_id, topic, subject, f"Ethical Dilemma: {topic}", json_data['ethics_dilemma'], 'manual_ai_dilemma')
                save_ai_content('ethics_dilemma', topic, json_data['ethics_dilemma'])

            # 21. ELI5
            if 'eli5' in json_data:
                data = json_data['eli5']
                content_to_save = json.dumps(data)
                flashcard_back = f"🧸 ELI5: {data.get('eli5', '')}\n\n💡 Analogy: {data.get('analogy', '')}"
                self._add_flashcard(user_id, topic, subject, f"ELI5: {topic}", flashcard_back, 'manual_ai_eli5')
                save_ai_content('eli5', topic, content_to_save)

            # Standard Post-Completion Triggers (Syllabus, XP, etc.)
            try:
                from app.services.syllabus_tracker import SyllabusTracker
                SyllabusTracker.update_topic_progress(topic, 'Completed')
            except: pass

            try:
                from app.services.game_engine import trigger_event
                trigger_event('TASK_COMPLETE_BONUS', user_id)
            except: pass

            # Boss Fight Check
            self._check_boss_fight(topic, subject, task_data)

            print("Brain: Manual Ingestion Complete!")
            return True

        except Exception as e:
            print(f"Brain: Ingestion Failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _check_boss_fight(self, topic, subject, task_data):
        try:
            book_title = self._identify_book_for_topic(subject, topic)
            boss_name = f"The Guardian of {book_title}" if book_title else f"The {subject} Final Boss"

            from app.db_models.study_plan import get_pending_task_count
            plan_id = task_data.get('plan_id')
            if plan_id:
                pending_count = get_pending_task_count(plan_id, subject, exclude_task_id=task_data.get('id'))
                if pending_count == 0:
                    self.execute_action("SUMMON_BOSS", {"filters": {"subject": subject}, "name": boss_name, "reasoning": "Subject/Book Completion"})
        except Exception as e:
            print(f"Boss Check Failed: {e}")

    def process_task_completion(self, task_data: dict):
        """
        Proactively triggers Brain actions when a study task is completed.
        """
        topic = task_data.get('topic')
        subject = task_data.get('subject')
        user_id = task_data.get('user_id', 1)

        print(f"Brain: Processing completion for {subject} - {topic} (User {user_id})")

        if not topic:
            return

        # MANUAL MODE CHECK
        # Note: If user wants automation, we should skip this return.
        # But if manual_mode is True, we generate manual prompt and return.
        if self.manual_mode:
            self.generate_manual_completion_prompt(task_data)
            return

        # ... Existing Automation Logic ...
        try:
            import concurrent.futures
            from flask import current_app
            
            # Capture app context for worker threads
            app = current_app._get_current_object()
            
            # Define all actions to run (The Full Brain Vault Suite)
            actions = [
                # Core Learning
                ("CREATE_FLASHCARDS", {"topic": topic, "count": 5, "reasoning": "Task Completion Automation"}),
                ("CREATE_MOCK_TEST", {"topic": topic, "count": 10, "reasoning": "Task Completion Automation"}),
                ("GENERATE_ELI5", {"topic": topic}),
                ("GENERATE_CHEAT_SHEET", {"topic": topic}),
                
                # Context & Connections
                ("PREDICT_QUESTIONS", {"topic": topic, "subject": subject, "timeframe_days": 30}),
                ("GENERATE_TOPIC_LINKAGES", {"topic": topic, "subject": subject}),
                ("GENERATE_TIMELINE", {"topic": topic}),
                ("GENERATE_MAP_WORK", {"topic": topic}),
                ("GENERATE_MIND_MAP", {"topic": topic}),
                
                # Creative & Application
                ("GENERATE_PODCAST_SCRIPT", {"topic": topic, "style": "humorous"}),
                ("GENERATE_SOCRATIC_DIALOGUE", {"topic": topic, "subject": subject}),
                ("GENERATE_ROLEPLAY_SCENARIO", {"topic": topic}),
                ("GENERATE_VISUAL_PROMPT", {"topic": topic}),
                
                # Analysis & Writing
                ("GENERATE_ESSAY_PROMPT", {"topic": topic, "subject": subject}),
                ("GENERATE_QUOTE_BANK", {"topic": topic}),
                ("FIND_COMMON_PITFALLS", {"topic": topic})
            ]

            print(f"Brain: 🚀 Launching {len(actions)} parallel automation tasks for {topic}")
            
            def run_action_safe(action, payload):
                """Helper to run action in app context and SAVE RESULTS"""
                import traceback
                try:
                    with app.app_context():
                        from app.db import get_db
                        conn = get_db()
                        
                        print(f"Brain: ⚡ Parallel Start -> {action}")
                        result = self.execute_action(action, payload)
                        
                        # PERSISTENCE LOGIC
                        if result and result.get('success'):
                            # 1. Foresight Predictions
                            if action == "PREDICT_QUESTIONS":
                                data = result.get('data', [])
                                if data:
                                    # Already saved in execute_action usually, but double check
                                    # The execute_action for PREDICT_QUESTIONS calls foresight_engine.predict_questions which saves to DB.
                                    # ALSO save summary to Brain Vault
                                    prediction_summary = "\n".join([f"- {p.get('question')} ({p.get('type')})" for p in data])
                                    save_ai_content('predictions', topic, prediction_summary, {'predictions': data})
                            
                            # 2. Socratic Dialogue
                            elif action == "GENERATE_SOCRATIC_DIALOGUE":
                                dialogue = result.get('dialogue')
                                verdict = result.get('verdict')
                                if dialogue:
                                    save_socratic_dialogue(user_id, topic, dialogue, json.dumps(verdict))
                                    # Double write to Brain Vault
                                    save_ai_content('socratic', topic, dialogue, verdict)
                                    conn.execute('INSERT INTO notifications (user_id, title, message, type) VALUES (?, ?, ?, ?)',
                                                (1, "New Socratic Debate", f"A debate on {topic} is ready.", "debate"))
                                    conn.commit()

                            # 3. Neural Hash
                            elif action == "GENERATE_TOPIC_LINKAGES":
                                linkages_data = result.get('data') # Assuming execute_action returns structured data now
                                if not linkages_data and result.get('linkages'):
                                    # Backward compatibility if it returns simple list
                                    linkages_data = {'cross_linkages': result.get('linkages'), 'core_themes': []}

                                if linkages_data:
                                    from app.db_models.neural_hash import save_neural_hash_log
                                    save_neural_hash_log(topic, "brain_vault", linkages_data)
                                    # Double write to Brain Vault
                                    save_ai_content('neural_hash', topic, json.dumps(linkages_data))

                                    # Also save to main table
                                    conn.execute('INSERT INTO neural_hashes (topic, core_themes, examiner_pattern, cross_linkages) VALUES (?, ?, ?, ?)',
                                                (topic, 
                                                 json.dumps(linkages_data.get('core_themes', [])), 
                                                 linkages_data.get('examiner_pattern', ''), 
                                                 json.dumps(linkages_data.get('cross_linkages', []))))
                                    conn.commit()

                            # 4. Mind Map
                            elif action == "GENERATE_MIND_MAP":
                                content = result.get('mind_map_json') # Preferred JSON
                                if content:
                                    MindMapService.save_mindmap(f"{topic} Mind Map", content)
                                    # Double write to Brain Vault
                                    save_ai_content('mind_map', topic, json.dumps(content))
                                else:
                                    # Fallback if text
                                    text_content = result.get('mind_map')
                                    if text_content:
                                         conn.execute('INSERT INTO ai_generated_content (content_type, topic, content) VALUES (?, ?, ?)',
                                                ('mind_map', topic, text_content))
                                         conn.commit()

                            # 5. Essay Prompt
                            elif action == "GENERATE_ESSAY_PROMPT":
                                content = result.get('prompt')
                                if content:
                                    self._save_essay_prompt(topic, subject, content)
                                    save_ai_content('essay_prompt', topic, content)

                            # 6. Map Work
                            elif action == "GENERATE_MAP_WORK":
                                locations = result.get('locations')
                                if locations:
                                    content = json.dumps(locations)
                                    self._add_flashcard(user_id, topic, subject, f"Map Work Challenge: {topic}", content, 'auto_ai_mapwork', card_type='map_work')
                                    save_ai_content('map_work', topic, content)

                            # 7. Cheat Sheet & Mnemonics
                            elif action == "GENERATE_CHEAT_SHEET":
                                content = result.get('content')
                                if content:
                                    save_ai_content('cheat_sheet', topic, content)
                                    # Extract Mnemonics
                                    try:
                                        data = json.loads(content)
                                        for tab in data.get('tabs', []):
                                            if tab.get('id') == 'mnemonics':
                                                self._save_mnemonic(topic, tab.get('content'), 'text')
                                            if tab.get('id') == 'facts':
                                                # Save facts as revision card
                                                self._save_revision_note(topic, f"Quick Revision: {topic}", tab.get('content'))
                                    except: pass

                            # 8. Common Pitfalls
                            elif action == "FIND_COMMON_PITFALLS":
                                content = result.get('pitfalls')
                                if content:
                                    save_ai_content('pitfalls', topic, content)
                                    self._add_flashcard(user_id, topic, subject, f"Pitfalls: {topic}", content, 'auto_ai_pitfalls')

                            # 9. Other Content Types (Standard)
                            elif action in ["GENERATE_PODCAST_SCRIPT", "GENERATE_VISUAL_PROMPT", "GENERATE_ROLEPLAY_SCENARIO", "GENERATE_TIMELINE", "GENERATE_ELI5", "GENERATE_QUOTE_BANK"]:
                                # Mapping keys
                                key_map = {
                                    "GENERATE_PODCAST_SCRIPT": ("podcast", "script"),
                                    "GENERATE_VISUAL_PROMPT": ("visual_prompt", "prompt"),
                                    "GENERATE_ROLEPLAY_SCENARIO": ("roleplay", "scenario"),
                                    "GENERATE_TIMELINE": ("timeline", "timeline"),
                                    "GENERATE_ELI5": ("eli5", "explanation"),
                                    "GENERATE_QUOTE_BANK": ("quote_bank", "quotes")
                                }
                                c_type, key = key_map[action]
                                content = result.get(key)
                                if content:
                                    save_ai_content(c_type, topic, content)

                        print(f"Brain: ✅ Parallel Done & Saved -> {action}")
                except Exception as e:
                    print(f"Brain: ❌ Parallel Action {action} Failed: {e}")
                    traceback.print_exc()

            # Execute in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
                futures = [executor.submit(run_action_safe, action, payload) for action, payload in actions]
                concurrent.futures.wait(futures)
                
            print(f"Brain: 🏁 All parallel tasks completed for {topic}")

        except Exception as e:
            print(f"Brain: Task Completion Automation Failed: {e}")

    def _identify_book_for_topic(self, subject, topic):
        """Helper to find which book a topic belongs to."""
        try:
            books_path = os.path.join(os.getcwd(), 'app', 'data', 'books.json')
            if os.path.exists(books_path):
                with open(books_path, 'r') as f:
                    books = json.load(f)

                # Normalize string for comparison
                def normalize(s): return s.lower().replace(':', '').replace('-', ' ').strip()

                norm_topic = normalize(topic)

                for book in books:
                    if book.get('subject') == subject:
                        for chapter in book.get('chapters', []):
                            if normalize(chapter) in norm_topic or norm_topic in normalize(chapter):
                                return book.get('title')

                        # Also check if topic title matches book title (whole book review task)
                        if normalize(book.get('title')) in norm_topic:
                            return book.get('title')
        except Exception as e:
            print(f"Brain: Book identification error: {e}")
        return None

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
        
        # Mock Mode for Tests
        if self.is_lobotomized and action_type not in ["GENERATE_STUDY_PLAN", "SUMMON_BOSS", "RETRIEVE_FROM_PALACE", "TRIGGER_WATCHMAN", "SHOW_MORNING_BRIEFING", "SHOW_PANOPTICON", "CONSULT_GOLDEN_PATH"]:
             # ... (Keep existing mock logic for brevity, assuming it's safe)
             return {"success": True, "message": "Mock Action Executed (Lobotomized)"}

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
                    topic = payload.get('topic', None)
                    timeframe = payload.get('timeframe_days', 90)
                    predictions = foresight_engine.predict_questions(subject, timeframe, topic=topic)
                    
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

            elif action_type == "CONSTRUCT_PALACE":
                try:
                    from app.db import get_db
                    conn = get_db()
                    topic = payload.get('topic', 'General Knowledge')
                    
                    cursor = conn.execute('INSERT INTO mind_palace_locations (name, description, layout_type) VALUES (?, ?, ?)', 
                                        (f"The Hall of {topic}", f"A dedicated space for remembering {topic}", "hall"))
                    location_id = cursor.lastrowid
                    
                    brainstorm_prompt = f"""
                    # MISSION: MIND PALACE ARCHITECTURE
                    **Topic:** {topic}

                    **TASK:**
                    Create 5 vivid, bizarre, and memorable memory pegs (artifacts) for this topic.
                    Use the 'Loci Method' principles: Exaggeration, Absurdity, and Spatial Memory.

                    **OUTPUT SCHEMA (JSON Array):**
                    [
                        {{
                            "title": "Concept Name",
                            "content": "The vivid visual story. (e.g., 'A giant elephant eating the Constitution to represent Article 1...')",
                            "icon": "🐘"
                        }}
                    ]
                    """
                    response = model_manager.generate_content(brainstorm_prompt, model_type='pro')
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

            elif action_type == "CREATE_FLASHCARDS":
                try:
                    from app.services.flashcard_service import FlashcardService
                    topic = payload.get('topic', 'General')
                    count = payload.get('count', 5)
                    result = FlashcardService.generate_from_topic(topic, count)
                except Exception as e:
                    result = {"success": False, "message": f"Flashcard Generation Failed: {str(e)}"}

            elif action_type == "GENERATE_SOCRATIC_DIALOGUE":
                try:
                    from app.services.socratic_service import generate_autonomous_debate
                    topic = payload.get('topic', 'Philosophy')

                    # Generate a full autonomous debate (6 turns) with verdict
                    dialogue_text, history, verdict = generate_autonomous_debate(topic, turns=6)

                    result = {
                        "success": True,
                        "message": "Socratic Dialogue Generated.",
                        "dialogue": dialogue_text,
                        "verdict": verdict
                    }
                except Exception as e:
                    result = {"success": False, "message": f"Socratic Gen Failed: {str(e)}"}

            elif action_type == "GENERATE_ESSAY_PROMPT":
                try:
                    topic = payload.get('topic', '')
                    subject = payload.get('subject', '')
                    prompt = f"""
                    # MISSION: DESIGN A 'TRAP' ESSAY PROMPT (UPSC MAINS LEVEL)
                    **Topic:** {topic} ({subject})

                    **REQUIREMENTS:**
                    1. **The Prompt:** Must be abstract, philosophical, or multi-dimensional. Connect {topic} to Justice, Technology, or Human Nature.
                    2. **The Trap:** It should look simple but require deep nuance to score high.
                    3. **The Thesis Hint:** A 1-sentence "Golden Thread" argument.

                    **OUTPUT FORMAT:**
                    **Prompt:** "[The Prompt]"
                    **Thesis Hint:** [The specific angle to take]
                    **Micro-Syllabus:** [3 Bullet points on what to include]
                    """
                    response = model_manager.generate_content(prompt, model_type='pro')
                    result = {
                        "success": True,
                        "message": "Essay Prompt Generated.",
                        "prompt": response.text
                    }
                except Exception as e:
                    result = {"success": False, "message": f"Essay Gen Failed: {str(e)}"}

            elif action_type == "GENERATE_VISUAL_PROMPT":
                try:
                    topic = payload.get('topic', '')
                    prompt = f"""
                    Create a comprehensive 'Chapter Summary Infographic' text-to-image prompt for '{topic}'.
                    The prompt should describe a dense, high-resolution informational poster or digital illustration that covers ALL key concepts of the topic.
                    Include:
                    - Central theme visualization.
                    - Surroundings containing charts, icons, and symbolic representations of sub-topics.
                    - Color palette (e.g., 'Professional Blue & Gold', 'Historical Sepia').
                    - Style: 'Detailed Vector Art', 'Infographic Design', or 'Hyper-realistic Educational Poster'.
                    
                    Return ONLY the prompt text.
                    """
                    response = model_manager.generate_content(prompt, model_type='pro')
                    result = {
                        "success": True,
                        "message": "Visual Infographic Prompt Generated.",
                        "prompt": response.text
                    }
                except Exception as e:
                    result = {"success": False, "message": f"Visual Gen Failed: {str(e)}"}

            elif action_type == "GENERATE_ROLEPLAY_SCENARIO":
                try:
                    topic = payload.get('topic', '')
                    prompt = f"""
                    # MISSION: DISTRICT COLLECTOR CRISIS SIMULATION
                    **Context:** {topic}

                    **SCENARIO:**
                    You are the District Magistrate. A crisis related to {topic} has exploded.

                    **OUTPUT FORMAT:**
                    **🚨 THE INCIDENT:** [Visceral description of the event. High stakes.]
                    **👥 STAKEHOLDERS:** [Who is screaming at you? Politicians, Media, Mob, Victims.]
                    **⚖️ THE ETHICAL DILEMMA:** [Conflict between Rule of Law vs. Public Sentiment vs. Political Pressure.]
                    **⚡ DECISION MATRIX:**
                    - **Option A (The Bureaucrat):** Safe but slow.
                    - **Option B (The Cowboy):** Fast but illegal.
                    - **Option C (The Statesman):** The balanced (difficult) path.
                    """
                    response = model_manager.generate_content(prompt, model_type='pro')
                    result = {
                        "success": True,
                        "message": "Case Study Generated.",
                        "scenario": response.text
                    }
                except Exception as e:
                    result = {"success": False, "message": f"Roleplay Gen Failed: {str(e)}"}

            elif action_type == "GENERATE_MIND_MAP":
                try:
                    topic = payload.get('topic', '')
                    # Use MindMapService to generate structured JSON
                    mind_map_json = MindMapService.generate_mindmap(topic)
                    
                    result = {
                        "success": True,
                        "message": "Mind Map Generated.",
                        "mind_map_json": mind_map_json
                    }
                except Exception as e:
                    result = {"success": False, "message": f"Mind Map Gen Failed: {str(e)}"}

            elif action_type == "GENERATE_MAP_WORK":
                try:
                    topic = payload.get('topic', '')
                    prompt = f"""
                    # MISSION: GEOGRAPHICAL INTELLIGENCE
                    **Topic:** {topic}

                    Identify 5 CRITICAL locations associated with this topic.
                    Focus on: Strategic choke points, Resource deposits, Historical capitals, or Environmental hotspots.

                    **OUTPUT SCHEMA (JSON ONLY):**
                    [
                        {{
                            "name": "Name",
                            "lat": 0.0,
                            "lon": 0.0,
                            "reason": "Deep geographical/historical significance. Why does this place matter geopolitically?",
                            "question": "A challenging clue-based question (e.g., 'The gateway to the Red Sea...')"
                        }}
                    ]
                    """
                    response = model_manager.generate_content(prompt, model_type='pro')
                    data = self._parse_response(response.text)

                    locations = []
                    if isinstance(data, list):
                        locations = data

                    result = {
                        "success": True,
                        "message": "Map Work Generated.",
                        "locations": locations
                    }
                except Exception as e:
                    result = {"success": False, "message": f"Map Work Gen Failed: {str(e)}"}

            elif action_type == "GENERATE_TOPIC_LINKAGES":
                try:
                    topic = payload.get('topic', '')
                    related_topics = payload.get('related_topics', [])
                    prompt = f"""
                    # MISSION: INTERDISCIPLINARY SYNTHESIS (NEURAL HASH)
                    **Node A:** {topic}
                    **Node B List:** {', '.join(related_topics)}

                    **TASK:**
                    Connect {topic} to the list above using "First Principles".
                    Uncover hidden causal chains (Economy -> Society -> Polity).

                    **OUTPUT SCHEMA (JSON):**
                    {{
                        "core_themes": ["Theme A", "Theme B"],
                        "examiner_pattern": "Pattern of questions...",
                        "cross_linkages": ["Link 1", "Link 2"]
                    }}
                    """
                    response = model_manager.generate_content(prompt, model_type='pro')

                    data = self._parse_response(response.text)
                    if not data.get('cross_linkages'):
                         # Fallback if parsing failed but we got text
                         data = {'cross_linkages': [response.text], 'core_themes': []}

                    result = {
                        "success": True,
                        "message": "Linkages Generated.",
                        "data": data
                    }
                except Exception as e:
                    result = {"success": False, "message": f"Linkage Gen Failed: {str(e)}"}

            elif action_type == "GENERATE_CHEAT_SHEET":
                try:
                    topic = payload.get('topic', '')
                    prompt = f"""
                    # MISSION: ULTIMATE REVISION SHEET (LMR)
                    **Topic:** {topic}

                    **OBJECTIVE:** Create a high-density, low-fluff revision aid.

                    **OUTPUT SCHEMA (JSON):**
                    {{
                        "title": "{topic}",
                        "tabs": [
                            {{
                                "id": "facts",
                                "label": "⚡ Core DNA",
                                "content": "**Definitions**: Precise.\n**Data**: Latest stats.\n**Origin**: Historical context."
                            }},
                            {{
                                "id": "articles",
                                "label": "📜 Law & Consti",
                                "content": "Relevant Articles, Schedules, and Acts. Don't just list numbers, give the *essence*."
                            }},
                            {{
                                "id": "judgments",
                                "label": "⚖️ Jurisprudence",
                                "content": "Landmark SC Judgments (Case Name + Ratio Decidendi)."
                            }},
                            {{
                                "id": "examiner",
                                "label": "🧐 Examiner's Lens",
                                "content": "**Trap Areas**: Where students get confused.\n**High Yield Keywords**: Terms that fetch marks (e.g., 'Cooperative Federalism')."
                            }},
                            {{
                                "id": "interdisciplinary",
                                "label": "🌐 Linkages",
                                "content": "Connect {topic} to Economy, Ethics, and IR."
                            }},
                            {{
                                "id": "mnemonics",
                                "label": "🧠 Mnemonics",
                                "content": "Create a mnemonic for this topic."
                            }},
                            {{
                                "id": "concept_map",
                                "label": "🗺️ Neural Map",
                                "content": "graph TD; A[{topic}] --> B[Key Concept]; B --> C[Nuance];",
                                "type": "mermaid"
                            }},
                            {{
                                "id": "quiz",
                                "label": "❓ Active Recall",
                                "content": "JSON Array of 5 Objects: [{{ 'q': 'Scenario/Question', 'a': 'Specific Answer' }}]",
                                "type": "quiz"
                            }}
                        ]
                    }}
                    """
                    response = model_manager.generate_content(prompt, model_type='pro')
                    # Use _parse_response to handle JSON extraction safely
                    json_content = self._parse_response(response.text)

                    # Ensure it's stored as a stringified JSON for consistent DB storage
                    result = {
                        "success": True,
                        "message": "Cheat Sheet Generated.",
                        "content": json.dumps(json_content)
                    }
                except Exception as e:
                    result = {"success": False, "message": f"Cheat Sheet Gen Failed: {str(e)}"}

            elif action_type == "GENERATE_QUOTE_BANK":
                try:
                    topic = payload.get('topic', '')
                    prompt = f"""
                    Provide a high-quality Quote Bank and Data Sheet for '{topic}' suitable for UPSC Mains answers.
                    Structure:
                    1. **Quotes**: 3 impactful quotes by famous personalities/scholars. Include the Source.
                    2. **Data/Stats**: 3 key data points with Source (e.g. World Bank, NITI Aayog).
                    3. **Keywords**: 5 high-yield keywords to drop in answers.
                    
                    Format nicely with Markdown. 
                    """
                    response = model_manager.generate_content(prompt, model_type='pro')
                    # Simple splitting to separate quotes and data is hard without structured output
                    # Just return full text
                    text = response.text
                    quotes_part = "See below"
                    data_part = "See below"

                    # Try to split if labeled
                    if "Data:" in text:
                        parts = text.split("Data:")
                        quotes_part = parts[0].replace("Quotes:", "").strip()
                        data_part = parts[1].strip()
                    else:
                        quotes_part = text
                        data_part = ""

                    result = {
                        "success": True,
                        "message": "Quote Bank Generated.",
                        "quotes": response.text, # This field is legacy named 'quotes' but contains full rich text now
                        "data": "" # Deprecated, merged into quotes
                    }
                except Exception as e:
                    result = {"success": False, "message": f"Quote Bank Gen Failed: {str(e)}"}

            elif action_type == "GENERATE_TIMELINE":
                try:
                    topic = payload.get('topic', '')
                    prompt = f"""
                    # MISSION: NARRATIVE CHRONOLOGY
                    **Topic:** {topic}

                    **DIRECTIVE:**
                    Don't just list dates. Tell the *story* of cause and effect.

                    **FORMAT:**
                    **[Year]**: **[Event Name]**
                    -> *The Catalyst:* Why did this happen?
                    -> *The Aftermath:* What did it lead to?

                    Limit to 7-10 pivotal moments.
                    """
                    response = model_manager.generate_content(prompt, model_type='pro')
                    result = {
                        "success": True,
                        "message": "Timeline Generated.",
                        "timeline": response.text
                    }
                except Exception as e:
                    result = {"success": False, "message": f"Timeline Gen Failed: {str(e)}"}

            elif action_type == "GENERATE_ETHICS_DILEMMA":
                try:
                    topic = payload.get('topic', '')
                    prompt = f"""
                    # MISSION: ETHICAL CASE STUDY GENERATION
                    **Theme:** {topic}

                    **SCENARIO:**
                    Create a complex, grey-area case study for GS4 (Ethics).
                    - **Conflict:** Duty vs. Conscience vs. Law.
                    - **Stakes:** High (Life, death, or riot).
                    - **Nuance:** No easy answer. Both choices have negative consequences.

                    **OUTPUT:**
                    **Case:** [The Narrative]
                    **Ethical Issues:** [List of values in conflict]
                    **Options:** [Course of Action A vs B]
                    **Question:** "As the officer in charge, justify your course of action."
                    """
                    response = model_manager.generate_content(prompt, model_type='pro')
                    result = {
                        "success": True,
                        "message": "Dilemma Generated.",
                        "dilemma": response.text
                    }
                except Exception as e:
                    result = {"success": False, "message": f"Dilemma Gen Failed: {str(e)}"}

            elif action_type == "GENERATE_ELI5":
                try:
                    topic = payload.get('topic', '')
                    prompt = f"""
                    # MISSION: MULTI-LEVEL CONCEPT DECONSTRUCTION
                    **Topic:** {topic}

                    **OUTPUT SCHEMA (JSON ONLY):**
                    {{
                        "eli5": "Explain like I'm 5. Use a physical analogy (Lego, Pizza, Water).",
                        "eli15": "Explain like I'm 15. Connect to school subjects. No jargon.",
                        "eli_expert": "Explain to a PhD. Nuance, exceptions, and theoretical underpinnings.",
                        "analogy": "The 'Aha!' Moment Analogy. Totally distinct from the ELI5.",
                        "visual_analogy_prompt": "Midjourney Prompt: 'A surrealist painting of... --v 6.0'",
                        "real_world_example": "Where do we see {topic} in daily life? (Not a textbook example).",
                        "quiz": [
                            {{ "question": "Concept Check 1", "options": ["A", "B", "C"], "answer": "Correct Option" }},
                            {{ "question": "Concept Check 2", "options": ["A", "B", "C"], "answer": "Correct Option" }}
                        ]
                    }}
                    """
                    response = model_manager.generate_content(prompt, model_type='pro')
                    data = self._parse_response(response.text)

                    # Handle panic mode fallback
                    if data.get('error'):
                        data = {
                            "eli5": "The Brain is currently overwhelmed by high traffic (Quota Limit).",
                            "eli15": "Please review this topic manually or try again later.",
                            "eli_expert": "Service unavailable.",
                            "analogy": "Traffic Jam",
                            "visual_analogy_prompt": "A busy highway",
                            "real_world_example": "Server Overload",
                            "quiz": []
                        }

                    result = {
                        "success": True,
                        "message": "ELI5 Generated.",
                        "explanation": json.dumps(data), # Backward compatibility for some viewers
                        "data": data # New structured data
                    }
                except Exception as e:
                    result = {"success": False, "message": f"ELI5 Gen Failed: {str(e)}"}

            elif action_type == "FIND_COMMON_PITFALLS":
                try:
                    topic = payload.get('topic', '')
                    prompt = f"""
                    # MISSION: IDENTIFY LETHAL MISTAKES
                    **Topic:** {topic}

                    Identify 3 subtle but dangerous mistakes top students make in this topic.
                    Focus on: Nuance errors, Misinterpretation of terms, or Over-generalization.

                    **OUTPUT:**
                    1. **The Confusion:** [What they think] vs [What is true].
                    2. **The Example:** [A specific case/article].
                    3. **The Fix:** [How to remember correctly].
                    """
                    response = model_manager.generate_content(prompt, model_type='pro')
                    result = {"success": True, "pitfalls": response.text}
                except Exception as e:
                    result = {"success": False, "message": f"Pitfall search Failed: {str(e)}"}

            elif action_type == "ANALYZE_PYQ_TRENDS":
                try:
                    from app.db import get_db
                    conn = get_db()
                    filters = payload.get('filters', {})
                    topic_fallback = payload.get('topic')

                    # Construct query based on filters
                    query = "SELECT year, subject, topic, question_text FROM pyq_questions WHERE 1=1"
                    params = []

                    if filters.get('subject'):
                        query += " AND subject = ?"
                        params.append(filters['subject'])

                    if filters.get('year'):
                        query += " AND year = ?"
                        params.append(filters['year'])

                    if filters.get('topic'):
                        query += " AND topic LIKE ?"
                        params.append(f"%{filters['topic']}%")
                    elif topic_fallback:
                        query += " AND topic LIKE ?"
                        params.append(f"%{topic_fallback}%")

                    query += " ORDER BY year DESC LIMIT 50" # Analyze last 50 questions matching criteria

                    questions = conn.execute(query, params).fetchall()
                    questions_text = "\n".join([f"[{q['year']}] {q['topic']}: {q['question_text']}" for q in questions])

                    analysis_prompt = f"""
                    # MISSION: STRATEGIC INTELLIGENCE REPORT (SIR)
                    **Subject/Topic:** {filters.get('topic') or topic_fallback or 'General'}

                    **DATASET (PYQs):**
                    {questions_text}

                    **DIRECTIVE:**
                    You are the Chief Strategy Officer for a UPSC aspirant.
                    Decode the "Mind of the Examiner".

                    **OUTPUT FORMAT:**
                    **1. Thematic Heatmap:**
                    - List top 3 recurring micro-themes (e.g., "Not just Inflation, but specifically 'Headline vs Core Inflation'").

                    **2. Evolution Vector:**
                    - How has the question style changed? (e.g., "2015 was factual, 2023 is purely conceptual application").

                    **3. The 'Trap' Pattern:**
                    - Identify how they trick students (e.g., "Confusing Ministry X with Ministry Y").

                    **4. Next Year Prediction:**
                    - Based on this trajectory, what is the *exact* type of question likely to appear next?
                    """
                    # Trend analysis benefits from Pro
                    response = model_manager.generate_content(analysis_prompt, model_type='pro')
                    result = {
                        "success": True,
                        "message": "Trend Analysis Complete.",
                        "analysis": response.text
                    }
                except Exception as e:
                    result = {"success": False, "message": f"Trend Analysis Failed: {str(e)}"}

            elif action_type == "TRIANGULATE_TOPIC":
                try:
                    topic = payload.get('topic', '')
                    prompt = f"""
                    # MISSION: 360-DEGREE TRIANGULATION
                    **Target:** {topic}

                    **OBJECTIVE:**
                    Create a holistic "Theory of Everything" for this topic by connecting 3 distinct dimensions.

                    **OUTPUT SCHEMA (JSON-like text or Structured Markdown):**

                    **Dimension 1: The Anchor (Static Theory)**
                    - Historical origin or Constitutional Article.
                    - *Key Scholar/Judgment:* (e.g., "K.C. Wheare" or "Kesavananda Bharati").

                    **Dimension 2: The Pulse (Dynamic Current Affairs)**
                    - Why is this in news *right now*? (Last 12 months).
                    - Link to a specific report/index/event.

                    **Dimension 3: The Bridge (Interdisciplinary)**
                    - Connect it to a totally different GS paper (e.g., If Polity, link to Economy or Ethics).

                    **SYNTHESIS (The Golden Thread):**
                    - A powerful concluding paragraph merging all three.
                    """
                    response = model_manager.generate_content(prompt, model_type='pro')
                    result = {"success": True, "data": {"synthesis": response.text}}
                except Exception as e:
                    result = {"success": False, "message": f"Triangulation Failed: {str(e)}"}

            elif action_type == "DECODE_NEURAL_HASH":
                try:
                    topic = payload.get('topic', '')
                    prompt = f"""
                    # MISSION: DECODE THE NEURAL HASH
                    **Input:** {topic}

                    **TASK:**
                    Extract the "Hidden Syllabus" - the concepts examiners test but don't explicitly list.

                    **OUTPUT SCHEMA (JSON):**
                    {{
                        "core_themes": ["Theme 1 (The Obvious)", "Theme 2 (The Hidden)"],
                        "high_yield_keywords": ["Keyword 1", "Keyword 2"],
                        "examiner_pattern": "The mental model used to set questions on this (e.g. 'Focuses on exceptions to the rule').",
                        "potential_questions": [
                            {{ "type": "Conceptual", "question": "..." }},
                            {{ "type": "Applied", "question": "..." }}
                        ]
                    }}
                    """
                    response = model_manager.generate_content(prompt, model_type='pro')
                    data = self._parse_response(response.text)
                    result = {"success": True, "message": "Neural Hash Decoded.", "data": data}
                except Exception as e:
                    result = {"success": False, "message": f"Neural Hash Decode Failed: {str(e)}"}

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
            
            # 0. Check for Oracle Silence (Panic Mode)
            if "Oracle is silent" in text:
                return {"error": "Quota Exceeded", "is_fallback": True}

            # 1. Try to find JSON code block
            # 1. Robust JSON Scanner
            if text.startswith("```"):
                text = text.replace('```json', '').replace('```', '').strip()

            start = text.find('{')
            end = text.rfind('}')
            
            if start != -1 and end != -1:
                text = text[start:end+1]
            else:
                 # Fallback for strict regex if scanner fails (unlikely but safe)
                 pass 
            
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
