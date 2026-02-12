# backend/app/db_models/current_affairs.py
"""
Database operations for UPSC Current Affairs
"""
from app.db import get_db
import sqlite3
import json
from datetime import datetime

def init_current_affairs_table():
    """Initialize the current_affairs table"""
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS current_affairs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            original_link TEXT,
            source TEXT,
            published_date TEXT,
            fetch_date TEXT DEFAULT CURRENT_TIMESTAMP,
            original_summary TEXT,
            upsc_summary TEXT,
            key_points TEXT,
            papers TEXT,
            subjects TEXT,
            importance INTEGER DEFAULT 2,
            is_bookmarked BOOLEAN DEFAULT 0,
            user_notes TEXT,
            anki_card_id INTEGER DEFAULT NULL,
            image_url TEXT,
            related_pyqs TEXT,
            prelims_pointers TEXT,
            mains_dimensions TEXT,
            steeple_analysis TEXT,
            inter_linkages TEXT,
            mind_map TEXT,
            quiz TEXT,
            answer_framework TEXT,
            essay_fodder TEXT,
            timeline TEXT,
            data_visualization TEXT,
            podcast_script TEXT,
            interview_questions TEXT,
            simulation_scenario TEXT,
            future_scenarios TEXT,
            historical_analogies TEXT,
            locations TEXT,
            socratic_clash TEXT,
            mnemonics TEXT,
            systemic_bias TEXT,
            butterfly_effect TEXT,
            polymath_angle TEXT,
            quote_injection TEXT,
            roleplay_persona TEXT,
            systems_loops TEXT,
            counter_factuals TEXT,
            civilizational_parallels TEXT,
            fermi_estimates TEXT,
            global_context TEXT
        )
    ''')

    # Attempt to add new columns for existing databases
    # Enhanced Metadata v1
    try:
        conn.execute('ALTER TABLE current_affairs ADD COLUMN prelims_pointers TEXT')
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute('ALTER TABLE current_affairs ADD COLUMN mains_dimensions TEXT')
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute('ALTER TABLE current_affairs ADD COLUMN steeple_analysis TEXT')
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute('ALTER TABLE current_affairs ADD COLUMN inter_linkages TEXT')
    except sqlite3.OperationalError:
        pass

    # God Mode Metadata v2
    try:
        conn.execute('ALTER TABLE current_affairs ADD COLUMN mind_map TEXT')
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute('ALTER TABLE current_affairs ADD COLUMN quiz TEXT')
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute('ALTER TABLE current_affairs ADD COLUMN answer_framework TEXT')
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute('ALTER TABLE current_affairs ADD COLUMN essay_fodder TEXT')
    except sqlite3.OperationalError:
        pass

    # Universe Mode Metadata v3
    try:
        conn.execute('ALTER TABLE current_affairs ADD COLUMN timeline TEXT')
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute('ALTER TABLE current_affairs ADD COLUMN data_visualization TEXT')
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute('ALTER TABLE current_affairs ADD COLUMN podcast_script TEXT')
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute('ALTER TABLE current_affairs ADD COLUMN interview_questions TEXT')
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute('ALTER TABLE current_affairs ADD COLUMN simulation_scenario TEXT')
    except sqlite3.OperationalError:
        pass

    # Omniverse Mode Metadata v4
    try:
        conn.execute('ALTER TABLE current_affairs ADD COLUMN future_scenarios TEXT')
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute('ALTER TABLE current_affairs ADD COLUMN historical_analogies TEXT')
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute('ALTER TABLE current_affairs ADD COLUMN locations TEXT')
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute('ALTER TABLE current_affairs ADD COLUMN socratic_clash TEXT')
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute('ALTER TABLE current_affairs ADD COLUMN mnemonics TEXT')
    except sqlite3.OperationalError:
        pass

    # Singularity Mode Metadata v5
    try:
        conn.execute('ALTER TABLE current_affairs ADD COLUMN systemic_bias TEXT')
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute('ALTER TABLE current_affairs ADD COLUMN butterfly_effect TEXT')
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute('ALTER TABLE current_affairs ADD COLUMN polymath_angle TEXT')
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute('ALTER TABLE current_affairs ADD COLUMN quote_injection TEXT')
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute('ALTER TABLE current_affairs ADD COLUMN roleplay_persona TEXT')
    except sqlite3.OperationalError:
        pass

    # Akaashic Mode Metadata v6
    try:
        conn.execute('ALTER TABLE current_affairs ADD COLUMN systems_loops TEXT')
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute('ALTER TABLE current_affairs ADD COLUMN counter_factuals TEXT')
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute('ALTER TABLE current_affairs ADD COLUMN civilizational_parallels TEXT')
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute('ALTER TABLE current_affairs ADD COLUMN fermi_estimates TEXT')
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute('ALTER TABLE current_affairs ADD COLUMN global_context TEXT')
    except sqlite3.OperationalError:
        pass

    conn.commit()

def article_exists(link):
    """Check if article with link already exists"""
    conn = get_db()
    cursor = conn.execute('SELECT id FROM current_affairs WHERE original_link = ?', (link,))
    return cursor.fetchone() is not None

def save_article(article_data):
    """Save a new article to database"""
    conn = get_db()
    try:
        cursor = conn.execute('''
            INSERT INTO current_affairs (
                title, original_link, source, published_date,
                original_summary, upsc_summary, key_points,
                papers, subjects, importance, image_url, related_pyqs,
                prelims_pointers, mains_dimensions, steeple_analysis, inter_linkages,
                mind_map, quiz, answer_framework, essay_fodder,
                timeline, data_visualization, podcast_script, interview_questions, simulation_scenario,
                future_scenarios, historical_analogies, locations, socratic_clash, mnemonics,
                systemic_bias, butterfly_effect, polymath_angle, quote_injection, roleplay_persona,
                systems_loops, counter_factuals, civilizational_parallels, fermi_estimates, global_context
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            article_data['title'],
            article_data['link'],
            article_data['source'],
            article_data['published'],
            article_data.get('original_summary', ''),
            article_data.get('upsc_summary', ''),
            json.dumps(article_data.get('key_points', [])),
            json.dumps(article_data.get('papers', [])),
            json.dumps(article_data.get('subjects', [])),
            article_data.get('importance', 2),
            article_data.get('image_url', ''),
            json.dumps(article_data.get('related_pyqs', [])),
            json.dumps(article_data.get('prelims_pointers', [])),
            json.dumps(article_data.get('mains_dimensions', [])),
            json.dumps(article_data.get('steeple_analysis', {})),
            json.dumps(article_data.get('inter_linkages', [])),
            article_data.get('mind_map', ''),
            json.dumps(article_data.get('quiz', [])),
            json.dumps(article_data.get('answer_framework', {})),
            json.dumps(article_data.get('essay_fodder', {})),
            json.dumps(article_data.get('timeline', [])),
            json.dumps(article_data.get('data_visualization', {})),
            article_data.get('podcast_script', ''),
            json.dumps(article_data.get('interview_questions', [])),
            json.dumps(article_data.get('simulation_scenario', {})),
            json.dumps(article_data.get('future_scenarios', {})),
            json.dumps(article_data.get('historical_analogies', [])),
            json.dumps(article_data.get('locations', [])),
            json.dumps(article_data.get('socratic_clash', [])),
            json.dumps(article_data.get('mnemonics', [])),
            # Singularity Mode
            json.dumps(article_data.get('systemic_bias', {})),
            json.dumps(article_data.get('butterfly_effect', [])),
            json.dumps(article_data.get('polymath_angle', {})),
            json.dumps(article_data.get('quote_injection', {})),
            json.dumps(article_data.get('roleplay_persona', {})),
            # Akaashic Mode
            json.dumps(article_data.get('systems_loops', [])),
            json.dumps(article_data.get('counter_factuals', [])),
            json.dumps(article_data.get('civilizational_parallels', [])),
            json.dumps(article_data.get('fermi_estimates', {})),
            json.dumps(article_data.get('global_context', []))
        ))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        # Article already exists (caught by UNIQUE index)
        return None

