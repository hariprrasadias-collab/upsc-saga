"""
Project Prometheus - Strategic Forecasting Engine
Runs parallel simulations to determine the optimal daily strategy.
"""
from app.services.foresight_engine import foresight_engine
from app.services.model_manager import model_manager
import json

class PrometheusService:
    def __init__(self):
        pass

    def run_strategy_simulation(self):
        """
        Runs scenario analysis to find the optimal study path.
        """
        print("🔥 Prometheus: Running Scenario Analysis...")

        try:
            # 1. Get Baseline
            base_sim = foresight_engine.simulate_exam_outcome()

            # 2. AI Wargaming
            prompt = f"""
            # MISSION: STRATEGIC WARGAMING (PROJECT PROMETHEUS)
            **Current Status (Monte Carlo):**
            {json.dumps(base_sim)}

            **TASK:**
            Simulate the outcome of 3 distinct strategies over the next 30 days based on this data.

            1. **Operation Hammer (Aggressive):** Focus 80% time on the weakest subjects. High intensity.
            2. **Operation Fortress (Defensive):** Consolidate strong subjects to 100% accuracy. Ignore weaknesses.
            3. **Operation Flow (Adaptive):** Follow energy levels, ignoring fixed schedules.

            **DIRECTIVE:**
            Select the Winning Strategy that maximizes the probability of clearing the cutoff.

            **OUTPUT JSON:**
            {{
                "winning_strategy": "OPERATION_...",
                "confidence_score": 0.0-1.0,
                "rationale": "Why this wins...",
                "projected_score_delta": "+X Marks",
                "daily_directive": "One sentence command for today."
            }}
            """

            response = model_manager.generate_content(prompt, model_type='pro')
            text = response.text.strip()
            if text.startswith("```"): text = text.replace("```json", "").replace("```", "").strip()

            analysis = json.loads(text)

            return {
                "success": True,
                "timestamp": base_sim.get('timestamp'), # generated now
                "analysis": analysis
            }

        except Exception as e:
            print(f"Prometheus Failed: {e}")
            return {"success": False, "error": str(e)}

prometheus_service = PrometheusService()
