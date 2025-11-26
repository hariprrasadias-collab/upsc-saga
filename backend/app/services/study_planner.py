import datetime
from datetime import timedelta

# Define Study Resources with estimated hours
NCERT_BOOKS = [
    {"subject": "History", "title": "Class 6: Our Pasts I", "hours": 10},
    {"subject": "History", "title": "Class 7: Our Pasts II", "hours": 12},
    {"subject": "History", "title": "Class 8: Our Pasts III", "hours": 15},
    {"subject": "Geography", "title": "Class 6: The Earth Our Habitat", "hours": 8},
    {"subject": "Geography", "title": "Class 7: Our Environment", "hours": 10},
    {"subject": "Polity", "title": "Class 6: Social and Political Life I", "hours": 8},
    {"subject": "Polity", "title": "Class 7: Social and Political Life II", "hours": 10},
    {"subject": "Economy", "title": "Class 9: Economics", "hours": 12},
    {"subject": "Economy", "title": "Class 10: Understanding Economic Development", "hours": 15},
    # Add more as needed...
]

STANDARD_BOOKS = [
    {"subject": "Polity", "title": "Laxmikanth: Indian Polity", "hours": 120},
    {"subject": "History", "title": "Spectrum: Modern History", "hours": 80},
    {"subject": "Geography", "title": "GC Leong: Physical Geography", "hours": 60},
    {"subject": "Economy", "title": "Ramesh Singh: Indian Economy", "hours": 100},
    {"subject": "Environment", "title": "Shankar IAS Environment", "hours": 70},
    {"subject": "Art & Culture", "title": "Nitin Singhania", "hours": 60},
]

def get_slots_for_date(date_obj):
    """Return available slots for a given date."""
    # Weekday: Mon(0) to Fri(4)
    if date_obj.weekday() < 5:
        return [
            {"time": "04:00 - 07:00", "hours": 3, "type": "Morning Grind"},
            {"time": "20:00 - 23:00", "hours": 3, "type": "Night Owl"}
        ]
    # Weekend: Sat(5), Sun(6)
    else:
        return [
            {"time": "06:00 - 10:00", "hours": 4, "type": "Weekend Morning"},
            {"time": "14:00 - 17:00", "hours": 3, "type": "Weekend Afternoon"},
            {"time": "19:00 - 22:00", "hours": 3, "type": "Weekend Night"}
        ]

def generate_study_plan(start_date_str):
    """Generate a 2-year study plan starting from start_date."""
    start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
    end_date = start_date + timedelta(days=730) # 2 Years
    
    plan = []
    current_date = start_date
    
    # Queue of books to study
    # Strategy: NCERTs first, then Standard.
    # We pick 2 subjects at a time.
    
    # Group books by subject
    all_books = NCERT_BOOKS + STANDARD_BOOKS
    subjects = list(set(b['subject'] for b in all_books))
    
    # Organize queue: Subject 1 NCERTs, Subject 2 NCERTs, Subject 1 Standard, Subject 2 Standard...
    # This is complex. Let's simplify:
    # Phase 1: All NCERTs (2 subjects at a time)
    # Phase 2: All Standard (2 subjects at a time)
    
    ncert_queue = sorted(NCERT_BOOKS, key=lambda x: x['subject'])
    standard_queue = sorted(STANDARD_BOOKS, key=lambda x: x['subject'])
    
    # Active slots
    # Slot 1 (Morning) -> Subject A
    # Slot 2 (Night) -> Subject B
    
    # We need a manager to track progress of current books
    active_books = [None, None] # [Slot1_Book, Slot2_Book]
    book_queues = [ncert_queue[:], ncert_queue[::-1]] # Naive split for now, needs better logic
    
    # Better logic:
    # Pool of pending books.
    # When a slot is free, pick a book from a subject NOT currently in the other slot.
    
    pending_books = NCERT_BOOKS + STANDARD_BOOKS
    completed_books = []
    
    # Track progress (hours remaining)
    current_book_progress = [None, None] # {"book": book_obj, "remaining": hours}
    
    while current_date < end_date and (pending_books or any(current_book_progress)):
        slots = get_slots_for_date(current_date)
        daily_plan = {"date": current_date.isoformat(), "day": current_date.strftime("%A"), "slots": []}
        
        for i, slot in enumerate(slots):
            # Determine which "track" this slot belongs to
            # Weekdays: 0=Morning (Track A), 1=Night (Track B)
            # Weekends: 0=Track A, 1=Track B, 2=Revision/Track A
            
            track_idx = 0 if i % 2 == 0 else 1
            
            # If no book active in this track, pick one
            if not current_book_progress[track_idx]:
                if pending_books:
                    # Pick a book that is NOT the same subject as the other track (if possible)
                    other_track = current_book_progress[1 - track_idx]
                    other_subject = other_track['book']['subject'] if other_track else None
                    
                    # Find candidate
                    candidate = next((b for b in pending_books if b['subject'] != other_subject), pending_books[0])
                    pending_books.remove(candidate)
                    
                    current_book_progress[track_idx] = {"book": candidate, "remaining": candidate['hours']}
                else:
                    # No more books
                    daily_plan["slots"].append({**slot, "activity": "Revision / Mock Test"})
                    continue

            # Study active book
            active = current_book_progress[track_idx]
            hours_to_study = min(slot['hours'], active['remaining'])
            
            daily_plan["slots"].append({
                **slot,
                "subject": active['book']['subject'],
                "activity": f"Study {active['book']['title']}",
                "duration": hours_to_study
            })
            
            active['remaining'] -= hours_to_study
            
            # If finished
            if active['remaining'] <= 0:
                completed_books.append(active['book'])
                current_book_progress[track_idx] = None
                
        plan.append(daily_plan)
        current_date += timedelta(days=1)
        
    return plan
