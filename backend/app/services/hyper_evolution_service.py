"""
Hyper-Evolution Engine (The Singularity)
A continuous background loop that aggressively optimizes the codebase.
"""
import os
import time
import threading
import json
import random
from datetime import datetime
from app.services.model_manager import model_manager
from app.services.hephaestus_service import hephaestus
from app.db import get_db

class HyperEvolutionService:
    def __init__(self):
        self.active = False
        self.stream_log = [] # In-memory buffer for UI
        self.thread = None
        self._log_lock = threading.Lock()

    def start_loop(self, interval_seconds=300):
        """Start the continuous evolution loop"""
        if self.active: return
        self.active = True
        self.thread = threading.Thread(target=self._loop, args=(interval_seconds,), daemon=True)
        self.thread.start()
        self.log_event("SYSTEM", "Hyper-Evolution Engine Initiated. The Singularity has begun.")

    def stop_loop(self):
        self.active = False
        self.log_event("SYSTEM", "Hyper-Evolution Engine Paused.")

    def log_event(self, actor, message, metadata=None):
        """Add to live stream"""
        with self._log_lock:
            event = {
                "timestamp": datetime.now().isoformat(),
                "actor": actor,
                "message": message,
                "metadata": metadata
            }
            self.stream_log.append(event)
            # Keep buffer small
            if len(self.stream_log) > 100:
                self.stream_log.pop(0)
            print(f"🧬 [{actor}] {message}")

    def get_stream(self):
        with self._log_lock:
            return list(self.stream_log)

    def _loop(self, interval):
        """The Main Thinking Loop"""
        while self.active:
            try:
                # 1. Select Target
                target_file = self._select_target()
                if not target_file:
                    self.log_event("Scanner", "No suitable targets found. Sleeping.")
                    time.sleep(interval)
                    continue

                filename = os.path.basename(target_file)
                self.log_event("Scanner", f"Acquired Target: {filename}")

                # 2. Analyze (Hephaestus Integration)
                self.log_event("Hephaestus", f"Analyzing {filename} for structural weakness...")

                # We reuse Hephaestus but wrap it to capture logs
                # We need to manually invoke the LLM here to get the "Thinking" output visible
                with open(target_file, 'r', encoding='utf-8') as f:
                    code = f.read()

                # Phase 1: Critique
                self.log_event("Hephaestus", "Generating Optimization Strategy...")
                critique_prompt = f"""
                Analyze this code for '20x Effectiveness'.
                Code: {filename}

                Identify ONE major improvement:
                1. Performance (Vectorization/Caching).
                2. Autonomy (Remove hardcoded logic).
                3. Robustness (Better error handling).

                Output ONLY the critique.
                """
                critique = model_manager.generate_content(critique_prompt, model_type='fast').text
                self.log_event("Oracle", f"Insight: {critique[:100]}...")

                # Phase 2: Evolve
                self.log_event("Hephaestus", "Rewriting Codebase...")
                success = hephaestus.evolve_feature(target_file)

                if success:
                    self.log_event("System", f"Evolution Applied to {filename}. Version incremented.")
                else:
                    self.log_event("System", f"Evolution Skipped for {filename} (No improvement found).")

            except Exception as e:
                self.log_event("Error", f"Singularity Loop Failed: {e}")

            time.sleep(interval)

    def _select_target(self):
        """Randomly select a python file from services/routes"""
        candidates = []
        base_dir = os.path.join(os.getcwd(), 'backend', 'app')
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                if file.endswith('.py') and file != '__init__.py':
                    candidates.append(os.path.join(root, file))

        if candidates:
            return random.choice(candidates)
        return None

hyper_evolution = HyperEvolutionService()