def get_saved_articles(filters=None):
    """Get saved articles with optional filters"""
    conn = get_db()
    query = 'SELECT * FROM current_affairs WHERE 1=1'
    params = []
    
    if filters:
        if filters.get('paper'):
            query += ' AND papers LIKE ?'
            params.append(f'%{filters["paper"]}%')
        
        if filters.get('subject'):
            query += ' AND subjects LIKE ?'
            params.append(f'%{filters["subject"]}%')
        
        if filters.get('importance'):
            query += ' AND importance = ?'
            params.append(filters['importance'])
        
        if filters.get('bookmarked'):
            query += ' AND is_bookmarked = 1'
        
        if filters.get('search'):
            query += ' AND (title LIKE ? OR upsc_summary LIKE ?)'
            search_term = f'%{filters["search"]}%'
            params.extend([search_term, search_term])
    
    query += ' ORDER BY fetch_date DESC'
    
    rows = conn.execute(query, params).fetchall()
    
    articles = []
    for row in rows:
        articles.append({
            'id': row['id'],
            'title': row['title'],
            'link': row['original_link'],
            'source': row['source'],
            'published': row['published_date'],
            'fetchDate': row['fetch_date'],
            'originalSummary': row['original_summary'],
            'upscSummary': row['upsc_summary'],
            'keyPoints': json.loads(row['key_points'] or '[]'),
            'papers': json.loads(row['papers'] or '[]'),
            'subjects': json.loads(row['subjects'] or '[]'),
            'importance': row['importance'],
            'isBookmarked': bool(row['is_bookmarked']),
            'userNotes': row['user_notes'],
            'ankiCardId': row['anki_card_id'],
            'imageUrl': row['image_url'],
            'relatedPyqs': json.loads(row['related_pyqs'] or '[]'),
            'prelimsPointers': json.loads(row['prelims_pointers'] or '[]') if 'prelims_pointers' in row.keys() else [],
            'mainsDimensions': json.loads(row['mains_dimensions'] or '[]') if 'mains_dimensions' in row.keys() else [],
            'steepleAnalysis': json.loads(row['steeple_analysis'] or '{}') if 'steeple_analysis' in row.keys() else {},
            'interLinkages': json.loads(row['inter_linkages'] or '[]') if 'inter_linkages' in row.keys() else [],
            # God Mode fields
            'mindMap': row['mind_map'] if 'mind_map' in row.keys() else '',
            'quiz': json.loads(row['quiz'] or '[]') if 'quiz' in row.keys() else [],
            'answerFramework': json.loads(row['answer_framework'] or '{}') if 'answer_framework' in row.keys() else {},
            'essayFodder': json.loads(row['essay_fodder'] or '{}') if 'essay_fodder' in row.keys() else {},
            # Universe Mode fields
            'timeline': json.loads(row['timeline'] or '[]') if 'timeline' in row.keys() else [],
            'dataVisualization': json.loads(row['data_visualization'] or '{}') if 'data_visualization' in row.keys() else {},
            'podcastScript': row['podcast_script'] if 'podcast_script' in row.keys() else '',
            'interviewQuestions': json.loads(row['interview_questions'] or '[]') if 'interview_questions' in row.keys() else [],
            'simulationScenario': json.loads(row['simulation_scenario'] or '{}') if 'simulation_scenario' in row.keys() else {},
            # Omniverse Mode fields
            'futureScenarios': json.loads(row['future_scenarios'] or '{}') if 'future_scenarios' in row.keys() else {},
            'historicalAnalogies': json.loads(row['historical_analogies'] or '[]') if 'historical_analogies' in row.keys() else [],
            'locations': json.loads(row['locations'] or '[]') if 'locations' in row.keys() else [],
            'socraticClash': json.loads(row['socratic_clash'] or '[]') if 'socratic_clash' in row.keys() else [],
            'mnemonics': json.loads(row['mnemonics'] or '[]') if 'mnemonics' in row.keys() else [],
            # Singularity Mode fields
            'systemicBias': json.loads(row['systemic_bias'] or '{}') if 'systemic_bias' in row.keys() else {},
            'butterflyEffect': json.loads(row['butterfly_effect'] or '[]') if 'butterfly_effect' in row.keys() else [],
            'polymathAngle': json.loads(row['polymath_angle'] or '{}') if 'polymath_angle' in row.keys() else {},
            'quoteInjection': json.loads(row['quote_injection'] or '{}') if 'quote_injection' in row.keys() else {},
            'roleplayPersona': json.loads(row['roleplay_persona'] or '{}') if 'roleplay_persona' in row.keys() else {},
            # Akaashic Mode fields
            'systemsLoops': json.loads(row['systems_loops'] or '[]') if 'systems_loops' in row.keys() else [],
            'counterFactuals': json.loads(row['counter_factuals'] or '[]') if 'counter_factuals' in row.keys() else [],
            'civilizationalParallels': json.loads(row['civilizational_parallels'] or '[]') if 'civilizational_parallels' in row.keys() else [],
            'fermiEstimates': json.loads(row['fermi_estimates'] or '{}') if 'fermi_estimates' in row.keys() else {},
            'globalContext': json.loads(row['global_context'] or '[]') if 'global_context' in row.keys() else []
        })
    
    return articles

