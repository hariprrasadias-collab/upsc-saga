from app import create_app
import sys

try:
    app = create_app()
    print("App created successfully")
    for rule in app.url_map.iter_rules():
        if 'shop' in rule.rule:
            print(f"{rule.endpoint}: {rule.rule}")
except Exception as e:
    print(f"Error creating app: {e}")
    sys.exit(1)
