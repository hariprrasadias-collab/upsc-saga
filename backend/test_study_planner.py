import sys
import os
import datetime

# Add backend directory to path so we can import app modules regardless of where we run from
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from app.services.study_planner import get_smart_slots, get_slot_config

def test_get_smart_slots():
    print("\n🔍 Testing get_smart_slots in study_planner...")

    config = get_slot_config()

    # Test all weekdays (Mon-Fri)
    # 2023-10-09 is Monday, 2023-10-13 is Friday
    for day in range(9, 14):
        weekday_date = datetime.date(2023, 10, day)
        weekday_slots = get_smart_slots(weekday_date)
        expected_weekday_slots = config["weekday"]["morning"] + config["weekday"]["night"]
        assert weekday_slots == expected_weekday_slots, f"Failed on weekday date {weekday_date}. Expected {expected_weekday_slots}, got {weekday_slots}"
    print("✅ All Weekday (Mon-Fri) slots returned correctly.")

    # Test Saturday (2023-10-14)
    saturday_date = datetime.date(2023, 10, 14)
    saturday_slots = get_smart_slots(saturday_date)
    expected_saturday_slots = config["saturday"]["morning"] + config["saturday"]["evening"]

    assert saturday_slots == expected_saturday_slots, f"Failed on Saturday date {saturday_date}. Expected {expected_saturday_slots}, got {saturday_slots}"
    print("✅ Saturday slots returned correctly.")

    # Test Sunday (2023-10-15)
    sunday_date = datetime.date(2023, 10, 15)
    sunday_slots = get_smart_slots(sunday_date)
    expected_sunday_slots = config["sunday"]["mock"] + config["sunday"]["analysis"] + config["sunday"]["flashcards"] + config["sunday"]["buffer"]

    assert sunday_slots == expected_sunday_slots, f"Failed on Sunday date {sunday_date}. Expected {expected_sunday_slots}, got {sunday_slots}"
    print("✅ Sunday slots returned correctly.")

    print("✅ All get_smart_slots tests passed.")

if __name__ == "__main__":
    try:
        test_get_smart_slots()
    except AssertionError as e:
        print(f"❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ TEST ERROR: {e}")
        sys.exit(1)