def update_article_tags(article_id, papers, subjects):
    """Update article tags"""
    conn = get_db()
    conn.execute('''
        UPDATE current_affairs 
        SET papers = ?, subjects = ?
        WHERE id = ?
    ''', (json.dumps(papers), json.dumps(subjects), article_id))
    conn.commit()

def update_article_importance(article_id, importance):
    """Update article importance"""
    conn = get_db()
    conn.execute('''
        UPDATE current_affairs 
        SET importance = ?
        WHERE id = ?
    ''', (importance, article_id))
    conn.commit()

def toggle_bookmark(article_id):
    """Toggle bookmark status"""
    conn = get_db()
    current = conn.execute(
        'SELECT is_bookmarked FROM current_affairs WHERE id = ?',
        (article_id,)
    ).fetchone()
    
    new_status = 0 if current['is_bookmarked'] else 1
    conn.execute('''
        UPDATE current_affairs 
        SET is_bookmarked = ?
        WHERE id = ?
    ''', (new_status, article_id))
    conn.commit()
    return bool(new_status)

def update_user_notes(article_id, notes):
    """Update user notes"""
    conn = get_db()
    conn.execute('''
        UPDATE current_affairs 
        SET user_notes = ?
        WHERE id = ?
    ''', (notes, article_id))
    conn.commit()

