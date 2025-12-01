"""
Safe script to add autonomous brain initialization to app/__init__.py
"""
import re

# Read the current file
with open('backend/app/__init__.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Track if we made changes
changes_made = False

# Step 1: Add autonomous_brain import after study_plan import
for i, line in enumerate(lines):
    if 'from app.db_models.study_plan import init_study_plan_tables' in line:
        # Check if autonomous_brain import already exists
        if not any('autonomous_brain' in l for l in lines):
            # Add the import on the next line
            lines.insert(i + 1, '    from app.db_models.autonomous_brain import init_autonomous_brain_tables\n')
            changes_made = True
            print("✅ Added autonomous_brain import")
        break

# Step 2: Add init_autonomous_brain_tables() call after init_study_plan_tables()
for i, line in enumerate(lines):
    if 'init_study_plan_tables()' in line:
        # Check if init call already exists
        if not any('init_autonomous_brain_tables()' in l for l in lines):
            # Add the call on the next line
            lines.insert(i + 1, '        init_autonomous_brain_tables()\n')
            changes_made = True
            print("✅ Added autonomous_brain initialization call")
        break

# Step 3: Add autonomy routes before 'return app'
for i, line in enumerate(lines):
    if line.strip() == 'return app':
        # Check if autonomy routes already registered
        if not any('autonomy_routes' in l for l in lines):
            # Add autonomy routes registration before return
            lines.insert(i, '\n')
            lines.insert(i + 1, '    from app.routes.autonomy_routes import autonomy_bp\n')
            lines.insert(i + 2, '    app.register_blueprint(autonomy_bp, url_prefix=\'/api/autonomy\')\n')
            lines.insert(i + 3, '\n')
            changes_made = True
            print("✅ Added autonomy routes registration")
        break

if changes_made:
    # Write back the modified file
    with open('backend/app/__init__.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("\n✅ All changes applied successfully!")
    print("📋 Summary:")
    print("   - Added autonomous_brain table initialization")
    print("   - Added autonomy routes registration")
else:
    print("ℹ️  No changes needed - autonomous brain already integrated!")
