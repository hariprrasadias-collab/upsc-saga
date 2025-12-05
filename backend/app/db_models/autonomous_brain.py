from app.db import get_db

def init_autonomous_brain_tables():
    """Initialize tables for Autonomous Brain capabilities"""
    conn = get_db()
    
    # User preferences for autonomy
    conn.execute('''
        CREATE TABLE IF NOT EXISTS brain_user_preferences (
            user_id INTEGER PRIMARY KEY,
            autonomy_level TEXT DEFAULT 'manual',  -- 'manual', 'semi_auto', 'full_auto'
            auto_execute_content_curation BOOLEAN DEFAULT FALSE,
            auto_execute_scheduling BOOLEAN DEFAULT FALSE,
            auto_execute_flashcard_generation BOOLEAN DEFAULT FALSE,
            auto_execute_cleanup BOOLEAN DEFAULT FALSE,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Action logging for tracking Brain's decisions
    conn.execute('''
        CREATE TABLE IF NOT EXISTS brain_action_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL DEFAULT 1,
            action_type TEXT NOT NULL,
            action_payload JSON,
            action_label TEXT,
            executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            executed_by TEXT DEFAULT 'manual',  -- 'manual', 'auto', 'scheduled'
            outcome_status TEXT DEFAULT 'pending',  -- 'pending', 'success', 'failure', 'ignored', 'undone'
            outcome_measured_at TIMESTAMP,
            impact_score REAL,  -- -1.0 to 1.0
            user_feedback TEXT,
            context_snapshot JSON,
            reasoning TEXT,  -- Why Brain took this action
            confidence_score REAL  -- 0.0 to 1.0
        )
    ''')
    
    # Pattern learning storage
    conn.execute('''
        CREATE TABLE IF NOT EXISTS brain_learning_patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL DEFAULT 1,
            pattern_type TEXT NOT NULL,  -- 'successful_workflow', 'failed_action', 'user_override', 'optimal_timing'
            pattern_data JSON NOT NULL,
            confidence_score REAL DEFAULT 0.5,  -- 0.0 to 1.0, increases with observations
            times_observed INTEGER DEFAULT 1,
            last_observed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Weekly self-review logs
    conn.execute('''
        CREATE TABLE IF NOT EXISTS brain_self_reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            review_week TEXT NOT NULL,  -- Format: 2025-W48
            actions_taken INTEGER,
            success_rate REAL,
            user_satisfaction_score REAL,
            mistakes_detected INTEGER,
            self_corrections_made INTEGER,
            improvement_plan JSON,
            reviewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Blacklisted actions (Brain learns to avoid these)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS brain_action_blacklist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action_type TEXT NOT NULL,
            reason TEXT,
            failure_count INTEGER DEFAULT 0,
            blacklisted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            blacklist_until TIMESTAMP,  -- NULL = permanent
            auto_blacklisted BOOLEAN DEFAULT TRUE
        )
    ''')
    
    # Optimization opportunities (Proactive suggestions)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS brain_optimization_opportunities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL DEFAULT 1,
            type TEXT NOT NULL,  -- 'schedule', 'resource', 'load_balance'
            description TEXT NOT NULL,
            payload JSON,
            status TEXT DEFAULT 'pending',  -- 'pending', 'accepted', 'rejected', 'expired'
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP
        )
    ''')
    
    # A/B Testing Framework
    conn.execute('''
        CREATE TABLE IF NOT EXISTS brain_ab_tests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            test_name TEXT NOT NULL,
            strategy_a TEXT NOT NULL,
            strategy_b TEXT NOT NULL,
            active_strategy TEXT,  -- 'A' or 'B' (for current user)
            start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            end_date TIMESTAMP,
            status TEXT DEFAULT 'active',
            results JSON
        )
    ''')

    # Goal Tracking
    conn.execute('''
        CREATE TABLE IF NOT EXISTS brain_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL DEFAULT 1,
            title TEXT NOT NULL,
            type TEXT NOT NULL, -- 'syllabus', 'questions', 'hours', 'accuracy'
            target_value REAL NOT NULL,
            current_value REAL DEFAULT 0,
            deadline TIMESTAMP,
            status TEXT DEFAULT 'active', -- 'active', 'completed', 'failed'
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    print("✅ Autonomous Brain tables initialized")
