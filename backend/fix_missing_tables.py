from app import create_app
from app.db_models.automation_storage import init_automation_tables

app = create_app()

with app.app_context():
    init_automation_tables()
    print("Fix applied: Automation tables initialized.")
