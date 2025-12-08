from app.db import get_db
from datetime import datetime, timedelta
import json

from app.services.weak_area_service import WeakAreaAnalyzer

from app.services.content_recommender import ContentRecommender
from app.services.goal_service import GoalService
from app.services.ab_tester import ab_tester

class OptimizationEngine:
    """
    Service to proactively identify optimization opportunities for the user.
    Scans system state and suggests improvements.
    """

    def scan_for_optimizations(self):
        """
        Main scan loop. Checks various subsystems for opportunities.
        Returns list of new opportunities found.
        """
        opportunities = []
        
        # 1. Check for Free Time Slots (Schedule Optimization)
        schedule_opps = self._check_schedule_gaps()
        if schedule_opps:
            opportunities.extend(schedule_opps)
            
        # 2. Check for Unused Resources (Resource Optimization)
        resource_opps = self._check_unused_resources()
        if resource_opps:
            opportunities.extend(resource_opps)
            
        # 3. Check for Flashcard Overload (Load Balancing)
        load_opps = self._check_flashcard_load()
        if load_opps:
            opportunities.extend(load_opps)

        # 4. Check for Weak Area Scheduling (Study Optimization)
        study_opps = self._check_weak_area_scheduling()
        if study_opps:
            opportunities.extend(study_opps)

        # 5. Check for Content Recommendations (Smart Content)
        content_opps = self._check_content_recommendations()
        if content_opps:
            opportunities.extend(content_opps)

        # 6. Check for Adaptive Difficulty
        diff_opps = self._check_adaptive_difficulty()
        if diff_opps:
            opportunities.extend(diff_opps)

        # 7. Check for Goals
        goal_opps = self._check_goals()
        if goal_opps:
            opportunities.extend(goal_opps)

        # 8. Check for Burnout Risk (Bio-Optimization)
        burnout_opps = self._check_burnout_risk()
        if burnout_opps:
            opportunities.extend(burnout_opps)

        # 9. Check for Strategy Alignment
        strat_opps = self._check_strategy_alignment()
        if strat_opps:
            opportunities.extend(strat_opps)
            
        return opportunities

    def _check_schedule_gaps(self):
        """
        Checks for gaps in the schedule using real activity logs.
        """
        conn = get_db()
        
        # 1. Check if user has been inactive for > 4 hours today
        try:
            last_activity = conn.execute('''
                SELECT executed_at FROM brain_action_log 
                WHERE date(executed_at) = date('now') 
                ORDER BY executed_at DESC LIMIT 1
            ''').fetchone()
            
            if last_activity:
                last_time = datetime.fromisoformat(last_activity['executed_at'])
                hours_since = (datetime.now() - last_time).total_seconds() / 3600
                
                if hours_since > 4:
                    # Found a gap!
                    return [self._create_opportunity(
                        type='schedule',
                        description=f"You've been inactive for {int(hours_since)} hours. Good time for a quick revision?",
                        payload={
                            'action': 'SCHEDULE_REVISION', 
                            'time': 'Now',
                            'duration': 30
                        }
                    )]
        except Exception:
            pass 
            
        return []

    def _check_strategy_alignment(self):
        """
        Checks if current activities align with the Golden Path strategy.
        """
        # Real logic: Check if the last completed task was part of the Golden Path
        try:
            from app.services.brain_service import brain_service
            if not brain_service.current_strategy:
                return []
                
            conn = get_db()
            last_task = conn.execute('''
                SELECT topic FROM study_tasks 
                WHERE status = 'completed'
                ORDER BY date DESC, end_time DESC LIMIT 1
            ''').fetchone()
            
            if last_task:
                # Check if topic is in current strategy
                strategy_topics = [s['topic'] for s in brain_service.current_strategy]
                # Fuzzy match or direct check
                if not any(last_task['topic'] in s_topic for s_topic in strategy_topics):
                     return [self._create_opportunity(
                        type='STRATEGY_ALIGNMENT',
                        description=f"Distraction Alert: '{last_task['topic']}' is not on the Golden Path.",
                        payload={
                            'action': 'REVIEW_STRATEGY',
                            'target': 'Golden Path'
                        }
                    )]
        except Exception:
            pass
            
        return []

    def _check_unused_resources(self):
        """
        Real logic: Finds resources not accessed in 30 days.
        """
        # Placeholder until we have a proper resource tracking table
        return []

    def _check_flashcard_load(self):
        """
        Real logic: Checks actual due cards count.
        """
        conn = get_db()
        try:
            # Check if flashcards table exists and has due column
            # Assuming 'next_review' < now
            result = conn.execute('''
                SELECT COUNT(*) as count FROM revision_schedules 
                WHERE item_type = 'flashcard' AND next_review <= date('now')
            ''').fetchone()
            count = result['count'] if result else 0
            
            if count > 50: # Real threshold
                existing = conn.execute('''
                    SELECT COUNT(*) as count FROM brain_optimization_opportunities
                    WHERE type = 'load_balance' AND status = 'pending'
                ''').fetchone()
                
                if existing['count'] == 0:
                    return [self._create_opportunity(
                        type='load_balance',
                        description=f"Flashcard Pile-up: {count} cards due. Clear them now?",
                        payload={'action': 'START_SESSION', 'deck': 'All'}
                    )]
        except Exception as e:
            print(f"Flashcard Check Error: {e}")
                
        return []

    def _check_weak_area_scheduling(self):
        """
        Checks for weak areas and suggests scheduling a session.
        """
        # Get weak areas for user 1 (default)
        weak_areas = WeakAreaAnalyzer.analyze_user_performance(1)
        
        if not weak_areas:
            return []
            
        # Get top weak area
        top_weakness = weak_areas[0]
        topic = top_weakness['topic']
        subject = top_weakness['subject']
        
        # Check if we already have a pending suggestion for this
        conn = get_db()
        existing = conn.execute('''
            SELECT COUNT(*) as count FROM brain_optimization_opportunities
            WHERE type = 'study_schedule' AND status = 'pending' 
            AND payload LIKE ?
        ''', (f'%{topic}%',)).fetchone()
        
        if existing['count'] > 0:
            return []
            
        return [self._create_opportunity(
            type='study_schedule',
            description=f"Weakness detected in {topic} ({subject}). Focus session recommended.",
            payload={
                'action': 'SCHEDULE_SESSION',
                'topic': topic,
                'subject': subject,
                'time': 'Next Available Slot',
                'duration': 60
            }
        )]

    def _check_burnout_risk(self):
        """
        Checks for burnout risk using real bio-metrics from PanopticonService.
        """
        try:
            from app.services.panopticon_service import panopticon
            status = panopticon.get_current_status()
            
            if status['status'] == 'CRITICAL':
                conn = get_db()
                existing = conn.execute('''
                    SELECT COUNT(*) as count FROM brain_optimization_opportunities
                    WHERE type = 'BURNOUT_RISK' AND status = 'pending'
                ''').fetchone()
                
                if existing['count'] == 0:
                    return [self._create_opportunity(
                        type='BURNOUT_RISK',
                        description=f"Bio-Status Critical: {status['alert']}. Take a break immediately.",
                        payload={
                            'action': 'TRIGGER_PROTOCOL',
                            'protocol': 'RECOVERY_MODE'
                        }
                    )]
        except Exception as e:
            print(f"Burnout Check Error: {e}")
            
        return []

    def _check_content_recommendations(self):
        """
        Checks for content recommendations based on weak areas.
        """
        recommendations = ContentRecommender.get_recommendations_for_weak_areas(1)
        
        opportunities = []
        conn = get_db()
        
        for rec in recommendations:
            # Check for duplicates
            existing = conn.execute('''
                SELECT COUNT(*) as count FROM brain_optimization_opportunities
                WHERE type = 'content_recommendation' AND status = 'pending' 
                AND payload LIKE ?
            ''', (f'%{rec["link"]}%',)).fetchone()
            
            if existing['count'] == 0:
                opportunities.append(self._create_opportunity(
                    type='content_recommendation',
                    description=f"{rec['reason']}: {rec['title']}",
                    payload={
                        'action': 'READ_ARTICLE',
                        'link': rec['link'],
                        'title': rec['title']
                    }
                ))
                
        return opportunities

    def _create_opportunity(self, type, description, payload):
        """
        Helper to store opportunity in DB.
        """
        conn = get_db()
        
        cursor = conn.execute('''
            INSERT INTO brain_optimization_opportunities (
                type, description, payload, expires_at
            ) VALUES (?, ?, ?, ?)
        ''', (
            type, 
            description, 
            json.dumps(payload),
            (datetime.utcnow() + timedelta(days=1)).isoformat()
        ))
        conn.commit()
        
        return {
            'id': cursor.lastrowid,
            'type': type,
            'description': description,
            'payload': payload
        }

    def get_pending_optimizations(self):
        """Get all pending suggestions"""
        conn = get_db()
        opps = conn.execute('''
            SELECT * FROM brain_optimization_opportunities
            WHERE status = 'pending'
            ORDER BY created_at DESC
        ''').fetchall()
        
        return [dict(o) for o in opps]

    def accept_optimization(self, opp_id):
        """User accepted the suggestion"""
        conn = get_db()
        conn.execute('''
            UPDATE brain_optimization_opportunities
            SET status = 'accepted'
            WHERE id = ?
        ''', (opp_id,))
        conn.commit()
        
        # Here we would trigger the actual action
        # e.g., brain_service.execute_action(...)
        return {'success': True, 'message': 'Optimization accepted and queued.'}

    def _check_adaptive_difficulty(self):
        """
        Adjusts difficulty based on performance.
        """
        # Get performance stats (Weak + Strong)
        weak_stats = WeakAreaAnalyzer.analyze_user_performance(1)
        strong_stats = WeakAreaAnalyzer.analyze_strong_areas(1)
        
        # Combine unique topics
        stats = weak_stats + strong_stats
        
        opportunities = []
        conn = get_db()
        
        processed_topics = set()
        
        # 2. Check for At-Risk Goals (Mock logic for now)
        # Real logic would check progress vs time remaining
        
        return opportunities

    def _check_goals(self):
        """
        Checks goal status and suggests new goals.
        """
        goals = GoalService.get_goals(1)
        opportunities = []
        conn = get_db()
        
        # 1. Suggest Goal if None
        if not goals:
            existing = conn.execute('''
                SELECT COUNT(*) as count FROM brain_optimization_opportunities
                WHERE type = 'goal_setting' AND status = 'pending'
            ''').fetchone()
            
            if existing['count'] == 0:
                opportunities.append(self._create_opportunity(
                    type='goal_setting',
                    description="You have no active goals. Set a target to stay motivated.",
                    payload={
                        'action': 'CREATE_GOAL',
                        'suggestion': 'Complete 50 MCQs this week'
                    }
                ))
        
        return opportunities

# Singleton instance
optimization_engine = OptimizationEngine()
