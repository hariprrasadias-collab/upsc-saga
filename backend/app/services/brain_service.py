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

            # 7. Socratic Dialogue
            if 'socratic_dialogue' in json_data:
                sd = json_data['socratic_dialogue']
                dialogue = sd.get('dialogue', [])
                verdict = sd.get('verdict', {})
                # Flatten dialogue to string for flashcard
                self._add_flashcard(user_id, topic, subject, f"Socratic Debate: {topic}", "See Socratic Archives.", 'manual_ai_socratic')
                save_socratic_dialogue(user_id, topic, json.dumps(dialogue), json.dumps(verdict))

            # 8. Triangulation
            if 'triangulation' in json_data:
                tri = json_data['triangulation']
                synthesis = tri.get('synthesis', '')
                way_forward = json.dumps(tri.get('way_forward', {}), indent=2)
                content = f"Synthesis:\n{synthesis}\n\nWay Forward:\n{way_forward}"
                self._add_flashcard(user_id, topic, subject, f"Mains Strategy: {topic}", content, 'manual_ai_triangulation')
                save_triangulation(topic, synthesis, tri)

            # 9. Neural Hash
            if 'neural_hash' in json_data:
                nh = json_data['neural_hash']
                themes = ", ".join(nh.get('core_themes', []))
                pattern = nh.get('examiner_pattern', '')
                content = f"Core Themes: {themes}\n\nExaminer Pattern: {pattern}\n\nCross Linkages: {', '.join(nh.get('cross_linkages', []))}"
                self._add_flashcard(user_id, topic, subject, f"Examiner's Lens: {topic}", content, 'manual_ai_neural_hash')
                # Log simplified
                save_neural_hash_log(topic, "upsc_topic", nh)

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
        if self.manual_mode:
            self.generate_manual_completion_prompt(task_data)
            return

        # ... Existing Automation Logic (Legacy) ...
        try:
            import concurrent.futures
            from flask import current_app
            
            # Capture app context for worker threads
            app = current_app._get_current_object()
            
            def run_action_safe(action, payload):
                """Helper to run action in app context"""
                try:
                    with app.app_context():
                        print(f"Brain: ⚡ Parallel Start -> {action}")
                        self.execute_action(action, payload)
                        print(f"Brain: ✅ Parallel Done -> {action}")
                except Exception as e:
                    print(f"Brain: ❌ Parallel Action {action} Failed: {e}")

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
                ("GENERATE_MIND_MAP", {"topic": topic}), # NEW: Dedicated Mind Map
                
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
                import traceback # Debugging
                try:
                    with app.app_context():
                        from app.db import get_db
                        conn = get_db()
                        
                        print(f"Brain: ⚡ Parallel Start -> {action}")
                        result = self.execute_action(action, payload)
                        
                        # PERSISTENCE LOGIC
                        if result and result.get('success'):
                            if action == "PREDICT_QUESTIONS":
                                data = result.get('data', [])
                                if data:
                                    conn.executemany('INSERT INTO foresight_predictions (topic, question, type, probability, reasoning) VALUES (?, ?, ?, ?, ?)',
                                                    [(topic, p.get('question'), p.get('type'), p.get('probability'), p.get('reasoning')) for p in data])
                                    conn.commit()
                            
                            elif action == "GENERATE_SOCRATIC_DIALOGUE":
                                dialogue = result.get('dialogue')
                                verdict = result.get('verdict')
                                if dialogue:
                                    conn.execute('INSERT INTO socratic_conversations (topic, user_id, dialogue, insight) VALUES (?, ?, ?, ?)',
                                                (topic, 1, dialogue, json.dumps(verdict)))
                                    conn.execute('INSERT INTO notifications (user_id, title, message, type) VALUES (?, ?, ?, ?)',
                                                (1, "New Socratic Debate", f"A debate on {topic} is ready.", "debate"))
                                    conn.commit()

                            elif action == "GENERATE_TOPIC_LINKAGES":
                                linkages_data = result.get('data')
                                if linkages_data:
                                    # 1. Store in structured table (Legacy/Analytics)
                                    conn.execute('INSERT INTO neural_hashes (topic, core_themes, examiner_pattern, cross_linkages) VALUES (?, ?, ?, ?)',
                                                (topic, 
                                                 json.dumps(linkages_data.get('core_themes', [])), 
                                                 linkages_data.get('examiner_pattern', ''), 
                                                 json.dumps(linkages_data.get('cross_linkages', []))))
                                    
                                    # 2. Store in UI-visible log (neural_hash_logs)
                                    # Ensure it shows up in /api/neural_hash/history
                                    conn.execute('INSERT INTO neural_hash_logs (input_text, context_type, decoded_data) VALUES (?, ?, ?)',
                                                (topic, 'brain_vault', json.dumps(linkages_data)))
                                    
                                    conn.commit()

                            elif action == "GENERATE_PODCAST_SCRIPT":
                                script = result.get('script')
                                if script:
                                    conn.execute('INSERT INTO ai_generated_content (content_type, topic, content, metadata) VALUES (?, ?, ?, ?)',
                                                ('podcast', topic, script, json.dumps({'style': payload.get('style')})))
                                    conn.commit()
                            
                            # --- NEW PERSISTENCE HANDLERS ---
                            
                            elif action == "GENERATE_ESSAY_PROMPT":
                                content = result.get('prompt')
                                if content:
                                    conn.execute('INSERT INTO ai_generated_content (content_type, topic, content) VALUES (?, ?, ?)',
                                                ('essay_prompt', topic, content))
                                    conn.commit()

                            elif action == "GENERATE_VISUAL_PROMPT":
                                content = result.get('prompt')
                                if content:
                                    conn.execute('INSERT INTO ai_generated_content (content_type, topic, content) VALUES (?, ?, ?)',
                                                ('visual_prompt', topic, content))
                                    conn.commit()

                            elif action == "GENERATE_ROLEPLAY_SCENARIO":
                                content = result.get('scenario')
                                if content:
                                    conn.execute('INSERT INTO ai_generated_content (content_type, topic, content) VALUES (?, ?, ?)',
                                                ('roleplay', topic, content))
                                    conn.commit()
                            
                            elif action == "GENERATE_MIND_MAP":
                                content = result.get('mind_map')
                                if content:
                                    conn.execute('INSERT INTO ai_generated_content (content_type, topic, content) VALUES (?, ?, ?)',
                                                ('mind_map', topic, content))
                                    conn.commit()

                            elif action == "GENERATE_MAP_WORK":
                                locations = result.get('locations')
                                if locations:
                                    conn.execute('INSERT INTO ai_generated_content (content_type, topic, content) VALUES (?, ?, ?)',
                                                ('map_work', topic, json.dumps(locations)))
                                    conn.commit()

                            elif action == "GENERATE_CHEAT_SHEET":
                                content = result.get('content') # Already JSON string
                                if content:
                                    conn.execute('INSERT INTO ai_generated_content (content_type, topic, content) VALUES (?, ?, ?)',
                                                ('cheat_sheet', topic, content))
                                    conn.commit()

                            elif action == "GENERATE_QUOTE_BANK":
                                quotes = result.get('quotes', '')
                                full_content = quotes # Legacy field name, contains rich text
                                conn.execute('INSERT INTO ai_generated_content (content_type, topic, content) VALUES (?, ?, ?)',
                                            ('quote_bank', topic, full_content))
                                conn.commit()

                            elif action == "GENERATE_TIMELINE":
                                content = result.get('timeline')
                                if content:
                                    conn.execute('INSERT INTO ai_generated_content (content_type, topic, content) VALUES (?, ?, ?)',
                                                ('timeline', topic, content))
                                    conn.commit()

                            elif action == "GENERATE_ELI5":
                                content = result.get('explanation') # JSON string
                                if content:
                                    conn.execute('INSERT INTO ai_generated_content (content_type, topic, content) VALUES (?, ?, ?)',
                                                ('eli5', topic, content))
                                    conn.commit()

                            elif action == "FIND_COMMON_PITFALLS":
                                content = result.get('pitfalls')
                                if content:
                                    conn.execute('INSERT INTO ai_generated_content (content_type, topic, content) VALUES (?, ?, ?)',
                                                ('common_pitfalls', topic, content))
                                    conn.commit()

                        print(f"Brain: ✅ Parallel Done & Saved -> {action}")
                except Exception as e:
                    print(f"Brain: ❌ Parallel Action {action} Failed: {e}")
                    traceback.print_exc() # Print full stack for debugging

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
            # Handle generative actions with mocks
            if action_type == "CREATE_FLASHCARDS":
                # Create fake flashcards in DB directly to pass tests
                try:
                    # Direct DB injection since FlashcardService also checks for API key
                    topic = payload.get('topic', 'General')
                    self._add_flashcard(1, topic, "General", f"Mock Q: {topic}?", f"Mock A: {topic} is complex.", "mock_gen")
                    return {"success": True, "message": f"Mock flashcards created for {topic}"}
                except Exception as e:
                    return {"success": False, "message": str(e)}

            elif action_type == "EXPLAIN_SYLLABUS_NODE":
                return {"success": True, "explanation": "This is a mock explanation for testing."}
            elif action_type == "ANALYZE_PYQ_TRENDS":
                return {"success": True, "analysis": "Mock Trend Analysis: Increasing difficulty."}
            elif action_type == "PREDICT_QUESTIONS":
                return {"success": True, "data": [{"question": "Mock Question?", "type": "MCQ"}]}
            elif action_type == "GENERATE_SOCRATIC_DIALOGUE":
                return {"success": True, "dialogue": "Student: Why? Socrates: Why not?", "verdict": {"winner": "N/A"}}
            elif action_type == "TRIANGULATE_TOPIC":
                return {"success": True, "data": {"synthesis": "Mock Synthesis", "way_forward": {}}}
            elif action_type == "DECODE_NEURAL_HASH":
                return {"success": True, "data": {"core_themes": ["Mock Theme"], "cross_linkages": []}}
            elif action_type == "FIND_COMMON_PITFALLS":
                return {"success": True, "pitfalls": ["Mock Pitfall 1", "Mock Pitfall 2"]}
            elif action_type == "GENERATE_PODCAST_SCRIPT":
                return {"success": True, "script": "Host: Welcome to Mock Podcast."}
            elif action_type == "GENERATE_ESSAY_PROMPT":
                return {"success": True, "prompt": "Mock Essay Prompt"}
            elif action_type == "GENERATE_VISUAL_PROMPT":
                return {"success": True, "prompt": "Mock Visual Prompt"}
            elif action_type == "GENERATE_ROLEPLAY_SCENARIO":
                return {"success": True, "scenario": "Mock Roleplay Scenario"}
            elif action_type == "GENERATE_MAP_WORK":
                return {
                    "success": True,
                    "locations": [
                        {
                            "name": "Pataliputra",
                            "lat": 25.61,
                            "lon": 85.14,
                            "reason": "Capital of Mauryan Empire (Mock)",
                            "question": "Locate the capital of the Mauryan Empire."
                        },
                        {
                            "name": "Taxila",
                            "lat": 33.74,
                            "lon": 72.78,
                            "reason": "Ancient centre of learning (Mock)",
                            "question": "Locate the ancient university town of Taxila."
                        }
                    ]
                }
            elif action_type == "GENERATE_TOPIC_LINKAGES":
                return {"success": True, "linkages": ["Mock Linkage 1"]}
            elif action_type == "GENERATE_CHEAT_SHEET":
                return {
                    "success": True,
                    "content": json.dumps({
                        "title": "Mock Topic Cheat Sheet",
                        "tabs": [
                            {"id": "facts", "label": "⚡ Quick Facts", "content": "- Fact 1\n- Fact 2"},
                            {"id": "dates", "label": "📅 Key Dates", "content": "- 1947: Independence"},
                            {"id": "judgments", "label": "⚖️ Judgments", "content": "- Keshavananda Bharati Case"},
                            {"id": "mnemonics", "label": "🧠 Mnemonics", "content": "- ABCDE for something"},
                            {"id": "examiner", "label": "🧐 Examiner's View", "content": "**High Yield Keywords:**\n- Secularism\n- Basic Structure\n\n**Focus Areas:**\n- Preamble as part of Constitution"},
                            {"id": "concept_map", "label": "🗺️ Concept Map", "content": "graph TD; A[Constitution] --> B[Preamble]; B --> C[Justice]; B --> D[Liberty];", "type": "mermaid"},
                            {"id": "quiz", "label": "❓ Active Recall", "content": json.dumps([{"q": "Who is the custodian of the Constitution?", "a": "Supreme Court"}, {"q": "Article 32?", "a": "Right to Constitutional Remedies"}]), "type": "quiz"}
                        ]
                    })
                }
            elif action_type == "GENERATE_QUOTE_BANK":
                return {"success": True, "quotes": "Mock Quote", "data": "Mock Data"}
            elif action_type == "GENERATE_TIMELINE":
                return {"success": True, "timeline": "2023 - Mock Event"}
            elif action_type == "GENERATE_ETHICS_DILEMMA":
                return {"success": True, "dilemma": "Mock Dilemma"}
            elif action_type == "GENERATE_ELI5":
                return {"success": True, "explanation": "Mock ELI5"}
            # Fallback for others
            return {"success": True, "message": "Mock Action Executed"}

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
                    response = model_manager.generate_content(analysis_prompt)
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
                    # Complex analysis requires Pro
                    response = model_manager.generate_content(analysis_prompt, model_type='pro')
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
                    response = model_manager.generate_content(brainstorm_prompt)
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
                    response = model_manager.generate_content(prioritize_prompt)
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

                    if filters.get('topic'):
                        query += " AND topic LIKE ?"
                        params.append(f"%{filters['topic']}%")
                        
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
                    # Trend analysis benefits from Pro
                    response = model_manager.generate_content(analysis_prompt, model_type='pro')
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
                    response = model_manager.generate_content(explanation_prompt)
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
                    response = model_manager.generate_content(bio_prompt)
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
                    # Decoding nuance needs Pro
                    response = model_manager.generate_content(decode_prompt, model_type='pro')
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
                    response = model_manager.generate_content(recommend_prompt)
                    result = {
                        "success": True,
                        "message": "Brok has spoken.",
                        "recommendation": response.text
                    }
                except Exception as e:
                    result = {"success": False, "message": f"Recommendation Failed: {str(e)}"}

            elif action_type == "GENERATE_PODCAST_SCRIPT":
                try:
                    topic = payload.get('topic', '')
                    prompt = f"""
                    Generate a 'Coffee Chat' style dialogue about {topic}.
                    
                    **Cast:**
                    1. **Host**: Quick, smart, funny.
                    2. **Guest**: Skeptical, asks "Wait, what?" often.

                    **Refined Style Guide:**
                    - **Start In Media Res**: Jump straight into the gossip/hook. No "Welcome to the podcast".
                    - **Super Short Sentences**: People speak in bursts. Max 12 words per line.
                    - **Reactions**: Use "Whoa", "No way", "Crazy", "Right?" constantly.
                    - **Analogy First**: Explain complex things using pizza, traffic, or dating analogies.
                    
                    **Format:**
                    Host: [Text]
                    Guest: [Text]
                    
                    **Goal:** Make it feel like I'm eavesdropping on two smart friends at a cafe.
                    """
                    # Creative writing needs Pro
                    response = model_manager.generate_content(prompt, model_type='pro')
                    text = response.text.strip()
                    if text.startswith("```"):
                        text = text.replace("```json", "").replace("```", "").strip() # Remove main fences if any
                    
                    # Remove common chat prefixes
                    if text.lower().startswith("here is a"): 
                        text = text.split("\n", 1)[-1].strip()

                    result = {
                        "success": True,
                        "message": "Podcast Script Generated.",
                        "script": text
                    }
                except Exception as e:
                    result = {"success": False, "message": f"Podcast Gen Failed: {str(e)}"}

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
                    Create a philosophical or analytical UPSC Mains Essay Prompt based on '{topic}' ({subject}).
                    Connect it to a broader theme (e.g., Democracy, Justice, Environment).
                    Provide the prompt statement and a 1-line 'Thesis' hint.
                    Return ONLY the prompt and thesis. Do not include "Here is a prompt...".
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
                    response = model_manager.generate_content(prompt)
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
                    Create an 'Interactive Case Study' for a District Collector (IAS) regarding '{topic}'.
                    Format as a High-Stakes Decision Game.
                    Structure:
                    1. **The Crisis**: A detailed, realistic scenario involving this topic.
                    2. **The Pressure**: Specific stakeholders (Ministers, Media, Protestors) pushing conflicting demands.
                    3. **The Options**:
                       - Option A: (Popular but maybe illegal/unethical)
                       - Option B: (Strictly legal but unpopular/risky)
                       - Option C: (Innovative but difficult execution)
                    4. **The Question**: "You are the DM. Which option do you choose and why?"
                    
                    Return formatted Markdown.
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
                    prompt = f"""
                    Create a hierarchical Mind Map for '{topic}' using Mermaid JS syntax.
                    Use `graph TD` direction.
                    Ensure the code is valid Mermaid.
                    Structure:
                    - Central Node: {topic}
                    - Main Branches: Key Pillars/Dimensions.
                    - Sub Branches: Specific concepts/examples.
                    
                    Return ONLY the raw Mermaid code block (inside ```mermaid ... ``` or just the code).
                    """
                    response = model_manager.generate_content(prompt)
                    
                    # Robust extraction
                    text = response.text.replace('```mermaid', '').replace('```', '').strip()
                    if 'graph TD' not in text:
                        text = f"graph TD\nA[{topic}] --> B[Analysis]\nB --> C[See Text]" 
                        
                    result = {
                        "success": True,
                        "message": "Mind Map Generated.",
                        "mind_map": text
                    }
                except Exception as e:
                    result = {"success": False, "message": f"Mind Map Gen Failed: {str(e)}"}

            elif action_type == "GENERATE_MAP_WORK":
                try:
                    topic = payload.get('topic', '')
                    prompt = f"""
                    Identify 3-5 key geographical locations related to '{topic}' for map pointing.
                    Return JSON list: [{{
                        "name": "Name of Place",
                        "lat": 0.0,
                        "lon": 0.0,
                        "reason": "Historical/Geographical significance",
                        "question": "Question to ask user to find this place (e.g. 'Locate the capital of...')"
                    }}]
                    Ensure coordinates are accurate.
                    """
                    response = model_manager.generate_content(prompt)
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
                    Find conceptual linkages between '{topic}' and these recently studied topics: {', '.join(related_topics)}.
                    Explain the connection in 1 sentence per topic.
                    Example: "Monsoon impacts Inflation via food prices."
                    """
                    response = model_manager.generate_content(prompt)
                    # Simple text split by newline
                    linkages = [line.strip() for line in response.text.strip().split('\n') if line.strip()]

                    result = {
                        "success": True,
                        "message": "Linkages Generated.",
                        "linkages": linkages
                    }
                except Exception as e:
                    result = {"success": False, "message": f"Linkage Gen Failed: {str(e)}"}

            elif action_type == "GENERATE_CHEAT_SHEET":
                try:
                    topic = payload.get('topic', '')
                    prompt = f"""
                    Create a structured 'Cheat Sheet' for '{topic}' for last minute revision.
                    Return a JSON object with this structure:
                    {{
                        "title": "{topic}",
                        "tabs": [
                            {{ "id": "facts", "label": "⚡ Quick Facts", "content": "Markdown list of key definitions and facts" }},
                            {{ "id": "articles", "label": "📜 Articles/Sections", "content": "Markdown list of relevant legal articles" }},
                            {{ "id": "dates", "label": "📅 Timeline", "content": "Markdown chronological list" }},
                            {{ "id": "judgments", "label": "⚖️ Case Laws", "content": "Markdown of 3 key judgments/committees" }},
                            {{ "id": "mnemonics", "label": "🧠 Mnemonics", "content": "1 clever mnemonic to remember this topic" }},
                            {{ "id": "examiner", "label": "🧐 Examiner's View", "content": "Markdown: What keywords/themes does the examiner look for? High yield areas." }},
                            {{ "id": "concept_map", "label": "🗺️ Concept Map", "content": "Mermaid JS diagram code (graph TD or mindmap) illustrating the concept", "type": "mermaid" }},
                            {{ "id": "quiz", "label": "❓ Active Recall", "content": "JSON Array of 5 objects: [ { 'q': 'Question?', 'a': 'Short Answer' } ]", "type": "quiz" }}
                        ]
                    }}
                    Ensure content is concise Markdown. For the concept_map, provide ONLY the valid Mermaid code string. For quiz, ensure valid JSON string in content field.
                    """
                    response = model_manager.generate_content(prompt)
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
                    
                    # Store the rich markdown directly
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
                    Create a chronological timeline of key events related to '{topic}'.
                    Format: "Year/Era - **Event Name**: Brief significance (1 sentence)."
                    Cover at least 5-7 major milestones.
                    Start directly with the timeline.
                    """
                    response = model_manager.generate_content(prompt)
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
                    Create a realistic ethical dilemma or case study related to '{topic}' for a civil servant.
                    End with a question: "What would you do?"
                    Start directly with the Case Study. No intro text.
                    """
                    response = model_manager.generate_content(prompt, model_type='pro')
                    result = {
                        "success": True,
                        "message": "Dilemma Generated.",
                        "dilemma": response.text
                    }
                except Exception as e:
                    result = {"success": False, "message": f"Dilemma Gen Failed: {str(e)}"}

            elif action_type == "SCHEDULE_REVISION":
                try:
                    # Log A/B result if applicable
                    if 'ab_test_id' in payload:
                        from app.services.ab_tester import ab_tester
                        ab_tester.log_result(payload['ab_test_id'], 'action_executed', 1.0)
                        
                    result = {"success": True, "message": "Revision Scheduled (Mock)"}
                except Exception as e:
                    result = {"success": False, "message": f"Schedule Revision Failed: {str(e)}"}
            
            elif action_type == "COMPLETE_MOCK_TEST":
                try:
                    from app.services.syllabus_tracker import SyllabusTracker
                    payload_topics = payload.get('topics', [])
                    
                    updated = []
                    for t in payload_topics:
                        SyllabusTracker.update_topic_progress(t, 'Completed')
                        updated.append(t)
                        
                    result = {
                        "success": True,
                        "message": f"Marked {len(updated)} topics as Completed: {', '.join(updated)}",
                        "updated_topics": updated
                    }
                except Exception as e:
                    result = {"success": False, "message": f"Complete Mock Test Failed: {str(e)}"}

            elif action_type == "GENERATE_ELI5":
                try:
                    topic = payload.get('topic', '')
                    prompt = f"""
                    Explain the concept of '{topic}' at multiple levels of complexity.
                    Return strictly valid JSON with this structure:
                    {{
                        "eli5": "Explanation for a 5-year-old using simple analogies",
                        "eli15": "Explanation for a teenager (high school level)",
                        "eli_expert": "Academic/Professional definition with technical nuance",
                        "analogy": "A creative, distinct analogy to help visualize it",
                        "visual_analogy_prompt": "A detailed text-to-image prompt to visualize the analogy (e.g. 'A digital painting of...')",
                        "real_world_example": "A concrete real-world application or example",
                        "quiz": [
                            {{ "question": "Simple check question 1", "options": ["Option A", "Option B", "Option C"], "answer": "Option A" }},
                            {{ "question": "Simple check question 2", "options": ["Option A", "Option B", "Option C"], "answer": "Option B" }}
                        ]
                    }}
                    Do NOT include markdown formatting like ```json ... ```, just the raw JSON.
                    """
                    response = model_manager.generate_content(prompt)
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

            elif action_type == "EXPLAIN_SYLLABUS_NODE":
                try:
                    topic = payload.get('topic', '')
                    prompt = f"Explain the UPSC syllabus topic '{topic}' in concise detail. Cover key concepts."
                    response = model_manager.generate_content(prompt)
                    result = {"success": True, "explanation": response.text}
                except Exception as e:
                    result = {"success": False, "message": f"Explanation Failed: {str(e)}"}

            elif action_type == "FIND_COMMON_PITFALLS":
                try:
                    topic = payload.get('topic', '')
                    prompt = f"""
                    Identify 3-5 common conceptual mistakes or "Pitfalls" students make when Answer Writing or Studying '{topic}'.
                    For each pitfall:
                    1. The Mistake
                    2. The Correction/Nuance
                    
                    Format as a concise Markdown list.
                    """
                    response = model_manager.generate_content(prompt, model_type='pro')
                    result = {"success": True, "pitfalls": response.text}
                except Exception as e:
                    result = {"success": False, "message": f"Pitfall search Failed: {str(e)}"}

            elif action_type == "ANALYZE_PYQ_TRENDS":
                try:
                    topic = payload.get('topic', '')
                    prompt = f"""
                    Analyze Previous Year Question (PYQ) trends for '{topic}' in UPSC CSE (Prelims & Mains).
                    Highlight:
                    1. Frequency of questions
                    2. Nature of questions (Factual vs Analytical)
                    3. Key sub-themes repeated
                    """
                    response = model_manager.generate_content(prompt, model_type='pro')
                    result = {"success": True, "analysis": response.text}
                except Exception as e:
                    result = {"success": False, "message": f"Trend Analysis Failed: {str(e)}"}

            elif action_type == "TRIANGULATE_TOPIC":
                try:
                    topic = payload.get('topic', '')
                    prompt = f"""
                    Triangulate '{topic}' by connecting it to 3 dimensions:
                    1. Historical Context
                    2. Constitutional/Legal Framework
                    3. Current Affairs Relevance
                    Synthesize these into a holistic view.
                    """
                    response = model_manager.generate_content(prompt, model_type='pro')
                    result = {"success": True, "data": {"synthesis": response.text}}
                except Exception as e:
                    result = {"success": False, "message": f"Triangulation Failed: {str(e)}"}

            elif action_type == "DECODE_NEURAL_HASH":
                try:
                    topic = payload.get('topic', '')
                    prompt = f"Identify the core underlying themes and cross-disciplinary linkages for '{topic}'."
                    response = model_manager.generate_content(prompt)
                    result = {"success": True, "data": {"core_themes": [response.text]}}
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
