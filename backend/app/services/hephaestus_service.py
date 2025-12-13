import os
import traceback
import re
from app.services.model_manager import model_manager
from app.db import get_db
from app.services.model_manager import model_manager

class HephaestusService:
    """
    The Blacksmith of the System.
    Responsible for autonomous self-repair of backend code.
    """
    
    def __init__(self):
        pass # ModelManager handles init
            
    def attempt_repair(self, error: Exception, context_file: str = None):
        """
        Main entry point for self-repair.
        """
        if not model_manager: # Should never happen
            print("❌ Hephaestus Disabled: No Manager.")
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
        # MISSION: AUTONOMOUS CODE REPAIR (HEPHAESTUS)
        **Role:** Lead Software Architect (Python/Flask Expert).
        
        **CONTEXT:**
        A critical runtime exception occurred in `{target_file}`.
        
        **ERROR SIGNATURE:**
        `{str(error)}`

        **TRACEBACK:**
        {tb_str}
        
        **BROKEN CODE:**
        ```python
        {code_content}
        ```
        
        **DIRECTIVE:**
        1. **Diagnose:** Identify the root cause (Syntax, Logic, Import, Type Error).
        2. **Fix:** Rewrite the ENTIRE file with the fix applied.
        3. **Constraint:**
           - Preserve all unrelated logic.
           - Add defensive try/except blocks where risky.
           - Do NOT remove imports unless they are the cause.
        
        **OUTPUT:**
        Return ONLY the raw Python code block. No conversation.
        ```python
        ...
        ```
        """
        
        try:
            # Use Pro model for code repair - Critical reasoning required
            response = model_manager.generate_content(prompt, model_type='pro')
            fix_code = self._extract_code_block(response.text)
            
            if not fix_code:
                print("❌ Hephaestus: Failed to generate a valid code fix.")
                return False
                
            # 3.5 Verify Syntax (Safety Check)
            if not self._verify_syntax(fix_code):
                print("❌ Hephaestus: Generated code failed syntax check. Aborting.")
                return False
                
            # 4. Apply the Fix (with backup)
            self._apply_patch(target_file, fix_code)
            
            # 5. Log the Repair & Learn
            self._log_repair(target_file, str(error))
            
            return True
            
        except Exception as e:
            print(f"❌ Hephaestus: Repair process failed: {e}")
            return False

    def audit_file(self, file_path: str):
        """
        PROACTIVE REPAIR: Scans a file for latent bugs or optimizations.
        """
        if not model_manager.is_configured: return False
        
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
            
            # Use Pro model for audit
            response = model_manager.generate_content(prompt, model_type='pro')
            
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
        Compatible with Windows and Linux paths.
        """
        lines = tb_str.split('\n')
        
        candidate = None
        for line in lines:
            # Match "File" line with generic path separators
            # Regex captures: File "path", line N, in func
            match = re.search(r'File "(.*?)",', line)
            if match:
                path = match.group(1)
                # Check if it's our project file (heuristic: contains 'backend' or 'app')
                # Adjust 'backend' check based on deployment structure
                if ('backend' in path or 'app' in path) and 'site-packages' not in path and 'lib' not in path:
                    candidate = path
                    
        return candidate

    def _extract_code_block(self, text):
        """
        Extracts python code from markdown response.
        """
        # Try generic code block matcher
        # Matches ```(python/py|nothing)\n(CODE)\n``` in a robust way
        match = re.search(r"```(?:python|py)?\s*\n(.*?)\n```", text, re.DOTALL | re.IGNORECASE)
        if match:
             return match.group(1).strip()
             
        # Fallback: Just look for any fences
        match = re.search(r"```(.*?)```", text, re.DOTALL)
        if match:
             return match.group(1).strip()
        
        # Super Fallback: If the entire response looks like code (no fences, just def/import)
        if "def " in text or "import " in text:
             return text.strip()

        return None

    def _apply_patch(self, file_path, new_code):
        """
        Writes the new code to the file.
        Creates a .bak backup first.
        """
        try:
            # Backup
            backup_path = f"{file_path}.bak"
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    original = f.read()
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(original)

            # Write new
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_code)
            print(f"🔨 Hephaestus: Patch applied to {file_path}. Backup saved to {backup_path}. Restarting system...")
        except Exception as e:
            print(f"❌ Hephaestus Patch Error: {e}")

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
