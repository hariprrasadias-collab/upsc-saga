from app.services.model_manager import model_manager
import json

class InterviewService:
    """
    PHASE 11: THE INTERVIEWER
    Simulates the UPSC Personality Test (Interview).
    """

    @staticmethod
    def generate_daf_questions(profile_json):
        """
        Generates interview questions based on the DAF (Detailed Application Form).
        profile_json: { "hometown": "Pune", "hobbies": ["Chess", "Trekking"], "education": "B.Tech" }
        """
        if not model_manager.is_configured:
            return []

        prompt = f"""
        # MISSION: DAF ANALYSIS (INTERVIEW BOARD)
        **Profile:**
        {json.dumps(profile_json, indent=2)}

        **DIRECTIVE:**
        Act as a seasoned UPSC Interview Board Member.
        Generate 5 probing questions based on this profile.

        **TYPES:**
        1. **Hometown:** Local issues, history.
        2. **Hobbies:** Technicalities, metaphors.
        3. **Education:** Application of degree in admin.
        4. **Situational:** Ethical dilemma.

        **OUTPUT SCHEMA (JSON Array):**
        [
            {{ "type": "Hometown", "question": "..." }},
            {{ "type": "Hobby", "question": "..." }}
        ]
        """

        try:
            response = model_manager.generate_content(prompt, model_type='pro')
            text = response.text.strip().replace('```json', '').replace('```', '')
            return json.loads(text)
        except Exception as e:
            print(f"DAF Gen Error: {e}")
            return []

    @staticmethod
    def evaluate_interview_answer(question, answer):
        """
        Evaluates a spoken/written answer for the interview.
        """
        if not model_manager.is_configured:
            return {"feedback": "AI Offline"}

        prompt = f"""
        # MISSION: INTERVIEW EVALUATION
        **Question:** "{question}"
        **Candidate Answer:** "{answer}"

        **DIRECTIVE:**
        Evaluate based on:
        1. **Clarity & Brevity** (Did they ramble?)
        2. **Balance** (Did they take a radical stand?)
        3. **Confidence** (implied tone).

        **OUTPUT SCHEMA (JSON):**
        {{
            "score": 0-10,
            "feedback": "...",
            "better_response": "..."
        }}
        """
        try:
            response = model_manager.generate_content(prompt, model_type='fast')
            text = response.text.strip().replace('```json', '').replace('```', '')
            return json.loads(text)
        except Exception:
            return {}

interview_service = InterviewService()
