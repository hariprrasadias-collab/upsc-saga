import os
import requests
import json
import threading
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

class TelegramService:
    def __init__(self):
        self.bot_token = TELEGRAM_BOT_TOKEN
        self.chat_id = TELEGRAM_CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}" if self.bot_token else None
        self.offset = None

    def is_configured(self):
        return bool(self.bot_token and self.chat_id)

    def send_message(self, text, reply_markup=None):
        if not self.is_configured():
            return False

        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        if reply_markup:
            payload["reply_markup"] = json.dumps(reply_markup)

        try:
            response = requests.post(url, json=payload, timeout=10)
            return response.json().get("ok", False)
        except Exception as e:
            print(f"Telegram Send Error: {e}")
            return False

    def edit_message(self, message_id, text):
        if not self.is_configured():
            return False

        url = f"{self.base_url}/editMessageText"
        payload = {
            "chat_id": self.chat_id,
            "message_id": message_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        try:
            requests.post(url, json=payload, timeout=10)
        except Exception as e:
            print(f"Telegram Edit Error: {e}")

    def send_task_reminder(self, task):
        text = f"⏰ *Task Reminder*\n\nIt's time for: *{task['subject']} - {task['topic']}*\nTime: {task['start_time']} - {task['end_time']}"
        return self.send_message(text)

    def ask_task_completion(self, task):
        text = f"⏳ *Time's Up!*\n\nDid you complete: *{task['subject']} - {task['topic']}*?"
        reply_markup = {
            "inline_keyboard": [
                [
                    {"text": "✅ Yes", "callback_data": f"task_yes_{task['id']}"},
                    {"text": "❌ No", "callback_data": f"task_no_{task['id']}"}
                ]
            ]
        }
        return self.send_message(text, reply_markup)

    def poll_updates(self, app):
        """Long-polling for inline keyboard callbacks."""
        if not self.is_configured():
            print("Telegram polling disabled (credentials missing).")
            return

        print("Telegram polling started...")
        while True:
            try:
                url = f"{self.base_url}/getUpdates"
                params = {"timeout": 30}
                if self.offset:
                    params["offset"] = self.offset

                response = requests.get(url, params=params, timeout=40)
                data = response.json()

                if data.get("ok"):
                    for update in data.get("result", []):
                        self.offset = update["update_id"] + 1

                        if "callback_query" in update:
                            cb = update["callback_query"]
                            cb_data = cb.get("data", "")
                            message_id = cb["message"]["message_id"]

                            # Acknowledge callback
                            requests.post(f"{self.base_url}/answerCallbackQuery", json={"callback_query_id": cb["id"]})

                            if cb_data.startswith("task_yes_"):
                                task_id = int(cb_data.split("_")[-1])
                                self.handle_task_response(app, task_id, True, message_id)
                            elif cb_data.startswith("task_no_"):
                                task_id = int(cb_data.split("_")[-1])
                                self.handle_task_response(app, task_id, False, message_id)
            except Exception as e:
                print(f"Telegram Polling Error: {e}")
                time.sleep(5)

    def handle_task_response(self, app, task_id, is_completed, message_id):
        # We need app context to interact with DB
        with app.app_context():
            from app.db_models.study_plan import get_task_by_id, update_task_status
            from app.services.study_planner import smart_reschedule_task
            from app.services.brain_service import brain_service

            task = get_task_by_id(task_id)
            if not task:
                self.edit_message(message_id, "Task not found.")
                return

            if is_completed:
                update_task_status(task_id, 'Completed')
                brain_service.process_task_completion(task)
                self.edit_message(message_id, f"✅ Task *{task['topic']}* marked as completed! Automations triggered.")
            else:
                success = smart_reschedule_task(task_id)
                if success:
                    self.edit_message(message_id, f"🔄 Task *{task['topic']}* has been smartly rescheduled.")
                else:
                    self.edit_message(message_id, f"❌ Failed to reschedule *{task['topic']}*.")

telegram_service = TelegramService()
