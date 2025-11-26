from app.services.study_planner import generate_study_plan
import traceback

def debug():
    try:
        print("Generating plan...")
        plan = generate_study_plan('2025-01-01')
        print(f"Success! Generated {len(plan)} days.")
    except Exception:
        traceback.print_exc()

if __name__ == "__main__":
    debug()
