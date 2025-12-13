import os
import traceback
import re
import threading
from datetime import datetime
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
            print("❌ Hephaestus Disabled: No Manager.", flush=True)
            return False
            
        print(f"🔥 Hephaestus Activated: Analyzing error '{str(error)}'...", flush=True)
        
        # 1. Get Traceback
        if traceback_str:
            tb_str = traceback_str
        else:
            tb_str = traceback.format_exc()
        
        target_file = self._identify_culprit_file(tb_str)
        
        if not target_file:
            print("❌ Hephaestus: Could not identify a modifiable file in traceback.", flush=True)
            return False
            
        print(f"🎯 Hephaestus: Culprit identified -> {target_file}", flush=True)
        
        # 2. Read the broken code
        try:
            with open(target_file, 'r', encoding='utf-8') as f:
                code_content = f.read()
        except Exception as e:
            print(f"❌ Hephaestus: Failed to read file: {e}", flush=True)
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
                print("❌ Hephaestus: Failed to generate a valid code fix.", flush=True)
                return False
                
            if not self._verify_syntax(fix_code):
                print("❌ Hephaestus: Generated code failed syntax check. Aborting.", flush=True)
                return False
                
            self._apply_patch(target_file, fix_code)
            self._log_repair(target_file, str(error))
            return True
            
        except Exception as e:
            print(f"❌ Hephaestus: Repair process failed: {e}", flush=True)
            return False

    def evolve_feature(self, file_path: str):
        """
        PROACTIVE EVOLUTION: Rewrites code to be 'UPSC Aligned' (Titan Level).
        """
        if not model_manager.is_configured: return False

        print(f"🧬 Hephaestus: Evolving {file_path} to God Mode...", flush=True)

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
                print("✨ Hephaestus: Code is already at Titan Level.", flush=True)
                return False

            new_code = self._extract_code_block(response.text)

            if new_code and self._verify_syntax(new_code):
                self._apply_patch(file_path, new_code)
                print(f"🚀 Hephaestus: Evolved {file_path} successfully.", flush=True)
                return True

        except Exception as e:
            print(f"❌ Evolution Failed: {e}", flush=True)
            return False

    def scan_logs_and_repair(self, log_path: str):
        """
        Reads the log file, finds recent tracebacks, and attempts to fix them.
        """
        print(f"🕵️ Hephaestus: Scanning logs at {log_path}...", flush=True)
        if not os.path.exists(log_path):
             return

        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Improved regex to capture tracebacks more reliably
            # Looks for "Traceback (most recent call last):"
            traceback_blocks = re.split(r'(?=Traceback \(most recent call last\):)', content)

            # Filter valid blocks
            tracebacks = [block for block in traceback_blocks if "Traceback (most recent call last):" in block]

            if not tracebacks:
                print("✅ No tracebacks found in logs.", flush=True)
                return

            print(f"🕵️ Found {len(tracebacks)} tracebacks. Analyzing recent ones...", flush=True)

            # Process the last 3 distinct errors to be aggressive but safe
            processed_errors = set()

            for tb in reversed(tracebacks[-3:]):
                lines = [l for l in tb.strip().split('\n') if l.strip()]
                error_msg = lines[-1]

                # Avoid repeat processing in same scan
                if error_msg in processed_errors: continue
                processed_errors.add(error_msg)

                print(f"🔧 Attempting repair for: {error_msg}", flush=True)
                self.attempt_repair(error=Exception(error_msg), traceback_str=tb)

        except Exception as e:
            print(f"❌ Log Scan Failed: {e}", flush=True)

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
            print(f"❌ Hephaestus Syntax Error: {e}", flush=True)
            return False

    def _identify_culprit_file(self, tb_str):
        """
        Robust file identification with fuzzy fallback.
        """
        lines = tb_str.split('\n')
        for line in lines:
            match = re.search(r'File "(.*?)",', line)
            if match:
                path = match.group(1)

                # Filter for project files
                if ('backend' in path or 'app' in path) and 'site-packages' not in path and 'lib' not in path:
                    # 1. Exact match
                    if os.path.exists(path):
                        return path

                    # 2. Relative to CWD
                    rel_path = os.path.join(os.getcwd(), path.lstrip('/'))
                    if os.path.exists(rel_path):
                        return rel_path

                    # 3. Fuzzy Search (Basename match in project)
                    filename = os.path.basename(path)
                    print(f"🔍 Exact path not found. Searching for '{filename}'...", flush=True)
                    for root, dirs, files in os.walk(os.getcwd()):
                        if filename in files:
                            found_path = os.path.join(root, filename)
                            print(f"🔍 Found candidate: {found_path}", flush=True)
                            return found_path

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
            print(f"🔨 Hephaestus: Patch applied to {file_path}. Backup saved to {backup_path}.", flush=True)
        except Exception as e:
            print(f"❌ Hephaestus Patch Error: {e}", flush=True)

    def _log_repair(self, file_path, error_msg):
        # 1. DB Log
        try:
            conn = get_db()
            conn.execute('''
                INSERT INTO brain_action_log (action_type, action_payload, executed_by, outcome_status)
                VALUES (?, ?, ?, ?)
            ''', ('SELF_REPAIR', f"Fixed {os.path.basename(file_path)}: {error_msg}", 'Hephaestus', 'success'))
            conn.commit()
        except:
            pass

        # 2. Visible File Log
        try:
            with open("REPAIR_HISTORY.md", "a") as f:
                f.write(f"## Repair Event: {datetime.now()}\n")
                f.write(f"- **File:** `{file_path}`\n")
                f.write(f"- **Error:** `{error_msg}`\n")
                f.write(f"- **Status:** ✅ Patch Applied\n\n")
        except:
            pass

    def self_diagnose(self):
        """
        Runs internal integrity checks.
        """
        print("🏥 Hephaestus: Running System Diagnostics...", flush=True)
        issues = []

        # 1. Check Model Configuration
        if not model_manager.is_configured:
            issues.append("ModelManager not configured.")

        # 2. Check Database Connection
        try:
            get_db()
        except:
            issues.append("Database connection failed.")

        # 3. Check Logs Directory
        if not os.path.exists('logs'):
            issues.append("Logs directory missing.")

        if issues:
            print(f"⚠️ Diagnostics Found Issues: {issues}", flush=True)
            # Try to fix?
            if "Logs directory missing." in issues:
                os.makedirs('logs', exist_ok=True)
                print("🔧 Fixed: Logs directory created.", flush=True)
        else:
            print("✅ Diagnostics Passed: System Nominal.", flush=True)

hephaestus = HephaestusService()
