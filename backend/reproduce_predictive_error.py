import sqlite3
from app.services.predictive_analytics import (
    calculate_exam_readiness,
    calculate_success_probability,
    calculate_optimal_study_time,
    detect_burnout
)

def test_predictive():
    print("Testing calculate_exam_readiness...")
    try:
        res = calculate_exam_readiness()
        print("Result:", res)
    except Exception as e:
        print("ERROR in calculate_exam_readiness:", e)
        import traceback
        traceback.print_exc()

    print("\nTesting calculate_success_probability...")
    try:
        res = calculate_success_probability()
        print("Result:", res)
    except Exception as e:
        print("ERROR in calculate_success_probability:", e)
        import traceback
        traceback.print_exc()

    print("\nTesting calculate_optimal_study_time...")
    try:
        res = calculate_optimal_study_time()
        print("Result:", res)
    except Exception as e:
        print("ERROR in calculate_optimal_study_time:", e)
        import traceback
        traceback.print_exc()

    print("\nTesting detect_burnout...")
    try:
        res = detect_burnout()
        print("Result:", res)
    except Exception as e:
        print("ERROR in detect_burnout:", e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_predictive()
