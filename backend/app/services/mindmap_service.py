import json
import os
import logging
from app import db
from app.services.model_manager import model_manager

class MindMapService:
    @staticmethod
    def generate_mindmap(topic):
        """
        Generates a hierarchical JSON structure for a mind map using Gemini.
        """
        # API Check handled by manager

        prompt = f"""
        # MISSION: UPSC STRUCTURAL BLUEPRINT (MIND MAP)
        **Topic:** "{topic}"

        **DIRECTIVE:**
        Structure this strictly for a UPSC Mains Answer (Introduction -> Body -> Conclusion).

        **HIERARCHY RULES:**
        1. **Root:** The Topic.
        2. **Level 1 (The Framework):**
           - **Definition/Context** (Article No, Origin)
           - **Dimensions** (Social, Economic, Political)
           - **Issues/Challenges**
           - **Solutions/Way Forward** (Committees, Best Practices)
        3. **Level 2 (The Meat):** Specific points.
        4. **Level 3 (The Edge):** Data, Case Laws, Examples.

        **OUTPUT SCHEMA (JSON ONLY):**
        {{
            "name": "{topic}",
            "children": [
                {{
                    "name": "🏛️ Constitutional Basis",
                    "children": [ {{ "name": "Article X" }} ]
                }},
                {{
                    "name": "📉 Challenges",
                    "children": [ {{ "name": "Structural Bottlenecks", "children": [ {{ "name": "Data Point: 45% vacancy" }} ] }} ]
                }}
            ]
        }}
        """

        try:
            # Use Pro model for better structural reasoning
            response = model_manager.generate_content(prompt, model_type='pro')
            text = response.text.strip()
            # Clean up potential markdown formatting if Gemini still adds it
            # Clean up potential markdown formatting if Gemini still adds it
            if text.startswith("```"):
                text = text.replace('```json', '').replace('```', '').strip()
                
            start = text.find('{')
            end = text.rfind('}')
            
            if start != -1 and end != -1:
                text = text[start:end+1]
            
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
    def deep_dive(topic, node_name):
        """
        Generates child nodes for a specific sub-topic in the mind map.
        """
        prompt = f"""
        # MISSION: SUB-NODE DEEP DIVE (MIND MAP EXPANSION)
        **Context Topic:** "{topic}"
        **Target Node to Expand:** "{node_name}"

        **DIRECTIVE:**
        The user has clicked "Deep Dive" on this node. Provide 3-5 high-yield specific child concepts, facts, or data points for this specific sub-topic.

        **OUTPUT SCHEMA (JSON ONLY):**
        [
            {{ "name": "Deep point 1" }},
            {{ "name": "Data: 45% growth", "children": [ {{ "name": "Source: World Bank" }} ] }}
        ]
        """
        try:
            response = model_manager.generate_content(prompt, model_type='fast')
            text = response.text.strip()
            if text.startswith("```"):
                text = text.replace('```json', '').replace('```', '').strip()
                
            start = text.find('[')
            end = text.rfind(']')
            
            if start != -1 and end != -1:
                text = text[start:end+1]
                
            if not text:
                raise Exception("Empty response from AI")
                
            return json.loads(text)
        except Exception as e:
            print(f"Error generating deep dive: {e}")
            return [{"name": f"Error: {str(e)}"}]

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
