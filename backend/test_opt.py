import sqlite3
from app.services.analytics_service import get_all_subjects_performance, get_subject_performance

def test_opt():
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    subjects = ['GS1', 'GS2', 'GS3', 'GS4', 'Prelims', 'Optional']
    # test syntax
    pass
