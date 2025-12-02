from app import create_app
from app.db_models.gamification import init_gamification_tables

app = create_app()

with app.app_context():
    print("🎮 Initializing Gamification Tables...")
    try:
        init_gamification_tables()
        print("✅ Gamification Tables Created & Seeded.")
    except Exception as e:
        print(f"❌ Error: {e}")
