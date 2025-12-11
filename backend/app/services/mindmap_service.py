import json
import os
from app.services.model_manager import model_manager
from app import db

class MindMapService:
    @staticmethod
    def generate_mindmap(topic):
        """
        Generates a hierarchical JSON structure for a mind map using Gemini.
        """
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
            response = model_manager.generate_content(prompt)
            if hasattr(response, 'text'):
                text = response.text.strip()
            else:
                text = str(response)

            # Clean up potential markdown formatting
            text = text.replace('```json', '').replace('```', '').strip()
            
            # Handle empty response
            if not text:
                raise Exception("Empty response from AI")

            try:
                return json.loads(text)
            except json.JSONDecodeError:
                # Fallback structure if JSON fails
                return {
                    "name": topic,
                    "children": [
                        {"name": "Concept 1 (Error Parsing)", "children": []},
                        {"name": "Concept 2 (Error Parsing)", "children": []}
                    ]
                }

        except Exception as e:
            print(f"Error generating mind map: {e}")
            # Return safe fallback instead of crashing
            return {
                "name": topic,
                "children": [
                    {"name": "Error Generating Map", "children": [{"name": str(e)}]}
                ]
            }

    @staticmethod
    def save_mindmap(title, root_node):
        try:
            conn = db.get_db()
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO mind_maps (title, root_node, created_at)
                VALUES (?, ?, datetime('now'))
            ''', (title, json.dumps(root_node)))

            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error saving mind map: {e}")
            return None

    @staticmethod
    def get_all_mindmaps():
        try:
            conn = db.get_db()
            cursor = conn.cursor()

            cursor.execute('SELECT id, title, created_at FROM mind_maps ORDER BY created_at DESC')
            return [dict(row) for row in cursor.fetchall()]
        except Exception:
            return []

    @staticmethod
    def get_mindmap(map_id):
        try:
            conn = db.get_db()
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM mind_maps WHERE id = ?', (map_id,))
            row = cursor.fetchone()

            if row:
                data = dict(row)
                data['root_node'] = json.loads(data['root_node'])
                return data
            return None
        except Exception:
            return None

    @staticmethod
    def delete_mindmap(map_id):
        try:
            conn = db.get_db()
            cursor = conn.cursor()

            cursor.execute('DELETE FROM mind_maps WHERE id = ?', (map_id,))
            conn.commit()

            return cursor.rowcount > 0
        except Exception:
            return False
