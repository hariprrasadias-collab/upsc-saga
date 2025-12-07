import google.generativeai as genai
import os
import json
import random
import time
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
    # Look deeper into history for context
    relevant_history = history[-10:] if len(history) > 10 else history
    for turn in relevant_history:
        speaker = turn.get('speakerId', 'unknown')
        name = AGENTS.get(speaker, {'name': 'User'}).get('name')
        text = turn.get('text', '')
        context_str += f"{name}: {text}\n"

    if user_input:
        context_str += f"User: {user_input}\n"

    # 2. The Moderator (Dynamic Speaker Selection & Scoring)
    # We ask the model to act as a "Debate Moderator" first to analyze the state.
    
    agent_descriptions = "\n".join([f"{k}: {v['name']} ({v['role']})" for k, v in AGENTS.items()])

    moderator_prompt = f"""
    You are the Moderator of a high-stakes philosophical debate on "{topic}".
    
    AGENTS:
    {agent_descriptions}

    CONVERSATION SO FAR:
    {context_str}

    TASK:
    1. Analyze the Last Argument (by User or Agent). Score it (0-10) on Logic, Relevance, and Impact.
    2. Decide WHO should speak next to best challenge the argument or advance the debate.
       - Select the agent whose philosophy most directly CONFLICTS with the last point.
       - Do not let the same person speak twice in a row.
    3. Provide a "Secret Strategy" for the selected agent.

    Return JSON:
    {{
        "user_score": {{ "logic": 0, "relevance": 0, "impact": 0 }},
        "next_speaker_id": "skeptic" | "idealist" | "realist" | "iconoclast" | "sage" | "strategist",
        "strategy": "..."
    }}
    """
    
    try:
        mod_response = model.generate_content(moderator_prompt)
        text = mod_response.text.replace('```json', '').replace('```', '').strip()
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            text = text[start:end+1]

        mod_data = json.loads(text)
        
        next_speaker_id = mod_data.get('next_speaker_id', 'skeptic')
        strategy = mod_data.get('strategy', 'Question the premise.')
        user_score = mod_data.get('user_score', {})

        # Fallback if invalid ID
        if next_speaker_id not in AGENTS:
            next_speaker_id = random.choice(list(AGENTS.keys()))

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
    1. First, THINK silently about the previous argument. Identify fallacies or weak points.
    2. Then, SPEAK. Keep it under 3 sentences. Be profound, challenging, and in-character.
    
    Return JSON:
    {{
        "thought_process": "I observe that...",
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
            "timestamp": int(time.time() * 1000)
        }
    except Exception as e:
        print(f"Agent Error: {e}")
        return {
            "speakerId": next_speaker_id,
            "text": f"The complexity of this argument eludes me for a moment. (AI Error: {str(e)})",
            "type": "ARGUMENT",
            "thoughts": f"System failure: {str(e)}",
            "score": {},
            "timestamp": int(time.time() * 1000)
        }

def generate_autonomous_debate(topic, turns=6):
    """
    Generates a full multi-turn debate between agents automatically.
    Returns a formatted dialogue string and the raw history.
    """
    if not GEMINI_API_KEY:
        return "System Offline (No API Key).", []

    history = []

    # Initial Prompt to kickstart
    initial_prompt = f"Make a provocative opening statement about '{topic}' that invites debate."

    try:
        model = get_model()
        # Randomly pick a starter who isn't a skeptic (Skeptics usually respond)
        starters = ['idealist', 'iconoclast', 'strategist', 'sage']
        starter_id = random.choice(starters)
        starter_agent = AGENTS[starter_id]

        resp = model.generate_content(f"You are {starter_agent['name']}. {initial_prompt}")
        history.append({
            "speakerId": starter_id,
            "text": resp.text.strip(),
            "type": "ARGUMENT",
            "timestamp": int(time.time() * 1000)
        })

        # Loop for subsequent turns
        for _ in range(turns - 1):
            turn_data = generate_debate_turn(topic, history)
            history.append(turn_data)
            # Small delay to avoid rate limits if any, though Gemini is fast
            time.sleep(0.5)

        # Format Dialogue
        formatted_dialogue = f"# 🏛️ Socratic Debate: {topic}\n\n"
        for turn in history:
            speaker_id = turn.get('speakerId')
            agent = AGENTS.get(speaker_id, {'name': 'Unknown'})
            name = agent['name']
            text = turn.get('text')

            # Add an icon
            icon = "🗣️"
            if speaker_id == 'skeptic': icon = "🤔"
            elif speaker_id == 'idealist': icon = "✨"
            elif speaker_id == 'realist': icon = "📜"
            elif speaker_id == 'iconoclast': icon = "⚡"
            elif speaker_id == 'sage': icon = "🎍"
            elif speaker_id == 'strategist': icon = "♟️"

            formatted_dialogue += f"### {icon} {name}\n{text}\n\n"

            if turn.get('thoughts'):
                formatted_dialogue += f"> *Thinking: {turn.get('thoughts')}*\n\n"

        # Generate Verdict (Athena's Judgment)
        verdict = generate_debate_verdict(topic, history)

        # Append verdict to formatted dialogue
        formatted_dialogue += f"\n---\n\n## ⚖️ Athena's Judgment\n\n"
        formatted_dialogue += f"**Winner:** {verdict.get('winner', 'No clear winner')}\n\n"
        formatted_dialogue += f"**Synthesis:** {verdict.get('synthesis', '')}\n\n"
        formatted_dialogue += f"**Key Concepts:** {', '.join(verdict.get('key_concepts', []))}\n"

        return formatted_dialogue, history, verdict

    except Exception as e:
        print(f"Autonomous Debate Error: {e}")
        return f"Error generating debate: {str(e)}", [], {}

def generate_debate_verdict(topic, history):
    """
    Analyzes a full debate history and provides a structured verdict.
    """
    if not GEMINI_API_KEY:
        return {}

    model = get_model()

    transcript = ""
    for turn in history:
        speaker = turn.get('speakerId', 'unknown')
        name = AGENTS.get(speaker, {'name': 'Unknown'}).get('name')
        text = turn.get('text', '')
        transcript += f"{name}: {text}\n"

    judge_prompt = f"""
    You are Athena, the Goddess of Wisdom. You have observed a debate on "{topic}".

    TRANSCRIPT:
    {transcript}

    TASK:
    1. Identify the "Winner" (the agent who provided the most robust, logical, or impactful argument).
    2. Extract 3-5 Key Concepts (philosophical terms, fallacies, or ideas mentioned).
    3. Provide a "Synthesis" - a profound paragraph that reconciles the opposing views or highlights the complexity.
    4. Select the "Best Quote" from the transcript.

    Return JSON:
    {{
        "winner": "Name of Agent",
        "key_concepts": ["concept1", "concept2", ...],
        "synthesis": "...",
        "best_quote": "..."
    }}
    """

    try:
        response = model.generate_content(judge_prompt)
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
            "synthesis": "The debate was too complex for a verdict.",
            "best_quote": ""
        }
