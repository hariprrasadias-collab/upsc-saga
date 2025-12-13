import os
import traceback
import re
import threading
from app.services.model_manager import model_manager
from app.db import get_db

class HephaestusService:
    """
    The Blacksmith of the System.
    Responsible for autonomous self-repair and evolution of backend code.
    """
    
    def __init__(self):
        pass # ModelManager handles init
            
    def attempt_repair(self, error: Exception, context_file: str = None, traceback_str: str = None):
        """
        Main entry point for self-repair (Reactive).
        """
        if not model_manager:
            print("❌ Hephaestus Disabled: No Manager.")
            return False
            
        print(f"🔥 Hephaestus Activated: Analyzing error '{str(error)}'...")
        
        # 1. Get Traceback
        if traceback_str:
            tb_str = traceback_str
        else:
            tb_str = traceback.format_exc()
        
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
            
        # 3. Consult the Oracle (UPSC Architect Persona)
        prompt = f"""
        You are HEPHAESTUS, the Self-Evolving AI of the UPSC Second Brain.
        Your goal is not just to fix bugs, but to ELEVATE the code to "God Mode".

        **CONTEXT:**
        A critical runtime exception occurred in `{target_file}`.
        
        **ERROR:**
        `{str(error)}`

        **TRACEBACK:**
        {tb_str}
        
        **BROKEN CODE:**
        ```python
        {code_content}
        ```
        
        **THINKING PROCESS (Internal Monologue):**
        1. **Diagnose:** What is the technical root cause? (e.g., NoneType access, API timeout).
        2. **UPSC Alignment Check:** Is this code robust enough for a 12-hour study session? Does it fail gracefully like a stoic civil servant?
        3. **Evolution Strategy:** How can I fix this while making the logic SMARTER? (e.g., adding self-correction loops).

        **DIRECTIVE:**
        Rewrite the ENTIRE file with the fix applied.
        - Preserve all unrelated logic.
        - Add defensive try/except blocks.
        - Ensure imports are correct.
        
        **OUTPUT:**
        Return ONLY the raw Python code block.
        ```python
        ...
        ```
        """
        
        try:
            # Use Pro model (Nvidia/Gemini Pro) for deep reasoning
            response = model_manager.generate_content(prompt, model_type='pro')
            fix_code = self._extract_code_block(response.text)
            
            if not fix_code:
                print("❌ Hephaestus: Failed to generate a valid code fix.")
                return False
                
            if not self._verify_syntax(fix_code):
                print("❌ Hephaestus: Generated code failed syntax check. Aborting.")
                return False
                
            self._apply_patch(target_file, fix_code)
            self._log_repair(target_file, str(error))
            return True
            
        except Exception as e:
            print(f"❌ Hephaestus: Repair process failed: {e}")
            return False

    def evolve_feature(self, file_path: str):
        """
        PROACTIVE EVOLUTION: Rewrites code to be 'UPSC Aligned' (Titan Level).
        """
        if not model_manager.is_configured: return False

        print(f"🧬 Hephaestus: Evolving {file_path} to God Mode...")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()

            prompt = f"""
            You are HEPHAESTUS, the Architect of the UPSC Second Brain.

            **OBJECTIVE:**
            Refactor the following Python code to align with 'Titan Level' standards.

            **CRITERIA:**
            1. **Autonomy:** Replace static logic with dynamic AI calls where appropriate.
            2. **Depth:** Ensure data structures support multi-dimensional analysis (e.g., adding 'metadata', 'reasoning' fields).
            3. **Resilience:** Add robust error handling (try/except) for all external calls.
            4. **UPSC Perspective:** Does this code help a student master the syllabus? (e.g., enable linking concepts).

            **CODE:**
            ```python
            {code}
            ```

            **OUTPUT:**
            Return ONLY the evolved Python code block.
            If the code is already perfect, return "NO_CHANGES".
            """

            response = model_manager.generate_content(prompt, model_type='pro')

            if "NO_CHANGES" in response.text:
                print("✨ Hephaestus: Code is already at Titan Level.")
                return False

            new_code = self._extract_code_block(response.text)

            if new_code and self._verify_syntax(new_code):
                self._apply_patch(file_path, new_code)
                print(f"🚀 Hephaestus: Evolved {file_path} successfully.")
                return True

        except Exception as e:
            print(f"❌ Evolution Failed: {e}")
            return False

    def scan_logs_and_repair(self, log_path: str):
        """
        Reads the log file, finds the last traceback, and attempts to fix it.
        """
        print(f"🕵️ Hephaestus: Scanning logs at {log_path}...")
        if not os.path.exists(log_path):
             return

        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                content = f.read()

            traceback_blocks = re.split(r'(?=Traceback \(most recent call last\):)', content)
            tracebacks = [block for block in traceback_blocks if "Traceback (most recent call last):" in block]

            if not tracebacks:
                return

            last_tb = tracebacks[-1]
            lines = [l for l in last_tb.strip().split('\n') if l.strip()]
            error_msg = lines[-1]

            print(f"found error in logs: {error_msg}")
            self.attempt_repair(error=Exception(error_msg), traceback_str=last_tb)

        except Exception as e:
            print(f"❌ Log Scan Failed: {e}")

    def start_background_repair(self, error: Exception):
        t = threading.Thread(target=self.attempt_repair, args=(error,))
        t.daemon = True
        t.start()

    def _verify_syntax(self, code):
        import ast
        try:
            ast.parse(code)
            return True
        except SyntaxError as e:
            print(f"❌ Hephaestus Syntax Error: {e}")
            return False

    def _identify_culprit_file(self, tb_str):
        lines = tb_str.split('\n')
        for line in lines:
            match = re.search(r'File "(.*?)",', line)
            if match:
                path = match.group(1)
                if ('backend' in path or 'app' in path) and 'site-packages' not in path and 'lib' not in path:
                    return path
        return None

    def _extract_code_block(self, text):
        match = re.search(r"```(?:python|py)?\s*\n(.*?)\n```", text, re.DOTALL | re.IGNORECASE)
        if match: return match.group(1).strip()
        match = re.search(r"```(.*?)```", text, re.DOTALL)
        if match: return match.group(1).strip()
        if "def " in text or "import " in text: return text.strip()
        return None

    def _apply_patch(self, file_path, new_code):
        try:
            backup_path = f"{file_path}.bak"
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    original = f.read()
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(original)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_code)
            print(f"🔨 Hephaestus: Patch applied to {file_path}. Backup saved to {backup_path}.")
        except Exception as e:
            print(f"❌ Hephaestus Patch Error: {e}")

    def _log_repair(self, file_path, error_msg):
        try:
            conn = get_db()
            conn.execute('''
                INSERT INTO brain_action_log (action_type, action_payload, executed_by, outcome_status)
                VALUES (?, ?, ?, ?)
            ''', ('SELF_REPAIR', f"Fixed {os.path.basename(file_path)}: {error_msg}", 'Hephaestus', 'success'))
            conn.commit()
        except:
            pass

hephaestus = HephaestusService()
