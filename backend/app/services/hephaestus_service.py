import os
import traceback
import re
import threading
from app.services.model_manager import model_manager
from app.db import get_db

class HephaestusService:
    """
    The Blacksmith of the System.
    Responsible for autonomous self-repair of backend code.
    """
    
    def __init__(self):
        pass # ModelManager handles init
            
    def attempt_repair(self, error: Exception, context_file: str = None, traceback_str: str = None):
        """
        Main entry point for self-repair.
        If traceback_str is provided, it uses that (for log scanning).
        Otherwise, it calls traceback.format_exc() (for live errors).
        """
        if not model_manager: # Should never happen
            print("❌ Hephaestus Disabled: No Manager.")
            return False
            
        print(f"🔥 Hephaestus Activated: Analyzing error '{str(error)}'...")
        
        # 1. Get Traceback
        if traceback_str:
            tb_str = traceback_str
        else:
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
            
        # 3. Consult the Oracle (Gemini/Nvidia)
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
           - Fix the specific error mentioned.
        
        **OUTPUT:**
        Return ONLY the raw Python code block. No conversation.
        ```python
        ...
        ```
        """
        
        try:
            # Use Pro model for code repair - Critical reasoning required
            # The 'pro' tier (Nvidia/Gemini 1.5 Pro) is best for coding tasks.
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

    def scan_logs_and_repair(self, log_path: str):
        """
        Reads the log file, finds the last traceback, and attempts to fix it.
        """
        print(f"🕵️ Hephaestus: Scanning logs at {log_path}...")
        if not os.path.exists(log_path):
             print(f"ℹ️ Log file {log_path} not found. Skipping scan.")
             return

        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Regex to capture Python tracebacks
            # Starts with "Traceback (most recent call last):" and consumes until the next timestamp or EOF
            # Assuming timestamps look like [202... or similar, or just relying on indentation
            # A safer bet is just extracting the block starting with Traceback
            traceback_blocks = re.split(r'(?=Traceback \(most recent call last\):)', content)

            # Filter for actual tracebacks
            tracebacks = [block for block in traceback_blocks if "Traceback (most recent call last):" in block]

            if not tracebacks:
                print("✅ No tracebacks found in logs.")
                return

            # Analyze the last one
            last_tb = tracebacks[-1]

            # Extract error message (last non-empty line usually)
            lines = [l for l in last_tb.strip().split('\n') if l.strip()]
            error_msg = lines[-1]

            print(f"found error in logs: {error_msg}")

            # Attempt repair
            # We pass the error message as the Exception string, and the full text as traceback
            self.attempt_repair(error=Exception(error_msg), traceback_str=last_tb)

        except Exception as e:
            print(f"❌ Log Scan Failed: {e}")

    def start_background_repair(self, error: Exception):
        """
        Non-blocking wrapper for attempt_repair.
        """
        t = threading.Thread(target=self.attempt_repair, args=(error,))
        t.daemon = True
        t.start()

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
