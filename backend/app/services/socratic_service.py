import google.generativeai as genai
import os
import json
import random
import time
from dotenv import load_dotenv
from app.services.model_manager import model_manager

load_dotenv()

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

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
    },
    'iconoclast': {
        'name': 'Nietzsche',
        'role': 'The Iconoclast',
        'style': 'Challenges established values. Focuses on Will to Power. Critiques "slave morality" and conformity.',
        'focus': 'Power & Individualism'
    },
    'sage': {
        'name': 'Confucius',
        'role': 'The Harmonizer',
        'style': 'Focuses on social order, ritual (Li), family duty, and ethical leadership. Conservative and community-oriented.',
        'focus': 'Harmony & Duty'
    },
    'strategist': {
        'name': 'Machiavelli',
        'role': 'The Pragmatist',
        'style': 'Focuses on effectiveness, statecraft, and maintaining power. The ends justify the means. Coldly rational.',
        'focus': 'Realpolitik & Outcome'
    }
}

def generate_debate_turn(topic, history, user_input=None):
    if not GEMINI_API_KEY:
        return {
            "speakerId": "skeptic",
            "text": "My connection to the Muses is severed (Missing API Key).",
            "type": "error",
            "technique": "Silence",
            "fallacies": []
        }

    # model = get_model() # Removed in favor of model_manager
    
    # 1. Context Construction
    context_str = ""
    relevant_history = history[-10:] if len(history) > 10 else history
    for turn in relevant_history:
        speaker = turn.get('speakerId', 'unknown')
        name = AGENTS.get(speaker, {'name': 'User'}).get('name')
        text = turn.get('text', '')
        context_str += f"{name}: {text}\n"

    if user_input:
        context_str += f"User: {user_input}\n"

    # 2. The Moderator (Dynamic Speaker Selection & Scoring)
    agent_descriptions = "\n".join([f"{k}: {v['name']} ({v['role']})" for k, v in AGENTS.items()])

    moderator_prompt = f"""
    You are the Moderator of a high-stakes philosophical debate on "{topic}".
    
    AGENTS:
    {agent_descriptions}

    CONVERSATION SO FAR:
    {context_str}

    TASK:
    1. Analyze the Last Argument.
    2. Decide WHO should speak next.
       - Select the agent whose philosophy most directly CONFLICTS with the last point.
       - Do not let the same person speak twice in a row.
    3. Provide a "Secret Strategy" for the selected agent.

    Return JSON:
    {{
        "next_speaker_id": "skeptic" | "idealist" | "realist" | "iconoclast" | "sage" | "strategist",
        "strategy": "..."
    }}
    """
    
    try:
        mod_response = model_manager.generate_content(moderator_prompt, model_type='pro')
        text = mod_response.text.replace('```json', '').replace('```', '').strip()
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            text = text[start:end+1]

        mod_data = json.loads(text)
        
        next_speaker_id = mod_data.get('next_speaker_id', 'skeptic')
        strategy = mod_data.get('strategy', 'Question the premise.')

        if next_speaker_id not in AGENTS:
            next_speaker_id = random.choice(list(AGENTS.keys()))

    except Exception as e:
        print(f"Moderator Error: {e}")
        next_speaker_id = random.choice(list(AGENTS.keys()))
        strategy = "Respond relevantly."

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
    1. THINK: Identify fallacies or weak points in the previous speaker's argument (if any).
    2. TECHNIQUE: Name the rhetorical device you will use (e.g., Elenchus, Ad Hominem, Syllogism, Analogy, Aphorism, Dialectic).
    3. SPEAK: Keep it under 3 sentences. Be profound, challenging, and in-character.
    
    Return JSON:
    {{
        "thought_process": "I observe that...",
        "rhetorical_technique": "Name of technique",
        "detected_fallacies_in_prev_turn": ["Strawman", "Ad Hominem"] (or empty list),
        "text": "...",
        "type": "ARGUMENT" | "QUESTION" | "REBUTTAL"
    }}
    """

    try:
        response = model_manager.generate_content(agent_prompt, model_type='pro')
        text = response.text.strip()
        try:
            start_idx = text.find('{')
            end_idx = text.rfind('}')
            
            if start_idx != -1 and end_idx != -1:
                json_str = text[start_idx:end_idx+1]
                result = json.loads(json_str)
            else:
                result = {"text": text, "type": "ARGUMENT", "thought_process": "", "rhetorical_technique": "Direct Assertion", "detected_fallacies_in_prev_turn": []}
        except json.JSONDecodeError:
             result = {"text": text, "type": "ARGUMENT", "thought_process": "", "rhetorical_technique": "Direct Assertion", "detected_fallacies_in_prev_turn": []}
        
        return {
            "speakerId": next_speaker_id,
            "text": result.get('text', 'I am contemplating...'),
            "type": result.get('type', 'ARGUMENT'),
            "thoughts": result.get('thought_process', ''),
            "technique": result.get('rhetorical_technique', 'Rhetoric'),
            "fallacies": result.get('detected_fallacies_in_prev_turn', []),
            "timestamp": int(time.time() * 1000)
        }
    except Exception as e:
        print(f"Agent Error: {e}")
        return {
            "speakerId": next_speaker_id,
            "text": f"Error: {str(e)}",
            "type": "error",
            "technique": "System Failure",
            "fallacies": []
        }

def generate_autonomous_debate(topic, turns=6):
    """
    Generates a full multi-turn debate.
    Returns:
    1. JSON string of the full history (for DB storage in 'dialogue' column)
    2. Raw history list
    3. Verdict dict
    """
    if not GEMINI_API_KEY:
        return json.dumps([{"text": "System Offline", "speakerId": "skeptic"}]), [], {}

    history = []

    try:
        # model = get_model()
        starters = ['idealist', 'iconoclast', 'strategist', 'sage']
        starter_id = random.choice(starters)
        starter_agent = AGENTS[starter_id]

        # Initial turn
        resp = model_manager.generate_content(
            f"You are {starter_agent['name']}. Make a provocative opening statement about '{topic}' using a specific rhetorical technique.",
            model_type='pro'
        )
        history.append({
            "speakerId": starter_id,
            "text": resp.text.strip(),
            "type": "ARGUMENT",
            "technique": "Opening Statement",
            "fallacies": [],
            "timestamp": int(time.time() * 1000)
        })

        # Subsequent turns
        for _ in range(turns - 1):
            turn_data = generate_debate_turn(topic, history)
            history.append(turn_data)
            time.sleep(0.5)

        # Generate Verdict
        verdict = generate_debate_verdict(topic, history)

        # Return serialized JSON for storage
        return json.dumps(history), history, verdict

    except Exception as e:
        print(f"Autonomous Debate Error: {e}")
        return json.dumps([{"text": f"Error: {e}", "speakerId": "skeptic"}]), [], {}

def continue_autonomous_debate(topic, current_history, additional_turns=3):
    """
    Continues an existing debate for more turns.
    Returns: updated JSON string, updated history, new verdict.
    """
    if not GEMINI_API_KEY:
         return json.dumps(current_history), current_history, {}

    # Ensure history is list
    if isinstance(current_history, str):
        try:
            current_history = json.loads(current_history)
        except:
            current_history = []

    history = list(current_history)

    try:
        for _ in range(additional_turns):
            turn_data = generate_debate_turn(topic, history)
            history.append(turn_data)
            time.sleep(0.5)

        verdict = generate_debate_verdict(topic, history)
        return json.dumps(history), history, verdict

    except Exception as e:
        print(f"Continuation Error: {e}")
        return json.dumps(history), history, {}


def generate_debate_verdict(topic, history):
    """
    Analyzes a full debate history and provides a structured verdict.
    """
    if not GEMINI_API_KEY:
        return {}

    # model = get_model()

    transcript = ""
    for turn in history:
        speaker = turn.get('speakerId', 'unknown')
        name = AGENTS.get(speaker, {'name': 'Unknown'}).get('name')
        text = turn.get('text', '')
        technique = turn.get('technique', '')
        transcript += f"{name} ({technique}): {text}\n"

    judge_prompt = f"""
    You are Athena, the Goddess of Wisdom. You have observed a debate on "{topic}".

    TRANSCRIPT:
    {transcript}

    TASK:
    1. Identify the "Winner" (the agent who provided the most robust, logical, or impactful argument).
    2. Extract 3-5 Key Concepts (philosophical terms, fallacies, or ideas mentioned).
    3. Provide a "Synthesis" - a profound paragraph that reconciles the opposing views.
    4. Select the "Best Quote".
    5. Identify 1-2 "Mental Models" or "Frameworks" used.

    Return JSON:
    {{
        "winner": "Name of Agent",
        "key_concepts": ["concept1", "concept2", ...],
        "synthesis": "...",
        "best_quote": "...",
        "mental_models": ["model1", "model2"]
    }}
    """

    try:
        response = model_manager.generate_content(judge_prompt, model_type='pro')
        text = response.text.replace('```json', '').replace('```', '').strip()

        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            text = text[start:end+1]

        return json.loads(text)
    except Exception as e:
        print(f"Verdict Generation Error: {e}")
        return {
            "winner": "Undecided",
            "key_concepts": [],
            "synthesis": "Analysis failed.",
            "best_quote": ""
        }
