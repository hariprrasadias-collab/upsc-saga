import datetime
from datetime import timedelta
import heapq
from app.db_models.study_plan import create_new_plan, add_tasks_bulk, get_active_plan, get_tasks_for_date, get_pending_tasks_before_date, reschedule_task, init_study_plan_tables, get_future_buffer_slots

# Initialize tables on module load (or call explicitly in app factory)
# init_study_plan_tables() - MOVED TO app/__init__.py to avoid AppContext Error

# Define Study Resources with chapters
NCERT_BOOKS = [
    {
        "subject": "History", 
        "title": "Class 6: Our Pasts I", 
        "chapters": [
            "Ch 1: What, Where, How and When?", "Ch 2: From Hunting–Gathering to Growing Food",
            "Ch 3: In the Earliest Cities", "Ch 4: What Books and Burials Tell Us",
            "Ch 5: Kingdoms, Kings and an Early Republic", "Ch 6: New Questions and Ideas",
            "Ch 7: Ashoka, The Emperor Who Gave Up War", "Ch 8: Vital Villages, Thriving Towns",
            "Ch 9: Traders, Kings and Pilgrims", "Ch 10: New Empires and Kingdoms",
            "Ch 11: Buildings, Paintings and Books"
        ]
    },
    {
        "subject": "History", 
        "title": "Class 7: Our Pasts II", 
        "chapters": [
            "Ch 1: Tracing Changes Through A Thousand Years", "Ch 2: New Kings And Kingdoms",
            "Ch 3: The Delhi Sultans", "Ch 4: The Mughal Empire",
            "Ch 5: Rulers And Buildings", "Ch 6: Towns, Traders And Craftspersons",
            "Ch 7: Tribes, Nomads And Settled Communities", "Ch 8: Devotional Paths To The Divine",
            "Ch 9: The Making Of Regional Cultures", "Ch 10: Eighteenth-Century Political Formations"
        ]
    },
    {
        "subject": "Geography", 
        "title": "Class 6: The Earth Our Habitat", 
        "chapters": [
            "Ch 1: The Earth in the Solar System", "Ch 2: Globe : Latitudes and Longitudes",
            "Ch 3: Motions of the Earth", "Ch 4: Maps",
            "Ch 5: Major Domains of the Earth", "Ch 6: Major Landforms of the Earth",
            "Ch 7: Our Country - India", "Ch 8: India : Climate, Vegetation and Wildlife"
        ]
    },
    {
        "subject": "Polity", 
        "title": "Class 6: Social and Political Life I", 
        "chapters": [
            "Ch 1: Understanding Diversity", "Ch 2: Diversity and Discrimination",
            "Ch 3: What is Government?", "Ch 4: Key Elements of a Democratic Government",
            "Ch 5: Panchayati Raj", "Ch 6: Rural Administration",
            "Ch 7: Urban Administration", "Ch 8: Rural Livelihoods",
            "Ch 9: Urban Livelihoods"
        ]
    },
    # Add more books with chapters as needed...
     {
        "subject": "Economy", 
        "title": "Class 9: Economics", 
        "chapters": [
            "Ch 1: The Story of Village Palampur", "Ch 2: People as Resource",
            "Ch 3: Poverty as a Challenge", "Ch 4: Food Security in India"
        ]
    }
]

STANDARD_BOOKS = [
    {
        "subject": "Polity", 
        "title": "Laxmikanth: Indian Polity", 
        "chapters": [
            "Ch 1: Historical Background", "Ch 2: Making of the Constitution",
            "Ch 3: Salient Features of the Constitution", "Ch 4: Preamble of the Constitution",
            "Ch 5: Union and its Territory", "Ch 6: Citizenship",
            "Ch 7: Fundamental Rights (Part 1)", "Ch 7: Fundamental Rights (Part 2)",
            "Ch 8: Directive Principles of State Policy", "Ch 9: Fundamental Duties",
            "Ch 10: Amendment of the Constitution", "Ch 11: Basic Structure of the Constitution"
        ]
    },
    {
        "subject": "History", 
        "title": "Spectrum: Modern History", 
        "chapters": [
            "Unit 1: Sources and Approaches", "Unit 2: Advent of Europeans",
            "Unit 3: Rising Resentment against Company Rule", "Unit 4: Reform Movements",
            "Unit 5: The Struggle Begins", "Unit 6: National Movement 1905-1918",
            "Unit 7: Era of Mass Nationalism 1919-1939", "Unit 8: Towards Freedom and Partition"
        ]
    }
]

