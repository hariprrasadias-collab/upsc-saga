import json
import os
import google.generativeai as genai
from app import db

class MindMapService:
    @staticmethod
    def generate_mindmap(topic):
        """
        Generates a hierarchical JSON structure for a mind map using Gemini.
        """
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise Exception("GEMINI_API_KEY not found")

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest')

        prompt = f"""
        Create a detailed mind map for the topic: "{topic}".
        Return ONLY a valid JSON object representing the tree structure.
        The structure must be:
        {{
            "name": "{topic}",
            "children": [
                {{
                    "name": "Subtopic 1",
                    "children": [ ... ]
                }},
                ...
            ]
        }}
        Ensure the depth is at least 3 levels.
        Do not include any markdown formatting (like ```json), just the raw JSON string.
        """

        try:
            response = model.generate_content(prompt)
            text = response.text.strip()
            # Clean up potential markdown formatting if Gemini still adds it
            if text.startswith("```json"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
            
            return json.loads(text)
        except Exception as e:
            print(f"Error generating mind map: {e}")
            raise Exception(f"Failed to generate mind map: {str(e)}")

    @staticmethod
    def save_mindmap(title, root_node):
        conn = db.get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO mind_maps (title, root_node)
            VALUES (?, ?)
        ''', (title, json.dumps(root_node)))
        
        conn.commit()
        return cursor.lastrowid

    @staticmethod
    def get_all_mindmaps():
        conn = db.get_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, title, created_at FROM mind_maps ORDER BY created_at DESC')
        return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_mindmap(map_id):
        conn = db.get_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM mind_maps WHERE id = ?', (map_id,))
        row = cursor.fetchone()
        
        if row:
            data = dict(row)
            data['root_node'] = json.loads(data['root_node'])
            return data
        return None

    @staticmethod
    def delete_mindmap(map_id):
        conn = db.get_db()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM mind_maps WHERE id = ?', (map_id,))
        conn.commit()
        
        return cursor.rowcount > 0

