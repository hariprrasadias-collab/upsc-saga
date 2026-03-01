import sys
import os
import sqlite3
import json

# Add current directory to path so we can import app modules
sys.path.append(os.getcwd())

def test_quest_service():
    print("\n🔍 Testing Quest Service...")
    try:
        from app.services.quest_service import quest_service
        quests = quest_service.generate_daily_quests(1)
        if quests and len(quests) > 0:
            print("✅ QuestService module found and operational.")
            print(f"   Generated {len(quests)} quests.")
        else:
            print("⚠️ QuestService returned empty quests.")
    except ImportError as e:
        print(f"❌ FAILED: Could not import QuestService. {e}")
    except Exception as e:
        print(f"❌ FAILED: QuestService error. {e}")

def test_mock_test_service():
    print("\n🔍 Testing Mock Test Service...")
    try:
        from app.services.mock_test_service import MockTestService
        if hasattr(MockTestService, 'create_smart_test'):
            print("✅ MockTestService.create_smart_test method exists.")
        else:
            print("❌ FAILED: MockTestService missing create_smart_test method.")
    except ImportError:
        print("❌ FAILED: Could not import MockTestService.")

def test_database_schema():
    print("\n🔍 Testing Database Schema...")
    # Use the same logic as app.db to find the database
    base_dir = os.path.join(os.getcwd(), 'backend') if os.path.exists(os.path.join(os.getcwd(), 'backend')) else os.getcwd()
    db_path = os.environ.get('DATABASE_PATH', os.path.join(base_dir, 'upsc_saga.db'))

    if not os.path.exists(db_path):
        print(f"⚠️ WARNING: Database not found at {db_path}. Skipping schema check (this is expected in CI/fresh builds).")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check syllabus_topics (renamed from syllabus_tracker)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='syllabus_topics'")
        if cursor.fetchone():
            print("✅ Table 'syllabus_topics' exists.")
        else:
            print("❌ FAILED: Table 'syllabus_topics' MISSING.")

        # Check custom_bosses column
        cursor.execute("PRAGMA table_info(custom_bosses)")
        columns = [row[1] for row in cursor.fetchall()]
        if 'name' in columns:
            print("✅ Table 'custom_bosses' has 'name' column.")
        else:
            print("❌ FAILED: Table 'custom_bosses' missing 'name' column.")
        
        conn.close()
    except Exception as e:
        print(f"❌ Database check failed: {e}")

def test_brain_service_status():
    print("\n🔍 Testing Brain Service Status...")
    try:
        from app.services.brain_service import brain_service
        status = brain_service._get_system_status_summary()
        if status.get('status') == 'ONLINE':
            print("✅ Brain Service reports status: ONLINE")
        else:
            print(f"❌ FAILED: Brain Service status is {status.get('status')}")
    except Exception as e:
        print(f"❌ Brain Service check failed: {e}")

if __name__ == "__main__":
    print(">> Starting System Verification...")
    test_quest_service()
    test_mock_test_service()
    test_database_schema()
    test_brain_service_status()
    print("\n>> Verification Complete.")
