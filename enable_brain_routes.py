"""
Script to safely uncomment brain routes in app/__init__.py
"""

# Read the current file
with open('backend/app/__init__.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Uncomment brain routes
if '# from app.routes.brain_routes import brain_bp' in content:
    content = content.replace(
        '# from app.routes.brain_routes import brain_bp',
        'from app.routes.brain_routes import brain_bp'
    )
    content = content.replace(
        "# app.register_blueprint(brain_bp, url_prefix='/api/brain')",
        "app.register_blueprint(brain_bp, url_prefix='/api/brain')"
    )
    
    # Write back
    with open('backend/app/__init__.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Brain routes uncommented successfully!")
else:
    print("ℹ️  Brain routes already uncommented or not found in expected format.")