def get_smart_slots(date_obj):
    """
    Return granular slots with STRICT TIMING (50m Study + 10m Break).
    Weekday: 4-7 AM (3 slots), 8-11 PM (3 slots)
    Saturday: 4h Revision + 3h New
    Sunday: 3h Mock + 2h Analysis + 1h Flashcards + Buffer
    """
    slots = []
    date_str = date_obj.isoformat()
    weekday = date_obj.weekday() # Mon=0, Sun=6
    
    # Weekday: Mon(0) to Fri(4)
    if weekday < 5:
        # Morning: 4-7 AM
        slots.extend([
            {"start": "04:00", "end": "04:50", "type": "study"}, # Break 04:50-05:00
            {"start": "05:00", "end": "05:50", "type": "study"}, # Break 05:50-06:00
            {"start": "06:00", "end": "06:50", "type": "study"}, # Break 06:50-07:00
        ])
        # Night: 8-11 PM
        slots.extend([
            {"start": "20:00", "end": "20:50", "type": "study"}, # Break 20:50-21:00
            {"start": "21:00", "end": "21:50", "type": "study"}, # Break 21:50-22:00
            {"start": "22:00", "end": "22:50", "type": "study"}, # Break 22:50-23:00
        ])
        
    # Saturday: Revision + New
    elif weekday == 5:
        # Morning: Revision (4h)
        slots.extend([
            {"start": "06:00", "end": "06:50", "type": "revision"},
            {"start": "07:00", "end": "07:50", "type": "revision"},
            {"start": "08:00", "end": "08:50", "type": "revision"},
            {"start": "09:00", "end": "09:50", "type": "revision"},
        ])
        # Evening: New Chapters (3h)
        slots.extend([
            {"start": "18:00", "end": "18:50", "type": "study"},
            {"start": "19:00", "end": "19:50", "type": "study"},
            {"start": "20:00", "end": "20:50", "type": "study"},
        ])

    # Sunday: Mock + Analysis + Flashcards + Buffer
    else:
        # Morning: Mock Test (3h continuous)
        slots.extend([
            {"start": "09:00", "end": "12:00", "type": "mock"},
        ])
        # Afternoon: Analysis (2h)
        slots.extend([
            {"start": "14:00", "end": "14:50", "type": "analysis"},
            {"start": "15:00", "end": "15:50", "type": "analysis"},
        ])
        # Evening: Flashcards (1h)
        slots.extend([
            {"start": "18:00", "end": "18:50", "type": "flashcards"},
        ])
        # Buffer Slot (Catch-up)
        slots.extend([
            {"start": "20:00", "end": "21:00", "type": "buffer"},
        ])
        
    return slots

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
    all_books_queue = NCERT_BOOKS + STANDARD_BOOKS
    
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
        
        # 1. Fill slots with SRS Reviews due today
        todays_reviews = [item for item in srs_queue if item['date'] <= date_iso]
        srs_queue = [item for item in srs_queue if item['date'] > date_iso]
        
        # Track which slots are used
        used_slots = [False] * len(slots)
        
        # Assign Reviews to Study/Revision/Buffer slots ONLY
        review_idx = 0
        for i, slot in enumerate(slots):
            if review_idx >= len(todays_reviews):
                break
            
            if slot['type'] in ['study', 'revision', 'buffer']:
                review_item = todays_reviews[review_idx]
                task = (
                    plan_id, date_iso, slot['start'], slot['end'], 
                    "SRS Review", 
                    f"Review: {review_item['topic']} ({review_item['type']})", 
                    review_item['link'], 
                    'pending'
                )
                tasks_buffer.append(task)
                used_slots[i] = True
                review_idx += 1
                
        # Overflow reviews to next day
        for i in range(review_idx, len(todays_reviews)):
            remaining = todays_reviews[i]
            remaining['date'] = (current_date + timedelta(days=1)).isoformat()
            srs_queue.append(remaining)
            
        # 2. Fill remaining slots
        for i, slot in enumerate(slots):
            if used_slots[i]:
                continue
                
            slot_type = slot.get('type', 'study')
            
            # --- SUNDAY MOCK TEST LOGIC ---
            if slot_type == 'mock':
                # Dynamic Mock Topic
                if completed_chapters_log:
                    recent_chapters = completed_chapters_log[-10:]
                    mock_topic = f"Mock Test: {len(recent_chapters)} Recent Chapters"
                else:
                    mock_topic = "Mock Test: General / Baseline"
                    
                task = (plan_id, date_iso, slot['start'], slot['end'], "Mock Test", mock_topic, "", 'pending')
                tasks_buffer.append(task)
                
            elif slot_type == 'analysis':
                task = (plan_id, date_iso, slot['start'], slot['end'], "Analysis", "Analyze Mock Performance & Weak Areas", "", 'pending')
                tasks_buffer.append(task)
                
            elif slot_type == 'flashcards':
                # Sunday Evening Flashcards (Always schedule if any chapters done)
                if completed_chapters_log:
                    subjects = list(set([c.split(' - ')[0] for c in completed_chapters_log[-20:]])) # Last 20 chaps context
                    subject_str = ", ".join(subjects[:3]) # Limit to 3 subjects
                    task = (plan_id, date_iso, slot['start'], slot['end'], "Flashcards", f"Weekly Recall: {subject_str}...", "", 'pending')
                else:
                    task = (plan_id, date_iso, slot['start'], slot['end'], "Flashcards", "Setup Flashcards / Review Basics", "", 'pending')
                tasks_buffer.append(task)
                
            elif slot_type == 'buffer':
                task = (plan_id, date_iso, slot['start'], slot['end'], "Buffer", "Catch-up / Free Time", "", 'pending')
                tasks_buffer.append(task)
                
            elif slot_type in ['study', 'revision']:
                # --- NEW STUDY LOGIC ---
                
                # Check for IMMEDIATE Flashcard Trigger (Priority over new study)
                if chapters_since_flashcard >= 10:
                    subjects = list(set([c.split(' - ')[0] for c in completed_chapters_log[-10:]]))
                    subject_str = ", ".join(subjects)
                    task = (plan_id, date_iso, slot['start'], slot['end'], "Flashcards", f"⚡ Triggered Recall: 10 Chaps ({subject_str})", "", 'pending')
                    tasks_buffer.append(task)
                    chapters_since_flashcard = 0
                    continue 
                
                if current_book_idx < len(all_books_queue):
                    book = all_books_queue[current_book_idx]
                    if current_chapter_idx < len(book['chapters']):
                        chapter_name = book['chapters'][current_chapter_idx]
                        topic_full = f"{book['title']} - {chapter_name}"
                        link = f"https://google.com/search?q={book['title'].replace(' ', '+')}+{chapter_name.replace(' ', '+')}+upsc+pdf"
                        
                        task = (
                            plan_id, date_iso, slot['start'], slot['end'], 
                            book['subject'], topic_full, link, 'pending'
                        )
                        tasks_buffer.append(task)
                        
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
                        i -= 1 
                else:
                    task = (plan_id, date_iso, slot['start'], slot['end'], "Bonus", "Advanced Revision / Mains Prep", "", 'pending')
                    tasks_buffer.append(task)

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
    
    # 2. Map pending tasks to buffer slots
    from app.db_models.study_plan import delete_task
    
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
