import datetime
from datetime import timedelta
import heapq
import json
import os
from app.db_models.study_plan import create_new_plan, add_tasks_bulk, get_active_plan, get_tasks_for_date, get_pending_tasks_before_date, reschedule_task, init_study_plan_tables, get_future_buffer_slots, delete_task

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

def get_slot_config():
    """Return slot configuration."""
    return {
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

def get_smart_slots(date_obj):
    """
    Return granular slots based on configuration.
    """
    slots = []
    weekday = date_obj.weekday() # Mon=0, Sun=6
    config = get_slot_config()
    
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

def handle_srs_reviews(srs_queue, date_iso, slots, tasks_buffer, used_slots, plan_id):
    """Fill slots with SRS Reviews due today."""
    todays_reviews = [item for item in srs_queue if item['date'] <= date_iso]
    # Remove processed items from queue, we will re-add overflows later
    remaining_queue = [item for item in srs_queue if item['date'] > date_iso]

    review_idx = 0
    for i, slot in enumerate(slots):
        if review_idx >= len(todays_reviews):
            break

        if slot['type'] in ['study', 'revision', 'buffer']:
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
        remaining = todays_reviews[i]
        # Spread overflow over next 3 days
        offset = (overflow_count % 3) + 1
        # Convert date_iso back to date object to add offset
        current_date = datetime.datetime.strptime(date_iso, "%Y-%m-%d").date()
        remaining['date'] = (current_date + timedelta(days=offset)).isoformat()
        remaining_queue.append(remaining)
        overflow_count += 1

    return remaining_queue

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

def generate_study_plan(start_date_str, force_new=False):
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
    
    # SRS Queue: Priority Queue of (date_str, task_details)
    srs_queue = [] 
    
    tasks_buffer = []
    
    while current_date < end_date:
        slots = get_smart_slots(current_date)
        date_iso = current_date.isoformat()
        
        used_slots = [False] * len(slots)
        
        # 1. Fill slots with SRS Reviews due today
        srs_queue = handle_srs_reviews(srs_queue, date_iso, slots, tasks_buffer, used_slots, plan_id)
            
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
                        
                        # SCHEDULE SRS REVIEWS
                        srs_queue.append({"date": (current_date + timedelta(days=1)).isoformat(), "topic": topic_full, "type": "Day 1", "link": link})
                        srs_queue.append({"date": (current_date + timedelta(days=7)).isoformat(), "topic": topic_full, "type": "Day 7", "link": link})
                        srs_queue.append({"date": (current_date + timedelta(days=30)).isoformat(), "topic": topic_full, "type": "Day 30", "link": link})
                        
                        current_chapter_idx += 1
                        
                        # CHECK FOR BOOK COMPLETION (Flashcard Trigger)
                        if current_chapter_idx >= len(book['chapters']):
                            # Book Completed! Schedule immediate Flashcard Review for next available slot (via SRS queue for priority)
                            srs_queue.insert(0, {
                                "date": (current_date + timedelta(days=1)).isoformat(),
                                "topic": f"FULL BOOK: {book['title']}",
                                "type": "Book Completion Review",
                                "link": ""
                            })
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
    result = []
    
    for i in range(days):
        date = start + timedelta(days=i)
        date_str = date.isoformat()
        tasks = get_tasks_for_date(date_str)
        
        day_plan = {
            "date": date_str,
            "day": date.strftime("%A"),
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
    Auto-Rescheduler:
    1. Find past due pending tasks.
    2. Find upcoming 'Buffer' slots.
    3. Move tasks to buffers.
    """
    today = datetime.date.today()
    pending_tasks = get_pending_tasks_before_date(today.isoformat())
    
    if not pending_tasks:
        return {"rescheduled_count": 0}
    
    # Auto-Reschedule Logic
    rescheduled_count = 0
    
    # 1. Get future buffer slots (starting tomorrow to avoid today's chaos)
    tomorrow = (today + timedelta(days=1)).isoformat()
    buffer_slots = get_future_buffer_slots(tomorrow)
    
    for task in pending_tasks:
        if not buffer_slots:
            break # No more slots available
            
        target_slot = buffer_slots.pop(0)
        
        # Move pending task to this slot
        # We keep the task ID but update date/time
        reschedule_task(task['id'], target_slot['date'], target_slot['start_time'], target_slot['end_time'])
        
        # Remove the buffer slot task (it's been consumed)
        delete_task(target_slot['id'])
        
        rescheduled_count += 1
    
    return {
        "rescheduled_count": rescheduled_count,
        "tasks": pending_tasks[:rescheduled_count] # Return only rescheduled ones
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
