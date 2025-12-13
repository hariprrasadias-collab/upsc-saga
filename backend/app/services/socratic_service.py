import os
import json
import random
import time
from dotenv import load_dotenv
from app.services.model_manager import model_manager

load_dotenv()

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
    # Manager handles auth

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
    # MISSION: MODERATE A CLASH OF PHILOSOPHERS
    **Topic:** "{topic}"
    
    **AGENTS:**
    {agent_descriptions}

    **TRANSCRIPT:**
    {context_str}

    **DIRECTIVE:**
    1. **Conflict Engine:** Who vehemently disagrees with the last point? Pick them.
    2. **Avoid Echo Chambers:** Never pick the same person twice.
    3. **Strategy Injection:** Don't just say "Respond". Give a specific tactical order (e.g., "Attack the underlying definition of Justice", "Use a reductio ad absurdum").

    **OUTPUT SCHEMA (JSON):**
    {{
        "next_speaker_id": "skeptic" | "idealist" | "realist" | "iconoclast" | "sage" | "strategist",
        "strategy": "Your secret tactical instruction to the agent."
    }}
    """
    
    try:
        mod_response = model_manager.generate_content(moderator_prompt, model_type='pro')
        # Robust Extraction
        text = mod_response.text.strip()
        if text.startswith("```"):
             text = text.replace('```json', '').replace('```', '').strip()

        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            text = text[start:end+1]
            mod_data = json.loads(text)
            next_speaker_id = mod_data.get('next_speaker_id', 'skeptic')
            strategy = mod_data.get('strategy', 'Question the premise.')
        else:
             raise Exception("No JSON found")

        if next_speaker_id not in AGENTS:
            next_speaker_id = random.choice(list(AGENTS.keys()))

    except Exception as e:
        print(f"Moderator Error: {e}")
        next_speaker_id = random.choice(list(AGENTS.keys()))
        strategy = "Respond relevantly."

    # 3. The Agent (Generation with Chain of Thought)
    agent = AGENTS[next_speaker_id]
    
    agent_prompt = f"""
    # MISSION: EXECUTE PHILOSOPHICAL COMBAT
    **Role:** {agent['name']} ({agent['role']})
    **Style:** {agent['style']}
    **Orders:** {strategy}
    
    **CONTEXT:**
    {context_str}
    
    **EXECUTION:**
    1. **Deconstruct:** Identify the hidden premise or fallacy in the last turn.
    2. **Attack:** Use your specific rhetorical style.
       - Socrates: Ask a trap question.
       - Nietzsche: Mock the morality.
       - Machiavelli: Focus on utility.
    3. **Output:** Short, punchy, profound. Max 50 words. No "I think". Just the argument.
    
    **OUTPUT SCHEMA (JSON):**
    {{
        "thought_process": "Internal monologue analyzing the opponent's weakness.",
        "rhetorical_technique": "The specific device used (e.g., 'Socratic Irony').",
        "detected_fallacies_in_prev_turn": ["Fallacy Name"],
        "text": "Your actual spoken line.",
        "type": "ARGUMENT" | "QUESTION" | "REBUTTAL"
    }}
    """

    try:
        response = model_manager.generate_content(agent_prompt, model_type='pro')
        text = response.text.strip()

        # Check for fallback text
        if "Oracle is silent" in text:
             return {
                "speakerId": next_speaker_id,
                "text": "(The philosopher is silent due to high mental load. Please try again later.)",
                "type": "error",
                "technique": "Silence",
                "fallacies": []
            }

        try:
            # Robust Extraction
            if text.startswith("```"):
                text = text.replace("```json", "").replace("```", "").strip()

            start_idx = text.find('{')
            end_idx = text.rfind('}')
            
            if start_idx != -1 and end_idx != -1:
                json_str = text[start_idx:end_idx+1]
                result = json.loads(json_str)
            else:
                 # Fallback Structure
                 result = {"text": text, "type": "ARGUMENT", "thought_process": "Raw Output", "rhetorical_technique": "Direct Assertion"}
        except json.JSONDecodeError:
             result = {"text": text, "type": "ARGUMENT", "thought_process": "Decode Error", "rhetorical_technique": "Direct Assertion"}
        
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
    # Manager handles auth

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
    # Manager handles auth

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
    # API key managed by model_manager

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

    Return strictly valid JSON. 
    IMPORTANT: Escape all double quotes within strings (e.g. "John's" -> "John\\'s").
    Do not use Markdown code blocks.
    Structure:
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
        text = response.text.strip()
        
        # 1. Strip Markdown Code Blocks (More specifically)
        if "```" in text:
            # Try to split by code blocks
            parts = text.split("```")
            for part in parts:
                if "{" in part and "}" in part:
                    # Clean potential 'json' label
                    if part.startswith("json"):
                        text = part[4:].strip()
                    else:
                        text = part.strip()
                    break

        # 2. Extract JSON object (Find outer braces)
        start = text.find('{')
        end = text.rfind('}')
        
        if start != -1 and end != -1:
            json_str = text[start : end + 1]
            try:
                # Try standard parse
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"JSON Decode Error: {e} | Content: {json_str[:50]}...")
                
                # ATTEMPT REPAIR
                try:
                    # 1. Fix unescaped quotes in strings? (Risky but common for "John's")
                    # Naive: Replace "s with 's where it might be a contraction
                    pass
                except: pass

                # Fallback: Recover partial data manually if JSON fails
                # If "winner" exists, try to grab it via regex
                import re
                winner_match = re.search(r'"winner"\s*:\s*"([^"]+)"', json_str)
                synthesis_match = re.search(r'"synthesis"\s*:\s*"((?:[^"\\]|\\.)*)"', json_str)
                
                winner = winner_match.group(1) if winner_match else "Undecided (Parsing Error)"
                synthesis = synthesis_match.group(1) if synthesis_match else response.text

                # Construct a valid object from partial success
                return {
                    "winner": winner,
                    "key_concepts": ["Debate Analysis"], # Hard to regex list safely
                    "synthesis": synthesis,
                    "best_quote": "N/A",
                    "mental_models": []
                }
        
        # Fallback if parsing completely fails
        print(f"Verdict Parsing Failed. Raw Text: {text[:100]}...")
        return {
            "winner": "Undecided (Parsing Error)",
            "key_concepts": ["Debate Analysis"],
            "synthesis": response.text, 
            "best_quote": "N/A",
            "mental_models": []
        }

    except Exception as e:
        print(f"Verdict Generation Error: {e}")
        return {
            "winner": "Undecided",
            "key_concepts": [],
            "synthesis": "Analysis failed.",
            "best_quote": ""
        }
