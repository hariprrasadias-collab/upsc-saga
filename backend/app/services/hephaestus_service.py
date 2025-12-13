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
    V3: Neural Link (Context-Aware) & Double-Shot Verification.
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
        
        # 2. Read broken code & dependencies
        try:
            with open(target_file, 'r', encoding='utf-8') as f:
                code_content = f.read()

            dep_context = self._get_dependency_context(target_file)

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
        
        **DEPENDENCIES (Context):**
        {dep_context}

        **BROKEN CODE:**
        ```python
        {code_content}
        ```
        
        **DIRECTIVE:**
        Rewrite the ENTIRE file with the fix applied.
        - Preserve all unrelated logic.
        - Add defensive try/except blocks.
        - Ensure imports are correct (Check dependencies).

        **OUTPUT:**
        Return ONLY the raw Python code block.
        ```python
        ...
        ```
        """
        
        try:
            # First Shot: Generate Fix
            response = model_manager.generate_content(prompt, model_type='pro')
            fix_code = self._extract_code_block(response.text)
            
            if not fix_code:
                print("❌ Hephaestus: Failed to generate a valid code fix.", flush=True)
                return False

            # Second Shot: Self-Reflection (Double Check)
            fix_code = self._verify_and_refine(fix_code, error_msg=str(error))
                
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

            dep_context = self._get_dependency_context(file_path)

            prompt = f"""
            You are HEPHAESTUS, the Architect of the UPSC Second Brain.

            **OBJECTIVE:**
            Refactor the following Python code to align with 'Titan Level' standards.

            **CRITERIA:**
            1. **Autonomy:** Replace static logic with dynamic AI calls where appropriate.
            2. **Depth:** Ensure data structures support multi-dimensional analysis (e.g., adding 'metadata', 'reasoning' fields).
            3. **Resilience:** Add robust error handling (try/except) for all external calls.
            4. **Context Awareness:** Respect the dependencies provided below.

            **DEPENDENCIES:**
            {dep_context}

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

            # Self-Reflection
            new_code = self._verify_and_refine(new_code, mode="evolution")

            if new_code and self._verify_syntax(new_code):
                self._apply_patch(file_path, new_code)
                print(f"🚀 Hephaestus: Evolved {file_path} successfully.", flush=True)
                return True

        except Exception as e:
            print(f"❌ Evolution Failed: {e}", flush=True)
            return False

    def _get_dependency_context(self, file_path: str):
        """
        Reads the content of local modules imported by the target file.
        """
        context = ""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Simple regex to find "from app.services.xyz import abc" or "import app.services.xyz"
            imports = re.findall(r'(?:from|import) (app\.[a-zA-Z0-9_.]*)', content)

            seen_files = set()
            for imp in imports:
                parts = imp.split('.')
                if parts[0] == 'app':
                    parts = parts[1:]

                # Try finding it
                base_dir = os.path.join(os.getcwd(), 'backend', 'app')
                if not os.path.exists(base_dir):
                     base_dir = os.path.join(os.getcwd(), 'app')

                module_path = os.path.join(base_dir, *parts) + ".py"

                if os.path.exists(module_path) and module_path not in seen_files:
                    seen_files.add(module_path)
                    try:
                        with open(module_path, 'r', encoding='utf-8') as mf:
                            context += f"\n\n# DEPENDENCY: {parts[-1]}.py\n{mf.read()[:500]}... (truncated)\n"
                    except:
                        pass
        except Exception as e:
            print(f"⚠️ Dependency Context Failed: {e}", flush=True)
        return context

    def _verify_and_refine(self, code: str, error_msg: str = None, mode="repair"):
        """
        Self-Reflection Loop: Checks the generated code for obvious bugs.
        """
        if not code: return None

        prompt = f"""
        **CRITICAL CODE REVIEW**
        You are the Quality Assurance AI. Review the following Python code for Critical Bugs.

        **CODE:**
        ```python
        {code}
        ```

        {f"**ORIGINAL ERROR TO FIX:** {error_msg}" if error_msg else ""}

        **TASK:**
        1. Does this code fix the error? (If repair mode)
        2. Are there any SyntaxErrors or ImportErrors?
        3. Are there missing variables?

        **OUTPUT:**
        If PERFECT: Return "APPROVED".
        If FLAWED: Return the CORRECTED code block only.
        """

        try:
            response = model_manager.generate_content(prompt, model_type='fast') # Use fast model for check
            text = response.text.strip()

            if "APPROVED" in text:
                return code

            corrected_code = self._extract_code_block(text)
            return corrected_code if corrected_code else code

        except:
            return code # Fallback to original generation

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

            traceback_blocks = re.split(r'(?=Traceback \(most recent call last\):)', content)
            tracebacks = [block for block in traceback_blocks if "Traceback (most recent call last):" in block]

            if not tracebacks:
                print("✅ No tracebacks found in logs.", flush=True)
                return

            print(f"🕵️ Found {len(tracebacks)} tracebacks. Analyzing recent ones...", flush=True)

            processed_errors = set()
            for tb in reversed(tracebacks[-3:]):
                lines = [l for l in tb.strip().split('\n') if l.strip()]
                error_msg = lines[-1]
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
        lines = tb_str.split('\n')
        for line in lines:
            match = re.search(r'File "(.*?)",', line)
            if match:
                path = match.group(1)
                if ('backend' in path or 'app' in path) and 'site-packages' not in path and 'lib' not in path:
                    if os.path.exists(path): return path
                    rel_path = os.path.join(os.getcwd(), path.lstrip('/'))
                    if os.path.exists(rel_path): return rel_path
                    filename = os.path.basename(path)
                    for root, dirs, files in os.walk(os.getcwd()):
                        if filename in files: return os.path.join(root, filename)
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
                f.write(f"## 🔧 Evolution Event: {datetime.now()}\n")
                f.write(f"- **Target:** `{file_path}`\n")
                f.write(f"- **Trigger:** `{error_msg}`\n")
                f.write(f"- **Outcome:** Neural Link verified. Patch applied.\n\n")
        except:
            pass

    def self_diagnose(self):
        print("🏥 Hephaestus: Running System Diagnostics...", flush=True)
        issues = []
        if not model_manager.is_configured: issues.append("ModelManager not configured.")
        try: get_db()
        except: issues.append("Database connection failed.")
        if not os.path.exists('logs'): issues.append("Logs directory missing.")
        if issues:
            print(f"⚠️ Diagnostics Found Issues: {issues}", flush=True)
            if "Logs directory missing." in issues:
                os.makedirs('logs', exist_ok=True)
                print("🔧 Fixed: Logs directory created.", flush=True)
        else:
            print("✅ Diagnostics Passed: System Nominal.", flush=True)

hephaestus = HephaestusService()
