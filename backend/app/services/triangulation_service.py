import google.generativeai as genai
import os
import json
from app.db import get_db
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def get_model():
    try:
        return genai.GenerativeModel('gemini-flash-latest')
    except:
        return genai.GenerativeModel('gemini-pro')

def analyze_topic_triangulation(text):
    """
    Triangulates a topic into Theory, Precedents, and PYQs.
    """
    if not GEMINI_API_KEY:
        return {"error": "Gemini API Key missing"}

    model = get_model()
    conn = get_db()

    # 1. AI Analysis (Omni-Link System)
    prompt = f"""
    Analyze the following text for UPSC Civil Services preparation.
    TEXT: "{text[:1500]}..."

    PERFORM A "SOURCE TRIANGULATION 4.0" ANALYSIS.
    
    Output MUST be valid JSON with the following structure:
    {{
        "core_topic": "Title of the Topic",
        "synthesis": "A high-quality, 150-word 'Body' paragraph for a Mains answer, synthesizing the current event with static theory.",
        "scholars": [
            {{ "name": "Scholar Name", "quote": "Relevant quote...", "context": "Context of the quote" }}
        ],
        "data_bank": [
            {{ "statistic": "e.g., 45% of...", "source": "World Bank/NITI Aayog", "relevance": "High" }}
        ],
        "critical_axis": {{
            "arguments_for": ["Argument 1", "Argument 2", "Argument 3"],
            "arguments_against": ["Counter-argument 1", "Counter-argument 2", "Counter-argument 3"]
        }},
        "pestle": {{
            "political": "...",
            "economic": "...",
            "sociological": "...",
            "technological": "...",
            "legal": "...",
            "environmental": "..."
        }},
        "gs_linkages": {{
            "gs1": "Link to Society/Geography/History",
            "gs2": "Link to Polity/IR/Governance",
            "gs3": "Link to Economy/Environment/Science",
            "gs4": "Link to Ethics/Integrity"
        }},
        "way_forward": {{
            "immediate": "Administrative action...",
            "medium_term": "Policy change...",
            "long_term": "Structural reform..."
        }},
        "predicted_question": "A potential UPSC Mains question based on this topic.",
        "mind_map_code": "Mermaid JS code for a simple mind map of this topic (graph TD...)",
        "keywords": ["keyword1", "keyword2", "keyword3"],
        "theory": [
            {{ "source": "Standard Book", "chapter": "Chapter Name", "relevance": "High" }}
        ],
        "precedents": [
            {{ "name": "Case/Article", "type": "Judgment/Article", "summary": "One line summary" }}
        ]
    }}
    """

    try:
        response = model.generate_content(prompt)
        ai_data = json.loads(response.text.replace('```json', '').replace('```', '').strip())
    except Exception as e:
        print(f"Triangulation AI Error: {e}")
        return {"error": str(e)}

    # 2. Fetch PYQs from Database
    keywords = ai_data.get('keywords', [])
    pyqs = []
    
    if keywords:
        # Construct dynamic query
        placeholders = ' OR '.join(['question_text LIKE ?'] * len(keywords))
        query = f"SELECT * FROM pyq_questions WHERE {placeholders} LIMIT 5"
        params = [f"%{k}%" for k in keywords]
        
        try:
            rows = conn.execute(query, params).fetchall()
            pyqs = [dict(row) for row in rows]
        except Exception as e:
            print(f"PYQ Fetch Error: {e}")

    return {
        "topic": ai_data.get('core_topic'),
        "synthesis": ai_data.get('synthesis'),
        "scholars": ai_data.get('scholars', []),
        "data_bank": ai_data.get('data_bank', []),
        "critical_axis": ai_data.get('critical_axis', {}),
        "pestle": ai_data.get('pestle', {}),
        "gs_linkages": ai_data.get('gs_linkages', {}),
        "way_forward": ai_data.get('way_forward', {}),
        "predicted_question": ai_data.get('predicted_question'),
        "mind_map_code": ai_data.get('mind_map_code'),
        "theory": ai_data.get('theory', []),
        "precedents": ai_data.get('precedents', []),
        "pyqs": pyqs
    }
