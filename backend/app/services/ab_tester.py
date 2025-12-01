from app.db import get_db
from datetime import datetime, timedelta
import json
import random

class ABTester:
    """
    Service to run A/B tests on Brain strategies to optimize user performance.
    """

    def create_test(self, test_name, strategy_a, strategy_b, duration_days=7):
        """
        Initialize a new A/B test.
        """
        conn = get_db()
        
        # Check if test already exists
        existing = conn.execute('SELECT * FROM brain_ab_tests WHERE test_name = ?', (test_name,)).fetchone()
        if existing:
            return {'success': False, 'message': 'Test already exists'}
            
        # Assign user to A or B (randomly for now, or based on user ID hash)
        # For a single user app, we might alternate days or weeks
        # Here, let's assume we test one strategy for a week, then switch?
        # Or simpler: Just assign a strategy for this "run" of the test
        active_strategy = random.choice(['A', 'B'])
        
        cursor = conn.execute('''
            INSERT INTO brain_ab_tests (
                test_name, strategy_a, strategy_b, active_strategy, end_date
            ) VALUES (?, ?, ?, ?, ?)
        ''', (
            test_name,
            strategy_a,
            strategy_b,
            active_strategy,
            (datetime.utcnow() + timedelta(days=duration_days)).isoformat()
        ))
        conn.commit()
        
        return {
            'id': cursor.lastrowid,
            'test_name': test_name,
            'active_strategy': active_strategy,
            'message': f"Test started. Active strategy: {active_strategy}"
        }

    def get_active_strategy(self, test_name):
        """
        Get the currently active strategy for a given test.
        Useful for other services to know how to behave.
        """
        conn = get_db()
        test = conn.execute('''
            SELECT active_strategy, status FROM brain_ab_tests 
            WHERE test_name = ? AND status = 'active'
        ''', (test_name,)).fetchone()
        
        if not test:
            return None # No active test
            
        return test['active_strategy']

    def log_result(self, test_name, metric_name, value):
        """
        Log a performance metric for the current strategy.
        """
        conn = get_db()
        test = conn.execute('SELECT * FROM brain_ab_tests WHERE test_name = ?', (test_name,)).fetchone()
        
        if not test or test['status'] != 'active':
            return False
            
        current_results = json.loads(test['results']) if test['results'] else {'A': [], 'B': []}
        strategy = test['active_strategy']
        
        if strategy not in current_results:
            current_results[strategy] = []
            
        current_results[strategy].append({
            'metric': metric_name,
            'value': value,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        conn.execute('''
            UPDATE brain_ab_tests
            SET results = ?
            WHERE id = ?
        ''', (json.dumps(current_results), test['id']))
        conn.commit()
        
        return True

    def get_test_results(self, test_name):
        """
        Analyze results of a test.
        """
        conn = get_db()
        test = conn.execute('SELECT * FROM brain_ab_tests WHERE test_name = ?', (test_name,)).fetchone()
        
        if not test:
            return None
            
        results = json.loads(test['results']) if test['results'] else {'A': [], 'B': []}
        
        # Simple analysis: Average of metrics
        analysis = {}
        for strategy in ['A', 'B']:
            values = [r['value'] for r in results.get(strategy, [])]
            if values:
                analysis[strategy] = sum(values) / len(values)
            else:
                analysis[strategy] = 0
                
        return {
            'test_name': test_name,
            'status': test['status'],
            'active_strategy': test['active_strategy'],
            'raw_results': results,
            'analysis': analysis,
            'winner': 'A' if analysis.get('A', 0) > analysis.get('B', 0) else 'B'
        }

# Singleton instance
ab_tester = ABTester()
