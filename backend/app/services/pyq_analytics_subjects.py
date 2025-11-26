def get_all_subjects() -> List[str]:
    """Get list of all unique subjects from PYQ database"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT DISTINCT subject 
        FROM pyq_questions 
        WHERE subject IS NOT NULL AND subject != ''
        ORDER BY subject
    """)
    
    results = cursor.fetchall()
    conn.close()
    
    return [row['subject'] for row in results]
