# Python script to initialize the Current Affairs database table
from app import create_app
from app.db_models.current_affairs import init_current_affairs_table

print("Initializing Current Affairs database...")

# Create app and push context
app = create_app()
with app.app_context():
    init_current_affairs_table()
    print("Database initialized successfully!")
    print("You can now use the Ravens tab to save and manage UPSC current affairs.")
