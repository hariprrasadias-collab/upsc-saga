"""
Script to safely add autonomy routes to app/__init__.py
"""

# Read the current file
with open('backend/app/__init__.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Check if autonomy routes are already added
if 'autonomy_routes' in content:
    print("✅ Autonomy routes already registered!")
else:
    # Find the brain_routes registration
    if 'from app.routes.brain_routes import brain_bp' in content:
        # Add after brain_routes
        content = content.replace(
            "from app.routes.brain_routes import brain_bp\n    app.register_blueprint(brain_bp, url_prefix='/api/brain')",
            "from app.routes.brain_routes import brain_bp\n    app.register_blueprint(brain_bp, url_prefix='/api/brain')\n    \n    from app.routes.autonomy_routes import autonomy_bp\n    app.register_blueprint(autonomy_bp, url_prefix='/api/autonomy')"
        )
    else:
        # Add before return app
        content = content.replace(
            "\n    return app",
            "\n    from app.routes.autonomy_routes import autonomy_bp\n    app.register_blueprint(autonomy_bp, url_prefix='/api/autonomy')\n\n    return app"
        )
    
    # Write back
    with open('backend/app/__init__.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Autonomy routes added successfully!")
