from app.db import get_db
from app.services.brain_service import brain_service
from datetime import datetime, timedelta
import json

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
        since = (datetime.utcnow() - timedelta(days=lookback_days)).isoformat()
        
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

        # 4. Generate Improvement Plan (using BrainService/Gemini)
        # We ask the Brain to reflect on its own stats
        reflection_prompt = f"""
        Analyze your performance over the last {lookback_days} days:
        - Total Actions: {total}
        - Success Rate: {success_rate:.1f}%
        - Average Impact: {avg_impact:.2f}
        - Top Mistakes: {json.dumps(top_mistakes)}
        - Top Successes: {json.dumps(top_successes)}
        
        Provide a brief 3-point improvement plan for the next week.
        Format as JSON: {{"plan": ["point 1", "point 2", "point 3"]}}
        """
        
        try:
            # We use a simplified thinking process here to avoid infinite loops
            # In a real system, we'd have a dedicated 'meta-cognition' model prompt
            improvement_plan = {
                "plan": [
                    f"Focus on reducing {top_mistakes[0]['action_type']} failures" if top_mistakes else "Maintain current performance",
                    "Increase autonomy for successful actions",
                    "Ask for more user feedback"
                ]
            }
            # TODO: Integrate actual Gemini call here for dynamic reflection
        except Exception as e:
            print(f"Reflection failed: {e}")
            improvement_plan = {"plan": ["Continue monitoring performance"]}

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
            0, # TODO: Track correction counts
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