def link_anki_card(article_id, anki_card_id):
    """Link article to Anki card"""
    conn = get_db()
    conn.execute('''
        UPDATE current_affairs 
        SET anki_card_id = ?
        WHERE id = ?
    ''', (anki_card_id, article_id))
    conn.commit()

def update_article_content_by_link(link, article_data):
    """Update article content by link (for re-processing)"""
    conn = get_db()
    conn.execute('''
        UPDATE current_affairs 
        SET upsc_summary = ?,
            key_points = ?,
            papers = ?,
            subjects = ?,
            importance = ?,
            image_url = ?,
            related_pyqs = ?,
            prelims_pointers = ?,
            mains_dimensions = ?,
            steeple_analysis = ?,
            inter_linkages = ?,
            mind_map = ?,
            quiz = ?,
            answer_framework = ?,
            essay_fodder = ?,
            timeline = ?,
            data_visualization = ?,
            podcast_script = ?,
            interview_questions = ?,
            simulation_scenario = ?,
            future_scenarios = ?,
            historical_analogies = ?,
            locations = ?,
            socratic_clash = ?,
            mnemonics = ?,
            systemic_bias = ?,
            butterfly_effect = ?,
            polymath_angle = ?,
            quote_injection = ?,
            roleplay_persona = ?,
            systems_loops = ?,
            counter_factuals = ?,
            civilizational_parallels = ?,
            fermi_estimates = ?,
            global_context = ?,
            fetch_date = CURRENT_TIMESTAMP
        WHERE original_link = ?
    ''', (
        article_data.get('upsc_summary', ''),
        json.dumps(article_data.get('key_points', [])),
        json.dumps(article_data.get('papers', [])),
        json.dumps(article_data.get('subjects', [])),
        article_data.get('importance', 2),
        article_data.get('image_url', ''),
        json.dumps(article_data.get('related_pyqs', [])),
        json.dumps(article_data.get('prelims_pointers', [])),
        json.dumps(article_data.get('mains_dimensions', [])),
        json.dumps(article_data.get('steeple_analysis', {})),
        json.dumps(article_data.get('inter_linkages', [])),
        article_data.get('mind_map', ''),
        json.dumps(article_data.get('quiz', [])),
        json.dumps(article_data.get('answer_framework', {})),
        json.dumps(article_data.get('essay_fodder', {})),
        json.dumps(article_data.get('timeline', [])),
        json.dumps(article_data.get('data_visualization', {})),
        article_data.get('podcast_script', ''),
        json.dumps(article_data.get('interview_questions', [])),
        json.dumps(article_data.get('simulation_scenario', {})),
        json.dumps(article_data.get('future_scenarios', {})),
        json.dumps(article_data.get('historical_analogies', [])),
        json.dumps(article_data.get('locations', [])),
        json.dumps(article_data.get('socratic_clash', [])),
        json.dumps(article_data.get('mnemonics', [])),
        json.dumps(article_data.get('systemic_bias', {})),
        json.dumps(article_data.get('butterfly_effect', [])),
        json.dumps(article_data.get('polymath_angle', {})),
        json.dumps(article_data.get('quote_injection', {})),
        json.dumps(article_data.get('roleplay_persona', {})),
        json.dumps(article_data.get('systems_loops', [])),
        json.dumps(article_data.get('counter_factuals', [])),
        json.dumps(article_data.get('civilizational_parallels', [])),
        json.dumps(article_data.get('fermi_estimates', {})),
        json.dumps(article_data.get('global_context', [])),
        link
    ))
    conn.commit()
    
    # Return the ID
    cursor = conn.execute('SELECT id FROM current_affairs WHERE original_link = ?', (link,))
    row = cursor.fetchone()
    return row['id'] if row else None
