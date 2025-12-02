import os
import traceback
import google.generativeai as genai
import re
from app.db import get_db

class HephaestusService:
    """
    The Blacksmith of the System.
    Responsible for autonomous self-repair of backend code.
    """
    
    def __init__(self):
        self.api_key = os.environ.get('GEMINI_API_KEY')
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp') # Use a smart model for code
        else:
            self.model = None
            
    def attempt_repair(self, error: Exception, context_file: str = None):
        """
        Main entry point for self-repair.
        1. Analyzes the error.
        2. Locates the culprit file.
        3. Generates a patch.
        4. Applies the patch.
        """
        if not self.model:
            print("❌ Hephaestus Disabled: No API Key.")
            return False
            
        print(f"🔥 Hephaestus Activated: Analyzing error '{str(error)}'...")
        
        # 1. Get Traceback and File
        tb_str = traceback.format_exc()
        
        # Extract the last file in the traceback that belongs to our app (not libraries)
        target_file = self._identify_culprit_file(tb_str)
        
        if not target_file:
            print("❌ Hephaestus: Could not identify a modifiable file in traceback.")
            return False
            
        print(f"🎯 Hephaestus: Culprit identified -> {target_file}")
        
        # 2. Read the broken code
        try:
            with open(target_file, 'r', encoding='utf-8') as f:
                code_content = f.read()
        except Exception as e:
            print(f"❌ Hephaestus: Failed to read file: {e}")
            return False
            
        # 3. Consult the Oracle (Gemini)
        prompt = f"""
        CRITICAL SYSTEM FAILURE DETECTED.
        You are Hephaestus, the AI Repair Engineer.
        
        ERROR: {str(error)}
        
        TRACEBACK:
        {tb_str}
        
        BROKEN FILE ({target_file}):
        ```python
        {code_content}
        ```
        
        TASK:
        1. Analyze the error and the code.
        2. Provide the CORRECTED full file content.
        3. Do NOT provide explanations, only the python code block.
        4. Ensure the fix is safe and maintains existing functionality.
        
        RESPONSE FORMAT:
        ```python
        ... full corrected code ...
        ```
        """
        
        try:
            response = self.model.generate_content(prompt)
            fix_code = self._extract_code_block(response.text)
            
            if not fix_code:
                print("❌ Hephaestus: Failed to generate a valid code fix.")
                return False
                
            # 3.5 Verify Syntax (Safety Check)
            if not self._verify_syntax(fix_code):
                print("❌ Hephaestus: Generated code failed syntax check. Aborting.")
                return False
                
            # 4. Apply the Fix
            self._apply_patch(target_file, fix_code)
            
            # 5. Log the Repair & Learn
            self._log_repair(target_file, str(error))
            
            # --- HIPPOCAMPUS INTEGRATION ---
            try:
                from app.services.hippocampus_service import hippocampus
                lesson = f"Fixed {str(error)} in {os.path.basename(target_file)}. Ensure syntax is correct."
                hippocampus.remember_lesson(context=str(error), lesson=lesson)
            except:
                pass
            # -------------------------------
            
            return True
            
        except Exception as e:
            print(f"❌ Hephaestus: Repair process failed: {e}")
            return False

    def audit_file(self, file_path: str):
        """
        PROACTIVE REPAIR: Scans a file for latent bugs or optimizations.
        """
        if not self.model: return False
        
        print(f"🕵️ Hephaestus: Auditing {file_path}...")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
                
            prompt = f"""
            You are Hephaestus, the Code Auditor.
            Review the following Python code for:
            1. Potential Bugs (latent crashes)
            2. Security Risks
            3. Performance Optimizations
            
            CODE:
            ```python
            {code}
            ```
            
            If you find CRITICAL issues, rewrite the code to fix them.
            If the code is fine, return "NO_CHANGES".
            
            RESPONSE FORMAT:
            ```python
            ... full optimized code ...
            ```
            OR
            NO_CHANGES
            """
            
            response = self.model.generate_content(prompt)
            
            if "NO_CHANGES" in response.text:
                print("✅ Hephaestus: File is healthy.")
                return False
                
            new_code = self._extract_code_block(response.text)
            
            if new_code and self._verify_syntax(new_code):
                self._apply_patch(file_path, new_code)
                print(f"✨ Hephaestus: Optimized {file_path}.")
                return True
                
        except Exception as e:
            print(f"❌ Audit Failed: {e}")
            return False

    def _verify_syntax(self, code):
        """
        Checks if the code is valid Python.
        """
        import ast
        try:
            ast.parse(code)
            return True
        except SyntaxError as e:
            print(f"❌ Hephaestus Syntax Error: {e}")
            return False

    def _identify_culprit_file(self, tb_str):
        """
        Parses traceback to find the most relevant project file.
        """
        lines = tb_str.split('\n')
        # Look for files in our project directory, excluding venv/libraries
        # Assuming project structure d:/upsc-second-brain/backend/app/...
        
        candidate = None
        for line in lines:
            if 'File "' in line and 'backend\\app' in line:
                # Extract path: File "d:\path\to\file.py", line 10
                match = re.search(r'File "(.*?)",', line)
                if match:
                    candidate = match.group(1)
                    
        return candidate

    def _extract_code_block(self, text):
        """
        Extracts python code from markdown response.
        """
        match = re.search(r'```python\n(.*?)```', text, re.DOTALL)
        if match:
            return match.group(1)
        
        # Fallback: maybe just ```
        match = re.search(r'```\n(.*?)```', text, re.DOTALL)
        if match:
            return match.group(1)
            
        return None

    def _apply_patch(self, file_path, new_code):
        """
        Writes the new code to the file.
        """
        # Create backup first? For now, YOLO (per user request for autonomy)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_code)
        print(f"🔨 Hephaestus: Patch applied to {file_path}. Restarting system...")

    def _log_repair(self, file_path, error_msg):
        """
        Logs the repair event to DB.
        """
        try:
            conn = get_db()
            conn.execute('''
                INSERT INTO brain_action_log (action_type, action_payload, executed_by, outcome_status)
                VALUES (?, ?, ?, ?)
            ''', ('SELF_REPAIR', f"Fixed {os.path.basename(file_path)}: {error_msg}", 'Hephaestus', 'success'))
            conn.commit()
        except:
            pass # Don't crash the crash handler

hephaestus = HephaestusService()
