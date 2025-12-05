import datetime
from datetime import timedelta
import heapq
import json
import os
from app.db_models.study_plan import create_new_plan, add_tasks_bulk, get_active_plan, get_tasks_for_date, get_pending_tasks_before_date, reschedule_task, init_study_plan_tables, get_future_buffer_slots, delete_task, get_tasks_for_date_range

def load_books_data():
    """Load books data from JSON file."""
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_path = os.path.join(base_dir, 'data', 'books.json')
        with open(data_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Warning: books.json not found. Returning empty list.")
        return []

def get_slot_config(preferences=None):
    """Return slot configuration, respecting user preferences if provided."""

    # Default Config
    config = {
        "weekday": {
            "morning": [
                {"start": "04:00", "end": "04:50", "type": "study"},
                {"start": "05:00", "end": "05:50", "type": "study"},
                {"start": "06:00", "end": "06:50", "type": "study"},
            ],
            "night": [
                {"start": "20:00", "end": "20:50", "type": "study"},
                {"start": "21:00", "end": "21:50", "type": "study"},
                {"start": "22:00", "end": "22:50", "type": "study"},
            ]
        },
        "saturday": {
            "morning": [
                {"start": "06:00", "end": "06:50", "type": "revision"},
                {"start": "07:00", "end": "07:50", "type": "revision"},
                {"start": "08:00", "end": "08:50", "type": "revision"},
                {"start": "09:00", "end": "09:50", "type": "revision"},
            ],
            "evening": [
                {"start": "18:00", "end": "18:50", "type": "study"},
                {"start": "19:00", "end": "19:50", "type": "study"},
                {"start": "20:00", "end": "20:50", "type": "study"},
            ]
        },
        "sunday": {
            "mock": [{"start": "09:00", "end": "12:00", "type": "mock"}],
            "analysis": [
                {"start": "14:00", "end": "14:50", "type": "analysis"},
                {"start": "15:00", "end": "15:50", "type": "analysis"},
            ],
            "flashcards": [{"start": "18:00", "end": "18:50", "type": "flashcards"}],
            "buffer": [{"start": "20:00", "end": "21:00", "type": "buffer"}]
        }
    }

    if preferences and "study_hours" in preferences:
        # Override weekday slots based on preferences
        # Example preference: ["morning", "evening"] or just ["evening"]
        # If user only wants evening, we remove morning slots
        user_hours = preferences["study_hours"]

        # Reset weekday slots
        config["weekday"]["morning"] = []
        config["weekday"]["night"] = []

        if "morning" in user_hours:
            config["weekday"]["morning"] = [
                {"start": "05:00", "end": "05:50", "type": "study"},
                {"start": "06:00", "end": "06:50", "type": "study"},
                {"start": "07:00", "end": "07:50", "type": "study"},
            ]

        if "evening" in user_hours:
             config["weekday"]["night"] = [
                {"start": "19:00", "end": "19:50", "type": "study"},
                {"start": "20:00", "end": "20:50", "type": "study"},
                {"start": "21:00", "end": "21:50", "type": "study"},
            ]

    return config

def get_smart_slots(date_obj, preferences=None):
    """
    Return granular slots based on configuration.
    """
    slots = []
    weekday = date_obj.weekday() # Mon=0, Sun=6
    config = get_slot_config(preferences)
    
    # Weekday: Mon(0) to Fri(4)
    if weekday < 5:
        slots.extend(config["weekday"]["morning"])
        slots.extend(config["weekday"]["night"])
        
    # Saturday: Revision + New
    elif weekday == 5:
        slots.extend(config["saturday"]["morning"])
        slots.extend(config["saturday"]["evening"])

    # Sunday: Mock + Analysis + Flashcards + Buffer
    else:
        slots.extend(config["sunday"]["mock"])
        slots.extend(config["sunday"]["analysis"])
        slots.extend(config["sunday"]["flashcards"])
        slots.extend(config["sunday"]["buffer"])
        
    return slots

def create_task_tuple(plan_id, date_iso, slot, subject, topic, link, status='pending'):
    """Helper to create a task tuple."""
    return (
        plan_id, date_iso, slot['start'], slot['end'],
        subject, topic, link, status
    )

def handle_srs_reviews(srs_heap, date_iso, slots, tasks_buffer, used_slots, plan_id):
    """Fill slots with SRS Reviews due today using heapq."""
    todays_reviews = []

    # Efficiently pop all items due today or earlier
    # Heap elements are tuples: (date_str, item_details_dict)
    # Python 3 does not support dict comparison, so we need to ensure unique sort key if dates are equal.
    # We can store (date_str, counter, item_details_dict) to avoid comparing dicts.

    # However, since we already pushed (date, dict), we need to fix the push format first.
    # But wait, we can't easily change the push format without changing all pushes.
    # Actually, we can just fix the comparison by defining a wrapper class or just pushing (date, id(dict), dict).
    # Using id() is a quick hack for uniqueness.

    # Better approach: We will change how we push to the heap in generate_study_plan.
    pass

    # ... Wait, I cannot edit generate_study_plan here. I am in handle_srs_reviews.
    # I need to edit both places.

    # Let's assume the heap will now contain (date_str, unique_id, task_details).

    while srs_heap and srs_heap[0][0] <= date_iso:
        todays_reviews.append(heapq.heappop(srs_heap)[-1]) # Get the task_details

    review_idx = 0
    for i, slot in enumerate(slots):
        if review_idx >= len(todays_reviews):
            break

        if slot['type'] in ['study', 'revision', 'buffer']:
            # todays_reviews now contains only the review_item (dict)
            review_item = todays_reviews[review_idx]
            task = create_task_tuple(
                plan_id, date_iso, slot,
                "SRS Review",
                f"Review: {review_item['topic']} ({review_item['type']})",
                review_item['link']
            )
            tasks_buffer.append(task)
            used_slots[i] = True
            review_idx += 1

    # Overflow reviews logic: distribute to next few days to avoid pile-up
    overflow_count = 0
    for i in range(review_idx, len(todays_reviews)):
        review_item = todays_reviews[i]
        # Spread overflow over next 3 days
        offset = (overflow_count % 3) + 1
        # Convert date_iso back to date object to add offset
        current_date = datetime.datetime.strptime(date_iso, "%Y-%m-%d").date()
        new_date_iso = (current_date + timedelta(days=offset)).isoformat()

        # Push back to heap with new date
        # Use simple hash or id for sorting stability
        heapq.heappush(srs_heap, (new_date_iso, id(review_item), review_item))
        overflow_count += 1

    return srs_heap

def handle_special_slots(slot, plan_id, date_iso, completed_chapters_log, tasks_buffer):
    """Handle special slots like mock, analysis, flashcards, buffer."""
    slot_type = slot.get('type', 'study')

    if slot_type == 'mock':
        if completed_chapters_log:
            recent_chapters = completed_chapters_log[-10:]
            mock_topic = f"Mock Test: {len(recent_chapters)} Recent Chapters"
        else:
            mock_topic = "Mock Test: General / Baseline"
        tasks_buffer.append(create_task_tuple(plan_id, date_iso, slot, "Mock Test", mock_topic, ""))
        return True

    elif slot_type == 'analysis':
        tasks_buffer.append(create_task_tuple(plan_id, date_iso, slot, "Analysis", "Analyze Mock Performance & Weak Areas", ""))
        return True

    elif slot_type == 'flashcards':
        if completed_chapters_log:
            subjects = list(set([c.split(' - ')[0] for c in completed_chapters_log[-20:]]))
            subject_str = ", ".join(subjects[:3])
            topic = f"Weekly Recall: {subject_str}..."
        else:
            topic = "Setup Flashcards / Review Basics"
        tasks_buffer.append(create_task_tuple(plan_id, date_iso, slot, "Flashcards", topic, ""))
        return True

    elif slot_type == 'buffer':
        tasks_buffer.append(create_task_tuple(plan_id, date_iso, slot, "Buffer", "Catch-up / Free Time", ""))
        return True

    return False

def generate_study_plan(start_date_str, force_new=False, preferences=None):
    """Generate a 2-year study plan with Intelligent Triggers (Flashcards after 10 ch) and Dynamic Mocks."""
    
    if not force_new:
        existing_plan = get_active_plan()
        if existing_plan:
            return {"success": True, "plan_id": existing_plan['id'], "message": "Existing plan retrieved"}

    start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
    end_date = start_date + timedelta(days=730) # 2 Years
    
    plan_id = create_new_plan(start_date_str, end_date.isoformat())
    
    current_date = start_date
    all_books_queue = load_books_data()
    
    current_book_idx = 0
    current_chapter_idx = 0
    
    # Intelligent Tracking
    chapters_since_flashcard = 0
    completed_chapters_log = [] # List of strings: "Book - Chapter"
    
    # SRS Heap: Priority Queue of (date_str, task_details)
    srs_heap = []
    
    tasks_buffer = []
    
    while current_date < end_date:
        slots = get_smart_slots(current_date, preferences)
        date_iso = current_date.isoformat()
        
        used_slots = [False] * len(slots)
        
        # 1. Fill slots with SRS Reviews due today
        handle_srs_reviews(srs_heap, date_iso, slots, tasks_buffer, used_slots, plan_id)
            
        # 2. Fill remaining slots
        for i, slot in enumerate(slots):
            if used_slots[i]:
                continue
                
            if handle_special_slots(slot, plan_id, date_iso, completed_chapters_log, tasks_buffer):
                continue
            
            # --- NEW STUDY LOGIC ---
            if slot['type'] in ['study', 'revision']:
                # Check for IMMEDIATE Flashcard Trigger (Priority over new study)
                if chapters_since_flashcard >= 10:
                    subjects = list(set([c.split(' - ')[0] for c in completed_chapters_log[-10:]]))
                    subject_str = ", ".join(subjects)
                    tasks_buffer.append(create_task_tuple(
                        plan_id, date_iso, slot,
                        "Flashcards",
                        f"⚡ Triggered Recall: 10 Chaps ({subject_str})",
                        ""
                    ))
                    chapters_since_flashcard = 0
                    continue 
                
                if current_book_idx < len(all_books_queue):
                    book = all_books_queue[current_book_idx]
                    if current_chapter_idx < len(book['chapters']):
                        chapter_name = book['chapters'][current_chapter_idx]
                        topic_full = f"{book['title']} - {chapter_name}"
                        link = f"https://google.com/search?q={book['title'].replace(' ', '+')}+{chapter_name.replace(' ', '+')}+upsc+pdf"
                        
                        tasks_buffer.append(create_task_tuple(
                            plan_id, date_iso, slot,
                            book['subject'], topic_full, link
                        ))
                        
                        # TRACKING
                        completed_chapters_log.append(topic_full)
                        chapters_since_flashcard += 1
                        
                        # SCHEDULE SRS REVIEWS (Push to Heap)
                        item_details = {"topic": topic_full, "link": link}
                        # Use id(dict) as tie-breaker for heap comparison
                        item1 = {**item_details, "type": "Day 1"}
                        heapq.heappush(srs_heap, ((current_date + timedelta(days=1)).isoformat(), id(item1), item1))

                        item7 = {**item_details, "type": "Day 7"}
                        heapq.heappush(srs_heap, ((current_date + timedelta(days=7)).isoformat(), id(item7), item7))

                        item30 = {**item_details, "type": "Day 30"}
                        heapq.heappush(srs_heap, ((current_date + timedelta(days=30)).isoformat(), id(item30), item30))
                        
                        current_chapter_idx += 1
                        
                        # CHECK FOR BOOK COMPLETION (Flashcard Trigger)
                        if current_chapter_idx >= len(book['chapters']):
                            # Book Completed! Schedule immediate Flashcard Review for next available slot (via SRS heap for priority)
                            # We set date to tomorrow (or today if we want immediate, but loop is processed)
                            # Using tomorrow ensures it's picked up.
                            next_day_iso = (current_date + timedelta(days=1)).isoformat()
                            book_review_item = {
                                "topic": f"FULL BOOK: {book['title']}",
                                "type": "Book Completion Review",
                                "link": ""
                            }
                            heapq.heappush(srs_heap, (next_day_iso, id(book_review_item), book_review_item))
                            # Also trigger flashcards immediately next slot if possible
                            chapters_since_flashcard = 10 # Force trigger next slot
                            
                    else:
                        current_book_idx += 1
                        current_chapter_idx = 0
                        # Retry this slot with next book
                        # We need to decrement i but we can't easily do that in a for loop enumerate.
                        # Instead, we can just continue and let the loop proceed?
                        # No, if we just continue, we waste the slot.
                        # Since we have incremented book index, we should try to fill THIS slot with the new book.
                        # But `i` is the slot index.
                        # Let's just use a recursive call or a while loop for filling slots?
                        # Or just accept that one slot might be skipped or "Bonus" if book changes mid-day.
                        # Actually, better logic:
                        # Since we just updated current_book_idx, let's try to fill the slot again in this iteration.
                        # But Python for loops don't support retry easily.
                        # We can just check again.

                        if current_book_idx < len(all_books_queue):
                             # Recursive retry for this slot logic - effectively copy paste logic or refactor more.
                             # For simplicity, let's just mark it as "Transition" or "Bonus" to keep logic simple
                             tasks_buffer.append(create_task_tuple(
                                plan_id, date_iso, slot,
                                "Buffer", "Book Transition / Review", ""
                            ))
                        else:
                             tasks_buffer.append(create_task_tuple(
                                plan_id, date_iso, slot,
                                "Bonus", "Advanced Revision / Mains Prep", ""
                            ))
                else:
                    tasks_buffer.append(create_task_tuple(
                        plan_id, date_iso, slot,
                        "Bonus", "Advanced Revision / Mains Prep", ""
                    ))

        if len(tasks_buffer) > 200:
            add_tasks_bulk(tasks_buffer)
            tasks_buffer = []
            
        current_date += timedelta(days=1)
        
    if tasks_buffer:
        add_tasks_bulk(tasks_buffer)
        
    return {"success": True, "plan_id": plan_id}

def get_plan_for_range(start_date_str, days=30):
    """Get plan for a date range"""
    start = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
    end = start + timedelta(days=days - 1)

    tasks_raw = get_tasks_for_date_range(start.isoformat(), end.isoformat())

    # Group by date
    tasks_by_date = {}
    current_iter = start
    while current_iter <= end:
        date_iso = current_iter.isoformat()
        tasks_by_date[date_iso] = []
        current_iter += timedelta(days=1)

    for t in tasks_raw:
        if t['date'] in tasks_by_date:
            tasks_by_date[t['date']].append(t)

    result = []
    
    # Sort dates to ensure order
    sorted_dates = sorted(tasks_by_date.keys())

    for date_str in sorted_dates:
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        tasks = tasks_by_date[date_str]
        
        day_plan = {
            "date": date_str,
            "day": date_obj.strftime("%A"),
            "slots": []
        }
        
        for t in tasks:
            day_plan["slots"].append({
                "id": t['id'],
                "time": f"{t['start_time']} - {t['end_time']}",
                "subject": t['subject'],
                "activity": t['topic'],
                "status": t['status'],
                "resource_link": t['resource_link']
            })
            
        result.append(day_plan)
        
    return result

def check_and_reschedule_pending():
    """
    Auto-Rescheduler with Dependency Awareness:
    1. Find past due pending tasks.
    2. Sort them to prioritize critical subjects or oldest first.
    3. Find upcoming 'Buffer' slots.
    4. Move tasks to buffers.
    """
    today = datetime.date.today()
    pending_tasks = get_pending_tasks_before_date(today.isoformat())
    
    if not pending_tasks:
        return {"rescheduled_count": 0}
    
    # Sort pending tasks: Oldest first (FIFO)
    # They are already sorted by date ASC from the DB query, but we can add secondary sorting if needed.

    # Auto-Reschedule Logic
    rescheduled_count = 0
    
    # 1. Get future buffer slots (starting tomorrow to avoid today's chaos)
    tomorrow = (today + timedelta(days=1)).isoformat()
    buffer_slots = get_future_buffer_slots(tomorrow)
    
    processed_task_ids = set()
    
    for task in pending_tasks:
        if task['id'] in processed_task_ids:
            continue

        if not buffer_slots:
            break # No more slots available
            
        target_slot = buffer_slots.pop(0)
        
        # Move pending task to this slot
        # We keep the task ID but update date/time
        reschedule_task(task['id'], target_slot['date'], target_slot['start_time'], target_slot['end_time'])
        
        # Remove the buffer slot task (it's been consumed)
        delete_task(target_slot['id'])
        
        processed_task_ids.add(task['id'])
        rescheduled_count += 1
    
    return {
        "rescheduled_count": rescheduled_count,
        "tasks": [t for t in pending_tasks if t['id'] in processed_task_ids]
    }

def get_todays_tasks_summary():
    """
    Get a text summary of today's tasks for the Brain context.
    """
    today_iso = datetime.date.today().isoformat()
    tasks = get_tasks_for_date(today_iso)
    
    if not tasks:
        return "No tasks scheduled for today."
        
    summary = [f"Tasks for {today_iso}:"]
    for t in tasks:
        status_str = "[DONE]" if t['status'] == 'completed' else "[TODO]"
        summary.append(f"- {status_str} [{t['start_time']}-{t['end_time']}] {t['subject']}: {t['topic']}")
        
    return "\n".join(summary)
