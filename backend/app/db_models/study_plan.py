# backend/app/db_models/study_plan.py
from app.db import get_db
import json
from datetime import datetime

def init_study_plan_tables():
    """Initialize study plan related tables"""
    conn = get_db()
    
    # Study Plan Table (High level container)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS study_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1,
            user_id INTEGER DEFAULT 1
        )
    ''')
    
    # Study Tasks Table (Granular tasks)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS study_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plan_id INTEGER,
            date TEXT NOT NULL,
            start_time TEXT NOT NULL, -- e.g., "04:00"
            end_time TEXT NOT NULL,   -- e.g., "05:00"
            subject TEXT NOT NULL,
            topic TEXT NOT NULL,
            resource_link TEXT,
            status TEXT DEFAULT 'pending', -- pending, completed, skipped, rescheduled
            google_event_id TEXT,
            FOREIGN KEY (plan_id) REFERENCES study_plans (id)
        )
    ''')

    # Study Sessions (Actual time tracked)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS study_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER DEFAULT 1,
            subject TEXT NOT NULL,
            topic TEXT,
            start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            end_time TIMESTAMP,
            duration_minutes INTEGER,
            notes TEXT
        )
    ''')

    # Time Boxes (Allocated time)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS time_boxes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER DEFAULT 1,
            subject TEXT NOT NULL,
            allocated_hours REAL DEFAULT 2.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()

def create_new_plan(start_date, end_date):
    """Create a new study plan entry"""
    conn = get_db()
    
    # Deactivate old plans
    conn.execute('UPDATE study_plans SET is_active = 0 WHERE is_active = 1')
    
    cursor = conn.execute('''
        INSERT INTO study_plans (start_date, end_date, is_active)
        VALUES (?, ?, 1)
    ''', (start_date, end_date))
    conn.commit()
    return cursor.lastrowid

def add_tasks_bulk(tasks):
    """Add multiple tasks efficiently"""
    conn = get_db()
    conn.executemany('''
        INSERT INTO study_tasks (
            plan_id, date, start_time, end_time, 
            subject, topic, resource_link, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', tasks)
    conn.commit()

def get_active_plan():
    """Get the currently active plan"""
    conn = get_db()
    plan = conn.execute('SELECT * FROM study_plans WHERE is_active = 1').fetchone()
    return dict(plan) if plan else None

def get_tasks_for_date(date_str):
    """Get tasks for a specific date"""
    conn = get_db()
    plan = get_active_plan()
    if not plan:
        return []
        
    tasks = conn.execute('''
        SELECT * FROM study_tasks 
        WHERE plan_id = ? AND date = ? 
        ORDER BY start_time ASC
    ''', (plan['id'], date_str)).fetchall()
    
    return [dict(t) for t in tasks]

def get_pending_tasks_before_date(date_str):
    """Get all pending tasks before a certain date (for rescheduling)"""
    conn = get_db()
    plan = get_active_plan()
    if not plan:
        return []
        
    tasks = conn.execute('''
        SELECT * FROM study_tasks 
        WHERE plan_id = ? AND date < ? AND status = 'pending'
        ORDER BY date ASC, start_time ASC
    ''', (plan['id'], date_str)).fetchall()
    
    return [dict(t) for t in tasks]

def get_pending_past_tasks_today(date_str, current_time_str):
    """Get all pending tasks for a specific date that have ended before current_time."""
    conn = get_db()
    plan = get_active_plan()
    if not plan:
        return []
        
    tasks = conn.execute('''
        SELECT * FROM study_tasks 
        WHERE plan_id = ? AND date = ? AND end_time < ? AND status = 'pending'
        ORDER BY start_time ASC
    ''', (plan['id'], date_str, current_time_str)).fetchall()
    
    return [dict(t) for t in tasks]

def update_task_status(task_id, status, google_event_id=None):
    """Update task status"""
    conn = get_db()
    if google_event_id:
        conn.execute('''
            UPDATE study_tasks 
            SET status = ?, google_event_id = ? 
            WHERE id = ?
        ''', (status, google_event_id, task_id))
    else:
        conn.execute('''
            UPDATE study_tasks 
            SET status = ? 
            WHERE id = ?
        ''', (status, task_id))
    conn.commit()

def reschedule_task(task_id, new_date, new_start, new_end):
    """Reschedule a task to a new slot"""
    conn = get_db()
    conn.execute('''
        UPDATE study_tasks 
        SET date = ?, start_time = ?, end_time = ?, status = 'rescheduled'
        WHERE id = ?
    ''', (new_date, new_start, new_end, task_id))
    conn.commit()

def get_future_buffer_slots(start_date_str):
    """Get all future buffer slots starting from a specific date"""
    conn = get_db()
    plan = get_active_plan()
    if not plan:
        return []
        
    tasks = conn.execute('''
        SELECT * FROM study_tasks 
        WHERE plan_id = ? AND date >= ? AND subject = 'Buffer' AND status = 'pending'
        ORDER BY date ASC, start_time ASC
    ''', (plan['id'], start_date_str)).fetchall()
    
    return [dict(t) for t in tasks]

def delete_task(task_id):
    """Delete a task (e.g., a buffer slot being overwritten)"""
    conn = get_db()
    conn.execute('DELETE FROM study_tasks WHERE id = ?', (task_id,))
    conn.commit()

def get_task_by_id(task_id):
    """Retrieve a single task by its ID."""
    conn = get_db()
    task = conn.execute('SELECT * FROM study_tasks WHERE id = ?', (task_id,)).fetchone()
    return dict(task) if task else None

def get_pending_task_count(plan_id, subject, exclude_task_id=None):
    """Get count of pending tasks for a subject in a plan."""
    conn = get_db()
    if exclude_task_id:
        count = conn.execute('''
            SELECT COUNT(*) FROM study_tasks
            WHERE plan_id = ? AND subject = ? AND status = 'pending' AND id != ?
        ''', (plan_id, subject, exclude_task_id)).fetchone()[0]
    else:
        count = conn.execute('''
            SELECT COUNT(*) FROM study_tasks
            WHERE plan_id = ? AND subject = ? AND status = 'pending'
        ''', (plan_id, subject)).fetchone()[0]
    return count
