from app.db import get_db
from datetime import datetime, timedelta
import json
import re
from app.services.model_manager import model_manager

class SelfReviewService:
    """
    Service to perform periodic self-reviews of the Brain's performance.
    Generates a report card and improvement plan.
    """

    def perform_review(self, lookback_days=7):
        """
        Analyze performance over the last N days.
        """
        conn = get_db()
        since = (datetime.utcnow() - timedelta(days=lookback_days)).strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"🧐 Starting Self-Review for last {lookback_days} days...")

        # 1. Gather Metrics
        stats = conn.execute('''
            SELECT 
                COUNT(*) as total_actions,
                SUM(CASE WHEN outcome_status = 'success' THEN 1 ELSE 0 END) as successes,
                SUM(CASE WHEN outcome_status = 'failure' THEN 1 ELSE 0 END) as failures,
                AVG(impact_score) as avg_impact
            FROM brain_action_log
            WHERE executed_at >= ?
        ''', (since,)).fetchone()
        
        total = stats['total_actions'] or 0
        success_rate = (stats['successes'] / total * 100) if total > 0 else 0.0
        avg_impact = stats['avg_impact'] or 0.0
        
        # 2. Identify Top Mistakes
        mistakes = conn.execute('''
            SELECT action_type, COUNT(*) as count
            FROM brain_action_log
            WHERE executed_at >= ? AND outcome_status = 'failure'
            GROUP BY action_type
            ORDER BY count DESC
            LIMIT 3
        ''', (since,)).fetchall()
        
        top_mistakes = [dict(m) for m in mistakes]
        
        # 3. Identify Top Successes
        successes = conn.execute('''
            SELECT action_type, COUNT(*) as count
            FROM brain_action_log
            WHERE executed_at >= ? AND outcome_status = 'success'
            GROUP BY action_type
            ORDER BY count DESC
            LIMIT 3
        ''', (since,)).fetchall()
        
        top_successes = [dict(s) for s in successes]
        
        # 3.1 Identify Self-Corrections
        corrections = conn.execute('''
            SELECT COUNT(*) as count
            FROM brain_action_log
            WHERE executed_at >= ? AND outcome_status IN ('undone', 'corrected')
        ''', (since,)).fetchone()
        correction_count = corrections['count'] if corrections else 0

        # 4. Generate Improvement Plan (using Gemini API via ModelManager)
        # We ask the Brain to reflect on its own stats
        reflection_prompt = f"""
        # SYSTEM ROLE: THE ARCHITECT (Self-Correction Module)
        You are the internal audit mechanism for the "Brain" (an AI UPSC Coach).
        Your job is to ruthlessly analyze performance metrics and prescribe optimization protocols.

        # PERFORMANCE DATA ({lookback_days} DAYS):
        - **Total Actions:** {total}
        - **Success Rate:** {success_rate:.1f}%
        - **Average Impact Score:** {avg_impact:.2f}
        - **Self Corrections:** {correction_count}
        - **Top Failures:** {json.dumps(top_mistakes)}
        - **Top Successes:** {json.dumps(top_successes)}
        
        # MISSION:
        Analyze the data. Identify patterns of failure. Prescribe a concrete, actionable 3-point plan for the next week.
        Do not be generic. Be specific to the "Action Types" mentioned in mistakes.

        # OUTPUT SCHEMA (JSON ONLY):
        {{
            "plan": [
                "Actionable Point 1 (Focus on correcting X...)",
                "Actionable Point 2 (Leverage success in Y...)",
                "Actionable Point 3 (System optimization...)"
            ]
        }}
        """
        
        try:
            # Generate AI Reflection (Pro model for complex reasoning)
            response = model_manager.generate_content(reflection_prompt, model_type='pro')
            text = response.text.strip()
            
            # Robust JSON Extraction
            text = text.strip()
            if text.startswith("```"):
                text = text.replace('```json', '').replace('```', '').strip()

            start = text.find('{')
            end = text.rfind('}')
            
            if start != -1 and end != -1:
                 improvement_plan = json.loads(text[start:end+1])
            else:
                 # Check for Panic Mode / Fallback text
                 if "Oracle is silent" in text or "error" in text.lower():
                     print("ℹ️ Metrics available, but AI Reflection unavailable (Panic Mode). using default plan.")
                     improvement_plan = {"plan": ["Review metrics manually", "Check system logs", "Retry analysis later"]}
                 else:
                     raise ValueError("No JSON found")

            # Basic validation
            if "plan" not in improvement_plan or not isinstance(improvement_plan["plan"], list):
                 improvement_plan = {"plan": ["Refine prompt engineering", "Monitor resource usage", "Optimize feedback loops"]}

        except Exception as e:
            print(f"Reflection failed (Using fallback): {e}")
            improvement_plan = {"plan": ["Continue monitoring performance", "Verify API connectivity"]}

        # 5. Store Review
        week_num = datetime.now().strftime("%Y-W%U")
        
        cursor = conn.execute('''
            INSERT INTO brain_self_reviews (
                review_week, actions_taken, success_rate, 
                user_satisfaction_score, mistakes_detected, 
                self_corrections_made, improvement_plan
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            week_num,
            total,
            success_rate,
            avg_impact * 100, # Normalize to 0-100 roughly
            stats['failures'] or 0,
            correction_count,
            json.dumps(improvement_plan)
        ))
        conn.commit()
        
        return {
            'review_id': cursor.lastrowid,
            'week': week_num,
            'stats': {
                'total': total,
                'success_rate': success_rate,
                'avg_impact': avg_impact
            },
            'improvement_plan': improvement_plan
        }

    def get_latest_review(self):
        """Get the most recent self-review"""
        conn = get_db()
        review = conn.execute('''
            SELECT * FROM brain_self_reviews 
            ORDER BY reviewed_at DESC LIMIT 1
        ''').fetchone()
        
        if not review:
            return None
            
        return dict(review)

# Singleton instance
self_review_service = SelfReviewService()
