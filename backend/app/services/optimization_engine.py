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
            
        return opportunities

    def _check_schedule_gaps(self):
        """
        Checks for gaps in the schedule, using A/B testing to optimize timing.
        """
        conn = get_db()
        
        # 1. Initialize/Get A/B Test
        test_name = "OptimalStudyTime"
        strategy = ab_tester.get_active_strategy(test_name)
        
        if not strategy:
            # Start the test if not exists
            ab_tester.create_test(
                test_name=test_name,
                strategy_a="Morning Focus",
                strategy_b="Evening Focus",
                duration_days=14
            )
            strategy = "A" # Default to A for first run
            
        # 2. Define time preference based on strategy
        # Strategy A: Morning (6 AM - 12 PM)
        # Strategy B: Evening (6 PM - 10 PM)
        preferred_time_desc = "morning" if strategy == 'A' else "evening"
        
        # 3. Check for existing pending suggestions to avoid spam
        existing = conn.execute('''
            SELECT COUNT(*) as count FROM brain_optimization_opportunities
            WHERE type = 'schedule' AND status = 'pending'
        ''').fetchone()
        
        if existing['count'] > 0:
            return [] 
            
        # 4. Create Opportunity (Mocking the gap finding)
        # In real app, we'd search for actual gaps in the preferred window
        return [self._create_opportunity(
            type='schedule',
            description=f"A/B Test ({strategy}): You have a free slot this {preferred_time_desc}. Perfect for a Mock Test.",
            payload={
                'action': 'CREATE_MOCK_TEST', 
                'time': f"Saturday {'9:00 AM' if strategy == 'A' else '7:00 PM'}",
                'ab_test_id': test_name,
                'strategy': strategy
            }
        )]

    def _check_unused_resources(self):
        """
        Mock logic: Finds resources not accessed in 2 weeks.
        """
        # Simulating finding unused notes
        return [] # Keeping it simple for now

    def _check_flashcard_load(self):
        """
        Mock logic: Checks if due cards > 500.
        """
        conn = get_db()
        
        # Count due cards (assuming table exists, otherwise 0)
        try:
            result = conn.execute('SELECT COUNT(*) as count FROM flashcards').fetchone()
            count = result['count'] if result else 0
        except:
            count = 600 # Simulate high load for testing
            
        if count > 500:
            existing = conn.execute('''
                SELECT COUNT(*) as count FROM brain_optimization_opportunities
                WHERE type = 'load_balance' AND status = 'pending'
            ''').fetchone()
            
            if existing['count'] == 0:
                return [self._create_opportunity(
                    type='load_balance',
                    description=f"High load detected ({count} cards). Spread reviews over 3 days?",
                    payload={'action': 'SPREAD_REVIEWS', 'days': 3}
                )]
                
        return []

    def _check_weak_area_scheduling(self):
        """
        Checks for weak areas and suggests scheduling a session.
        """
        # Get weak areas for user 1 (default)
        # In a real app, we'd iterate over all users or pass user_id
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
            
        # Find a slot (Mocking a slot for now, e.g., "Tomorrow Evening")
        # In a real scenario, we'd check the calendar.
        slot = "Tomorrow 7:00 PM"
        
        return [self._create_opportunity(
            type='study_schedule',
            description=f"Weakness detected in {topic} ({subject}). Schedule a focused session?",
            payload={
                'action': 'SCHEDULE_SESSION',
                'topic': topic,
                'subject': subject,
                'time': slot,
                'duration': 60
            }
        )]



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
        
        for topic_stat in stats:
            topic = topic_stat['topic']
            if topic in processed_topics:
                continue
            processed_topics.add(topic)
            
            accuracy = topic_stat['accuracy_rate']
            
            # Logic for increasing difficulty
            if accuracy > 80:
                # Check if we already suggested this
                existing = conn.execute('''
                    SELECT COUNT(*) as count FROM brain_optimization_opportunities
                    WHERE type = 'difficulty_adjustment' AND status = 'pending' 
                    AND payload LIKE ?
                ''', (f'%{topic}%',)).fetchone()
                
                if existing['count'] == 0:
                    opportunities.append(self._create_opportunity(
                        type='difficulty_adjustment',
                        description=f"You're crushing '{topic}' ({int(accuracy)}%). Switch to Hard mode?",
                        payload={
                            'action': 'CHANGE_DIFFICULTY',
                            'topic': topic,
                            'new_difficulty': 'Hard'
                        }
                    ))
            
            # Logic for decreasing difficulty (if struggling)
            elif accuracy < 40 and accuracy > 0: # >0 to avoid new topics
                existing = conn.execute('''
                    SELECT COUNT(*) as count FROM brain_optimization_opportunities
                    WHERE type = 'difficulty_adjustment' AND status = 'pending' 
                    AND payload LIKE ?
                ''', (f'%{topic}%',)).fetchone()
                
                if existing['count'] == 0:
                    opportunities.append(self._create_opportunity(
                        type='difficulty_adjustment',
                        description=f"Struggling with '{topic}' ({int(accuracy)}%). Switch to Easy mode to build basics?",
                        payload={
                            'action': 'CHANGE_DIFFICULTY',
                            'topic': topic,
                            'new_difficulty': 'Easy'
                        }
                    ))
                    
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
        
        # 2. Check for At-Risk Goals (Mock logic for now)
        # Real logic would check progress vs time remaining
        
        return opportunities

# Singleton instance
optimization_engine = OptimizationEngine()
