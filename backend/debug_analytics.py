import sqlite3
from datetime import datetime, timedelta
from app.services.analytics_service import calculate_study_hours, get_streak_days
import app.services.analytics_service
print(f"Loaded analytics_service from: {app.services.analytics_service.__file__}")

def debug_analytics():
    try:
        conn = sqlite3.connect('upsc_saga.db')
        conn.row_factory = sqlite3.Row
        user_id = 1
        start_date = (datetime.now() - timedelta(days=30)).isoformat()
        end_date = datetime.now().isoformat()
        
        print("Testing calculate_study_hours...")
        try:
            hours = calculate_study_hours(conn, user_id, start_date, end_date)
            print(f"Study Hours: {hours}")
        except Exception as e:
            print(f"ERROR in calculate_study_hours: {e}")
            import traceback
            traceback.print_exc()

        print("\nTesting get_streak_days...")
        try:
            streak = get_streak_days(conn, user_id)
            print(f"Streak: {streak}")
        except Exception as e:
            print(f"ERROR in get_streak_days: {e}")
            import traceback
            traceback.print_exc()
            
        conn.close()
    except Exception as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    debug_analytics()
