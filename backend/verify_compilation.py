from app import create_app
from app.services.compilation_service import CompilationService
import json

app = create_app()

with app.app_context():
    print("--- Verifying Compilation Service ---")
    
    # Get available months
    months = CompilationService.get_available_months()
    print(f"Available months: {len(months)}")
    
    if months:
        print(f"Found {len(months)} months with data:")
        for m in months:
            compilation = CompilationService.get_monthly_compilation(m['year'], m['month'])
            print(f"- {m['label']}: {compilation['total_articles']} articles")
            
    else:
        print("No months found with data.")
