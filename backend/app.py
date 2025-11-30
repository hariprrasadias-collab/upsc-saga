from app import create_app

app = create_app()

# Register Socratic Blueprint (Temporary direct registration if create_app doesn't scan)
# Ideally this should be in create_app, but let's check where create_app is defined first.
# Actually, let's check app/__init__.py first to do it properly.
if __name__ == '__main__':
    app.run(debug=True, port=5000)