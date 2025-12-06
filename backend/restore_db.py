from app import create_app
from app.db import get_db
from app.db_models.core import init_core_tables
from app.db_models.study_plan import init_study_plan_tables
from app.db_models.flashcards import init_flashcard_tables
from app.db_models.gamification import init_gamification_tables
from app.db_models.mock_tests import init_mock_test_tables
from app.db_models.current_affairs import init_current_affairs_table
from app.db_models.autonomous_brain import init_autonomous_brain_tables
from app.db_models.mind_palace import init_mind_palace_tables
from app.db_models.night_watchman import init_watchman_tables
from app.db_models.panopticon import init_panopticon_tables
from app.db_models.foresight import init_foresight_tables
from app.db_models.neural_hash import init_neural_hash_tables

print("Starting database restoration...")

app = create_app()
with app.app_context():
    conn = get_db()
    
    print("Initializing Core Tables...")
    init_core_tables()
    
    print("Initializing Study Plan Tables...")
    init_study_plan_tables()
    
    print("Initializing Flashcard Tables...")
    init_flashcard_tables()
    
    print("Initializing Gamification Tables...")
    init_gamification_tables()
    
    print("Initializing Mock Test Tables...")
    init_mock_test_tables()
    
    print("Initializing Current Affairs Tables...")
    init_current_affairs_table()
    
    print("Initializing Autonomous Brain Tables...")
    init_autonomous_brain_tables()
    
    print("Initializing Mind Palace Tables...")
    init_mind_palace_tables()
    
    print("Initializing Night Watchman Tables...")
    init_watchman_tables()
    
    print("Initializing Panopticon Tables...")
    # init_panopticon_tables takes db_path as argument
    init_panopticon_tables(app.config['DATABASE'])
    
    print("Initializing Foresight Tables...")
    init_foresight_tables()
    
    print("Initializing Neural Hash Tables...")
    init_neural_hash_tables()

    # Manually create tasks table
    print("Creating tasks table...")
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER DEFAULT 1,
            title TEXT NOT NULL,
            description TEXT,
            due_date TEXT,
            isCompleted BOOLEAN DEFAULT 0,
            is_quest BOOLEAN DEFAULT 0,
            xp_reward INTEGER DEFAULT 10,
            associated_stat TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    print("✅ Database restored successfully!")
