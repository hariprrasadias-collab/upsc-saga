"""
The Architect - Meta-Strategy Engine
Optimizes the optimizer.
"""
from app.services.hephaestus_service import hephaestus
from app.db import get_db
import os

class ArchitectService:
    def __init__(self):
        pass

    def review_system_performance(self):
        """
        Checks if Prometheus/Director strategies are actually working.
        If not, it triggers Hephaestus to evolve them.
        """
        print("🏗️ Architect: Reviewing Strategic Algorithms...")
        try:
            conn = get_db()

            # 1. Measure Efficacy
            # Check impact_score of recent actions
            # Impact score is updated by user feedback or self-correction loops
            stats = conn.execute('''
                SELECT action_type, AVG(impact_score) as avg_impact
                FROM brain_action_log
                WHERE action_type IN ('CONSULT_GOLDEN_PATH', 'DIRECTOR_INTERVENTION')
                GROUP BY action_type
            ''').fetchall()

            for row in stats:
                action = row['action_type']
                score = row['avg_impact'] or 0

                print(f"🏗️ Architect: {action} Impact = {score:.2f}")

                # Threshold for Evolution
                # If score is low (or None/0 initially), we might want to evolve to kickstart it
                if score < 0.3:
                    print(f"⚠️ Architect: {action} is ineffective. Initiating Evolution Protocol.")
                    self._evolve_algorithm(action)

            # Also randomly evolve Prometheus if it exists
            # to keep it fresh
            import random
            if random.random() < 0.1:
                self._evolve_algorithm('PROMETHEUS_FORECAST')

        except Exception as e:
            print(f"Architect Failed: {e}")

    def _evolve_algorithm(self, action_type):
        """
        Triggers Hephaestus to rewrite the service responsible for the action.
        """
        target_file = None
        if action_type == 'CONSULT_GOLDEN_PATH':
            target_file = 'backend/app/services/golden_path_service.py'
        elif action_type == 'DIRECTOR_INTERVENTION':
            target_file = 'backend/app/services/director_service.py'
        elif action_type == 'PROMETHEUS_FORECAST':
            target_file = 'backend/app/services/prometheus_service.py'

        if target_file:
            print(f"🏗️ Architect: Evolving {target_file}...")
            abs_path = os.path.join(os.getcwd(), target_file)
            hephaestus.evolve_feature(abs_path)

architect_service = ArchitectService()
