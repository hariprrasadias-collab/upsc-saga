import sqlite3
import os
from app import create_app
from app.db import get_db

def fix_schema():
    print("Starting schema repair...")
    app = create_app()
    with app.app_context():
        conn = get_db()
        
        # 1. Fix Mock Tests Table (Add total_marks)
        try:
            conn.execute('ALTER TABLE mock_tests ADD COLUMN total_marks REAL DEFAULT 0')
            print("Added total_marks to mock_tests")
        except sqlite3.OperationalError:
            print("mock_tests.total_marks already exists")

        # 2. Fix Current Affairs Table (Add tags)
        try:
            conn.execute('ALTER TABLE current_affairs ADD COLUMN tags TEXT')
            print("Added tags to current_affairs")
        except sqlite3.OperationalError:
            print("current_affairs.tags already exists")

        # 3. Create Syllabus Tables
        print("Creating syllabus tables...")
        conn.execute('''
            CREATE TABLE IF NOT EXISTS syllabus_topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                paper TEXT NOT NULL, -- GS1, GS2, etc.
                topic TEXT NOT NULL,
                subtopic TEXT,
                status TEXT DEFAULT 'Not Started', -- Not Started, Reading, Notes Done, Revision 1, Revision 2, Completed
                notes TEXT,
                importance TEXT DEFAULT 'Medium', -- High, Medium, Low
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS topic_revisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic_id INTEGER NOT NULL,
                revision_count INTEGER DEFAULT 0,
                last_revised_at TIMESTAMP,
                next_revision_date DATE,
                status TEXT DEFAULT 'pending',
                FOREIGN KEY (topic_id) REFERENCES syllabus_topics (id)
            )
        ''')

        # 4. Create PYQ Tables
        print("Creating PYQ tables...")
        conn.execute('''
            CREATE TABLE IF NOT EXISTS pyq_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year INTEGER,
                subject TEXT,
                topic TEXT,
                question_text TEXT,
                option_a TEXT,
                option_b TEXT,
                option_c TEXT,
                option_d TEXT,
                correct_option TEXT,
                explanation TEXT,
                difficulty TEXT,
                is_favorite BOOLEAN DEFAULT 0
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS pyq_quiz_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER DEFAULT 1,
                title TEXT,
                total_questions INTEGER,
                filters TEXT, -- JSON
                score REAL,
                correct_count INTEGER,
                incorrect_count INTEGER,
                duration_seconds INTEGER,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                submitted_at TIMESTAMP,
                status TEXT DEFAULT 'in_progress'
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS pyq_quiz_answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                question_id INTEGER,
                selected_answer TEXT,
                is_correct BOOLEAN,
                time_spent INTEGER,
                marked_for_review BOOLEAN DEFAULT 0,
                FOREIGN KEY (session_id) REFERENCES pyq_quiz_sessions (id),
                FOREIGN KEY (question_id) REFERENCES pyq_questions (id)
            )
        ''')

        # 5. Create Revision Schedules (Scheduler)
        print("Creating revision_schedules table...")
        conn.execute('''
            CREATE TABLE IF NOT EXISTS revision_schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_type TEXT NOT NULL, -- 'flashcard', 'topic', 'article'
                item_id INTEGER NOT NULL,
                next_review TIMESTAMP,
                interval INTEGER DEFAULT 1,
                ease_factor REAL DEFAULT 2.5,
                review_count INTEGER DEFAULT 0,
                last_reviewed TIMESTAMP
            )
        ''')

        # 6. Create Weak Area Analysis Tables
        print("Creating weak area analysis tables...")
        conn.execute('''
            CREATE TABLE IF NOT EXISTS weak_area_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER DEFAULT 1,
                subject TEXT,
                topic TEXT,
                total_attempts INTEGER DEFAULT 0,
                correct_attempts INTEGER DEFAULT 0,
                accuracy_rate REAL DEFAULT 0,
                trend TEXT DEFAULT 'stable',
                priority_score REAL DEFAULT 0,
                last_attempt_date TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS targeted_practice_sets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER DEFAULT 1,
                set_name TEXT,
                focus_topics TEXT,
                question_ids TEXT, -- JSON
                total_questions INTEGER,
                completed INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS practice_set_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                practice_set_id INTEGER,
                question_id INTEGER,
                is_correct BOOLEAN,
                time_taken INTEGER,
                FOREIGN KEY (practice_set_id) REFERENCES targeted_practice_sets (id)
            )
        ''')
        
        # 7. Create Answer Writing Tables (if missing)
        print("Creating answer writing tables...")
        from app.db_models.answer_writing import init_answer_writing_tables
        init_answer_writing_tables()
        
        # 8. Create Questions Master (if missing, referenced in weak_area_service)
        # This seems to be a unified view or table for all questions. 
        # For now, let's assume it might be an alias or we create a simple one.
        # Actually, weak_area_service queries it directly.
        conn.execute('''
            CREATE TABLE IF NOT EXISTS questions_master (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_text TEXT,
                subject TEXT,
                topic TEXT,
                difficulty TEXT,
                source TEXT -- 'pyq', 'mock', 'generated'
            )
        ''')

        # 9. Create Pomodoro Sessions Table
        print("Creating pomodoro_sessions table...")
        # Note: analytics_service.py expects 'timestamp' column, not 'completed_at'
        conn.execute('''
            CREATE TABLE IF NOT EXISTS pomodoro_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER DEFAULT 1,
                task_id INTEGER,
                duration_minutes INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Renamed from completed_at
                focus_score INTEGER,
                notes TEXT
            )
        ''')
        # Also check if table exists but has wrong column name (if created by previous run)
        try:
            conn.execute('ALTER TABLE pomodoro_sessions ADD COLUMN timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
        except sqlite3.OperationalError:
            pass # Column likely exists

        # 10. Create Mind Maps Table
        print("Creating mind_maps table...")
        conn.execute('''
            CREATE TABLE IF NOT EXISTS mind_maps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER DEFAULT 1,
                title TEXT, -- Added title
                topic TEXT NOT NULL,
                structure TEXT, -- JSON
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        try:
            conn.execute('ALTER TABLE mind_maps ADD COLUMN title TEXT')
        except sqlite3.OperationalError:
            pass

        # 11. Create Answer Submissions Table
        print("Creating answer_submissions table...")
        conn.execute('''
            CREATE TABLE IF NOT EXISTS answer_submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER DEFAULT 1,
                question_id INTEGER,
                answer_text TEXT,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                score REAL,
                feedback TEXT
            )
        ''')

        # 12. Create Essay Submissions Table
        print("Creating essay_submissions table...")
        conn.execute('''
            CREATE TABLE IF NOT EXISTS essay_submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER DEFAULT 1,
                topic TEXT,
                content TEXT,
                evaluation_json TEXT,
                score REAL,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 13. Fix Pomodoro Duration Column
        # analytics_service.py uses 'duration', schema had 'duration_minutes'
        try:
            conn.execute('ALTER TABLE pomodoro_sessions ADD COLUMN duration INTEGER')
            # Copy data if needed, or just leave it. 
            conn.execute('UPDATE pomodoro_sessions SET duration = duration_minutes WHERE duration IS NULL')
        except sqlite3.OperationalError:
            pass 

        # 14. Create test_results VIEW (Alias for test_attempts)
        print("Creating test_results view...")
        conn.execute('DROP VIEW IF EXISTS test_results')
        conn.execute('''
            CREATE VIEW test_results AS 
            SELECT * FROM test_attempts
        ''')

        # 15. Create user_question_attempts (for CSAT stats)
        print("Creating user_question_attempts table...")
        conn.execute('''
            CREATE TABLE IF NOT EXISTS user_question_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                question_id INTEGER,
                topic TEXT,
                is_correct BOOLEAN,
                attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 16. Fix Decks Table (Add description, color)
        print("Fixing decks table...")
        try:
            conn.execute('ALTER TABLE decks ADD COLUMN description TEXT')
        except sqlite3.OperationalError:
            pass
        try:
            conn.execute('ALTER TABLE decks ADD COLUMN color TEXT DEFAULT "#3498db"')
        except sqlite3.OperationalError:
            pass

        # 17. Fix Flashcards Table (Add card_type, source_id, tags)
        print("Fixing flashcards table...")
        try:
            conn.execute('ALTER TABLE flashcards ADD COLUMN card_type TEXT DEFAULT "basic"')
        except sqlite3.OperationalError:
            pass
        try:
            conn.execute('ALTER TABLE flashcards ADD COLUMN source_id INTEGER')
        except sqlite3.OperationalError:
            pass
        try:
            conn.execute('ALTER TABLE flashcards ADD COLUMN tags TEXT') # JSON string
        except sqlite3.OperationalError:
            pass

        # 18. Create Custom Bosses Table
        print("Creating custom_bosses table...")
        conn.execute('''
            CREATE TABLE IF NOT EXISTS custom_bosses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                filters TEXT NOT NULL, -- JSON
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 19. Create Badges Tables
        print("Creating badges tables...")
        conn.execute('''
            CREATE TABLE IF NOT EXISTS badges (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                icon TEXT,
                category TEXT, -- 'Scholar', 'Warrior', 'Monk'
                rarity TEXT, -- 'Common', 'Rare', 'Legendary'
                unlock_criteria TEXT, -- JSON or string "stat:value"
                xp_reward INTEGER DEFAULT 100
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS user_badges (
                user_id INTEGER,
                badge_id TEXT,
                unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, badge_id),
                FOREIGN KEY (badge_id) REFERENCES badges (id)
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS badge_progress (
                user_id INTEGER,
                badge_id TEXT,
                current_value INTEGER DEFAULT 0,
                target_value INTEGER,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, badge_id)
            )
        ''')

        conn.commit()
        print("✅ Schema repair completed successfully!")

if __name__ == "__main__":
    fix_schema()
