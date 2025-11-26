import datetime
from app import db

class SchedulerService:
    @staticmethod
    def calculate_next_review(rating, last_interval, last_ease_factor):
        """
        Implements SM-2 Algorithm
        rating: 1-5 (1=Again, 2=Hard, 3=Good, 4=Easy, 5=Very Easy)
        """
        if rating < 3:
            return 1, last_ease_factor  # Reset interval if forgotten

        # Calculate new ease factor
        new_ease_factor = last_ease_factor + (0.1 - (5 - rating) * (0.08 + (5 - rating) * 0.02))
        new_ease_factor = max(1.3, new_ease_factor)  # Minimum ease factor

        # Calculate new interval
        if last_interval == 0:
            new_interval = 1
        elif last_interval == 1:
            new_interval = 6
        else:
            new_interval = int(last_interval * new_ease_factor)

        return new_interval, new_ease_factor

    @staticmethod
    def schedule_review(item_type, item_id, rating):
        """
        Updates or creates a revision schedule for an item.
        """
        conn = db.get_db()
        cursor = conn.cursor()

        # Get existing schedule
        cursor.execute('''
            SELECT interval, ease_factor, review_count 
            FROM revision_schedules 
            WHERE item_type = ? AND item_id = ?
        ''', (item_type, item_id))
        
        row = cursor.fetchone()
        
        if row:
            last_interval, last_ease_factor, review_count = row
        else:
            last_interval, last_ease_factor, review_count = 0, 2.5, 0

        # Calculate next parameters
        new_interval, new_ease_factor = SchedulerService.calculate_next_review(rating, last_interval, last_ease_factor)
        
        next_review_date = datetime.datetime.now() + datetime.timedelta(days=new_interval)
        
        if row:
            cursor.execute('''
                UPDATE revision_schedules 
                SET last_reviewed = CURRENT_TIMESTAMP,
                    next_review = ?,
                    interval = ?,
                    ease_factor = ?,
                    review_count = review_count + 1
                WHERE item_type = ? AND item_id = ?
            ''', (next_review_date, new_interval, new_ease_factor, item_type, item_id))
        else:
            cursor.execute('''
                INSERT INTO revision_schedules (item_type, item_id, next_review, interval, ease_factor, review_count)
                VALUES (?, ?, ?, ?, ?, 1)
            ''', (item_type, item_id, next_review_date, new_interval, new_ease_factor))
            
        conn.commit()
        return {
            'next_review': next_review_date.isoformat(),
            'interval': new_interval,
            'ease_factor': new_ease_factor
        }

    @staticmethod
    def get_due_items():
        """
        Fetch all items due for review today or earlier.
        """
        conn = db.get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, item_type, item_id, next_review, interval 
            FROM revision_schedules 
            WHERE next_review <= CURRENT_TIMESTAMP
            ORDER BY next_review ASC
        ''')
        
        items = [dict(row) for row in cursor.fetchall()]
        return items
