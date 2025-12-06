import google.generativeai as genai
import os
import json
import random
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

AGENTS = {
    'skeptic': {
        'name': 'Socrates',
        'role': 'The Skeptic',
        'style': 'Relentless questioning. Exposes contradictions (Elenchus). Never accepts a premise without definition.',
        'focus': 'Logic & Definitions'
    },
    'idealist': {
        'name': 'Plato',
        'role': 'The Idealist',
        'style': 'Focuses on the "Form" of the Good. Abstract, moralizing, visionary. Concerned with what OUGHT to be.',
        'focus': 'Morality & Vision'
    },
    'realist': {
        'name': 'Aristotle',
        'role': 'The Realist',
        'style': 'Empirical, practical, systematic. Categorizes arguments. Concerned with what IS and what is FEASIBLE.',
        'focus': 'Evidence & Pragmatism'
    }
}

def get_model():
    """Returns the best available model with fallback."""
    try:
        return genai.GenerativeModel('gemini-2.0-flash-001')
    except:
        return genai.GenerativeModel('gemini-2.0-flash-001')

def generate_debate_turn(topic, history, user_input=None):
    if not GEMINI_API_KEY:
        return {
            "speakerId": "skeptic",
            "text": "My connection to the Muses is severed (Missing API Key).",
            "type": "error"
        }

    model = get_model()
    
    # 1. Context Construction
    context_str = ""
    for turn in history[-6:]:
        speaker = turn.get('speakerId', 'unknown')
        name = AGENTS.get(speaker, {'name': 'User'}).get('name')
        text = turn.get('text', '')
        context_str += f"{name}: {text}\n"

    if user_input:
        context_str += f"User: {user_input}\n"

    # 2. The Moderator (Dynamic Speaker Selection & Scoring)
    # We ask the model to act as a "Debate Moderator" first to analyze the state.
    
    moderator_prompt = f"""
    You are the Moderator of a high-stakes philosophical debate on "{topic}".
    
    AGENTS:
    1. Socrates (Skeptic): Attacks logic/definitions.
    2. Plato (Idealist): Attacks lack of vision/morality.
    3. Aristotle (Realist): Attacks lack of evidence/feasibility.

    CONVERSATION SO FAR:
    {context_str}

    TASK:
    1. Analyze the User's last argument (if any). Score it (0-10) on Logic, Relevance, and Impact.
    2. Decide WHO should speak next to best challenge the User or advance the debate.
       - If User was vague -> Socrates.
       - If User was cynical/pragmatic -> Plato.
       - If User was overly idealistic -> Aristotle.
    3. Provide a "Secret Strategy" for the selected agent.

    Return JSON:
    {{
        "user_score": {{ "logic": 0, "relevance": 0, "impact": 0 }},
        "next_speaker_id": "skeptic" | "idealist" | "realist",
        "strategy": "..."
    }}
    """
    
    try:
        mod_response = model.generate_content(moderator_prompt)
        mod_data = json.loads(mod_response.text.replace('```json', '').replace('```', '').strip())
        
        next_speaker_id = mod_data.get('next_speaker_id', 'skeptic')
        strategy = mod_data.get('strategy', 'Question the premise.')
        user_score = mod_data.get('user_score', {})
    except Exception as e:
        print(f"Moderator Error: {e}")
        next_speaker_id = random.choice(list(AGENTS.keys()))
        strategy = "Respond relevantly."
        user_score = {}

    # 3. The Agent (Generation with Chain of Thought)
    agent = AGENTS[next_speaker_id]
    
    agent_prompt = f"""
    You are {agent['name']} ({agent['role']}).
    Topic: {topic}
    
    YOUR PERSONA: {agent['style']}
    YOUR FOCUS: {agent['focus']}
    
    MODERATOR'S INSTRUCTION: {strategy}
    
    CONVERSATION:
    {context_str}
    
    TASK:
    Generate your response.
    1. First, THINK silently about the user's argument. Identify fallacies or weak points.
    2. Then, SPEAK. Keep it under 3 sentences. Be profound, challenging, and in-character.
    
    Return JSON:
    {{
        "thought_process": "I observe that the user...",
        "text": "...",
        "type": "ARGUMENT" | "QUESTION" | "REBUTTAL"
    }}
    """

    try:
        response = model.generate_content(agent_prompt)
        text = response.text.strip()
        # Robust JSON extraction
        try:
            # Find the first '{' and last '}'
            start_idx = text.find('{')
            end_idx = text.rfind('}')
            
            if start_idx != -1 and end_idx != -1:
                json_str = text[start_idx:end_idx+1]
                result = json.loads(json_str)
            else:
                # Fallback if no JSON found
                print(f"No JSON found in response: {text}")
                result = {"text": text, "type": "ARGUMENT", "thought_process": "I spoke without thinking structure."}
        except json.JSONDecodeError:
             print(f"JSON Decode Error. Raw text: {text}")
             result = {"text": text, "type": "ARGUMENT", "thought_process": "My thoughts are unstructured."}
        
        return {
            "speakerId": next_speaker_id,
            "text": result.get('text', 'I am contemplating...'),
            "type": result.get('type', 'ARGUMENT'),
            "thoughts": result.get('thought_process', ''),
            "score": user_score,
            "timestamp": 0
        }
    except Exception as e:
        print(f"Agent Error: {e}")
        return {
            "speakerId": next_speaker_id,
            "text": f"The complexity of this argument eludes me for a moment. (AI Error: {str(e)})",
            "type": "ARGUMENT",
            "thoughts": f"System failure: {str(e)}",
            "score": {},
            "timestamp": 0
        }
