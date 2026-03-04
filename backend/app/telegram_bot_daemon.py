import threading
import time
from app.services.telegram_service import telegram_service
from app.services.study_planner import check_telegram_tasks

def telegram_tasks_loop(app):
    """Periodically checks tasks every minute."""
    if not telegram_service.is_configured():
        print("Telegram bot not configured. Daemon tasks disabled.")
        return

    while True:
        try:
            check_telegram_tasks(app)
        except Exception as e:
            print(f"Telegram Tasks Daemon Error: {e}")
        time.sleep(60)

def start_telegram_daemon(app):
    if telegram_service.is_configured():
        polling_thread = threading.Thread(target=telegram_service.poll_updates, args=(app,), daemon=True)
        polling_thread.start()

        tasks_thread = threading.Thread(target=telegram_tasks_loop, args=(app,), daemon=True)
        tasks_thread.start()
        print("Telegram Bot Daemon started.")
