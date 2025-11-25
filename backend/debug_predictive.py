import sys
import os

# Add backend directory to path
sys.path.append(os.path.abspath('d:/upsc-second-brain/backend'))

from app.services.predictive_analytics import (
    calculate_exam_readiness,
    calculate_success_probability,
    calculate_optimal_study_time,
    detect_burnout
)

print("Testing calculate_exam_readiness...")
try:
    print(calculate_exam_readiness())
except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()

print("\nTesting calculate_success_probability...")
try:
    print(calculate_success_probability())
except Exception as e:
    print(f"FAILED: {e}")
    traceback.print_exc()

print("\nTesting calculate_optimal_study_time...")
try:
    print(calculate_optimal_study_time())
except Exception as e:
    print(f"FAILED: {e}")
    traceback.print_exc()

print("\nTesting detect_burnout...")
try:
    print(detect_burnout())
except Exception as e:
    print(f"FAILED: {e}")
    traceback.print_exc()
