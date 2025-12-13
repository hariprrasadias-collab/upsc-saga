# backend/app/routes/ravens.py
import threading
from flask import Blueprint, request, jsonify, current_app
import feedparser
import threading
import time
from app.db_models.current_affairs import (
    init_current_affairs_table, 
    save_article, 
    get_saved_articles,
    update_article_tags,
    update_article_importance,
    toggle_bookmark,
    update_user_notes,
    link_anki_card,
    article_exists,
    update_article_content_by_link
)
from app.services.upsc_summarizer import (
    summarize_for_upsc,
    extract_image_from_article,
    find_related_pyqs,
    fetch_article_content
)
import anki_client

bp = Blueprint('ravens', __name__, url_prefix='/api/ravens')

# Database table will be initialized when app starts

def run_background_fetch(app):
    """Background task to fetch and process news"""
    with app.app_context():
        print("🦅 Raven: Starting background fetch mission...")
        
        feeds = [
            'https://www.thehindu.com/news/national/feeder/default.rss',
            'https://pib.gov.in/RSS/RssFeed.aspx?ModId=2',
            'https://indianexpress.com/section/india/feed/',
            'https://www.thehindu.com/opinion/editorial/feeder/default.rss',
            'https://indianexpress.com/section/opinion/editorials/feed/'
        ]
        
        processed_count = 0
        
        for url in feeds:
            try:
                print(f"🦅 Raven: Scouting {url}...")
                feed = feedparser.parse(url)
                
                # Process only the latest 5 entries from each feed to avoid overload
                for entry in feed.entries[:5]:
                    link = entry.link
                    
                    # Skip if already exists
                    if article_exists(link):
                        continue
                        
                    print(f"🦅 Raven: Found new artifact - {entry.title}")
                    
                    try:
                        # 1. Fetch Content
                        full_content = fetch_article_content(link)
                        if not full_content or len(full_content) < 100:
                            full_content = entry.get('summary', '')
                        
                        # 2. AI Summarization
                        ai_result = summarize_for_upsc(entry.title, full_content, link)
                        
                        # 3. Extract Image
                        image_url = extract_image_from_article(link)
                        
                        # 4. Find PYQs
                        related_pyqs = find_related_pyqs(
                            ai_result['subjects'],
                            ai_result['papers']
                        )
                        
                        # 5. Save to DB
                        article_data = {
                            'title': entry.title,
                            'link': link,
                            'source': feed.feed.get('title', 'Unknown Source'),
                            'published': entry.get('published', 'Today'),
                            'original_summary': entry.get('summary', ''),
                            'upsc_summary': ai_result['upsc_summary'],
                            'key_points': ai_result['key_points'],
                            'papers': ai_result['papers'],
                            'subjects': ai_result['subjects'],
                            'importance': ai_result['importance'],
                            'image_url': image_url,
                            'related_pyqs': related_pyqs,
                            # Enhanced Metadata
                            'prelims_pointers': ai_result.get('prelims_pointers', []),
                            'mains_dimensions': ai_result.get('mains_dimensions', []),
                            'steeple_analysis': ai_result.get('steeple_analysis', {}),
                            'inter_linkages': ai_result.get('inter_linkages', []),
                            # God Mode Metadata
                            'mind_map': ai_result.get('mind_map', ''),
                            'quiz': ai_result.get('quiz', []),
                            'answer_framework': ai_result.get('answer_framework', {}),
                            'essay_fodder': ai_result.get('essay_fodder', {}),
                            # Universe Mode Metadata
                            'timeline': ai_result.get('timeline', []),
                            'data_visualization': ai_result.get('data_visualization', {}),
                            'podcast_script': ai_result.get('podcast_script', ''),
                            'interview_questions': ai_result.get('interview_questions', []),
                            'simulation_scenario': ai_result.get('simulation_scenario', {}),
                            # Omniverse Mode Metadata
                            'future_scenarios': ai_result.get('future_scenarios', {}),
                            'historical_analogies': ai_result.get('historical_analogies', []),
                            'locations': ai_result.get('locations', []),
                            'socratic_clash': ai_result.get('socratic_clash', []),
                            'mnemonics': ai_result.get('mnemonics', []),
                            # Singularity Mode Metadata
                            'systemic_bias': ai_result.get('systemic_bias', {}),
                            'butterfly_effect': ai_result.get('butterfly_effect', []),
                            'polymath_angle': ai_result.get('polymath_angle', {}),
                            'quote_injection': ai_result.get('quote_injection', {}),
                            'roleplay_persona': ai_result.get('roleplay_persona', {}),
                            # Akaashic Mode Metadata
                            'systems_loops': ai_result.get('systems_loops', []),
                            'counter_factuals': ai_result.get('counter_factuals', []),
                            'civilizational_parallels': ai_result.get('civilizational_parallels', []),
                            'fermi_estimates': ai_result.get('fermi_estimates', {}),
                            'global_context': ai_result.get('global_context', [])
                        }
                        
                        save_article(article_data)
                        processed_count += 1
                        print(f"🦅 Raven: Successfully archived - {entry.title}")
                        
                        # Be gentle with the API (10 RPM limit = 6s delay minimum, using 10s to be safe)
                        time.sleep(10)
                        
                    except Exception as inner_e:
                        print(f"🦅 Raven: Failed to process {entry.title}: {inner_e}")
                        
            except Exception as e:
                print(f"🦅 Raven: Failed to fly to {url}: {e}")
                
        print(f"🦅 Raven: Mission complete. Archived {processed_count} new artifacts.")

@bp.route('/background-fetch', methods=['POST'])
def trigger_background_fetch():
    """Trigger the background fetch process"""
    app = current_app._get_current_object()
    thread = threading.Thread(target=run_background_fetch, args=(app,))
    thread.daemon = True
    thread.start()
    return jsonify({'success': True, 'message': 'Ravens dispatched in background'})

@bp.route('', methods=['GET'])
def call_the_ravens():
    """Fetch live news from RSS feeds"""
    raven_type = request.args.get('type', 'munin')
    
    feeds = {
        'munin': [
            'https://www.thehindu.com/news/national/feeder/default.rss',
            'https://pib.gov.in/RSS/RssFeed.aspx?ModId=2',
            'https://indianexpress.com/section/india/feed/'
        ],
        'hugin': [
            'https://www.thehindu.com/opinion/editorial/feeder/default.rss',
            'https://indianexpress.com/section/opinion/editorials/feed/'
        ]
    }
    
    news_items = []
    target_feeds = feeds.get(raven_type, feeds['munin'])
    
    for url in target_feeds:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:10]:
                summary = entry.get('summary', '')
                
                # Check if already saved
                is_saved = article_exists(entry.link)
                
                news_items.append({
                    "title": entry.title,
                    "link": entry.link,
                    "published": entry.get('published', 'Today'),
                    "source": feed.feed.get('title', 'Unknown Source'),
                    "summary": summary,
                    "isSaved": is_saved
                })
        except Exception as e:
            print(f"Raven failed to fly to {url}: {e}")
    
    return jsonify(news_items)

@bp.route('/process', methods=['POST'])
def process_article():
    """Process an article with Gemini AI and save to database"""
    data = request.get_json()
    
    title = data.get('title')
    link = data.get('link')
    source = data.get('source')
    published = data.get('published')
    rss_summary = data.get('summary', '')
    force_reprocess = data.get('force', False)
    
    # Check for duplicates before processing (unless forcing)
    if article_exists(link) and not force_reprocess:
        return jsonify({'success': True, 'message': 'Article already exists', 'skipped': True})

    try:
        # Fetch full content
        full_content = fetch_article_content(link)
        if not full_content or len(full_content) < 100:
            full_content = rss_summary # Fallback
            
        # Get AI summary and tags
        ai_result = summarize_for_upsc(title, full_content, link)
        
        # Extract image
        image_url = extract_image_from_article(link)
        
        # Find related PYQs
        related_pyqs = find_related_pyqs(
            ai_result['subjects'],
            ai_result['papers']
        )
        
        # Prepare article data
        article_data = {
            'title': title,
            'link': link,
            'source': source,
            'published': published,
            'original_summary': rss_summary,
            'upsc_summary': ai_result['upsc_summary'],
            'key_points': ai_result['key_points'],
            'papers': ai_result['papers'],
            'subjects': ai_result['subjects'],
            'importance': ai_result['importance'],
            'image_url': image_url,
            'related_pyqs': related_pyqs,
            # Enhanced Metadata
            'prelims_pointers': ai_result.get('prelims_pointers', []),
            'mains_dimensions': ai_result.get('mains_dimensions', []),
            'steeple_analysis': ai_result.get('steeple_analysis', {}),
            'inter_linkages': ai_result.get('inter_linkages', []),
            # God Mode Metadata
            'mind_map': ai_result.get('mind_map', ''),
            'quiz': ai_result.get('quiz', []),
            'answer_framework': ai_result.get('answer_framework', {}),
            'essay_fodder': ai_result.get('essay_fodder', {}),
            # Universe Mode Metadata
            'timeline': ai_result.get('timeline', []),
            'data_visualization': ai_result.get('data_visualization', {}),
            'podcast_script': ai_result.get('podcast_script', ''),
            'interview_questions': ai_result.get('interview_questions', []),
            'simulation_scenario': ai_result.get('simulation_scenario', {}),
            # Omniverse Mode Metadata
            'future_scenarios': ai_result.get('future_scenarios', {}),
            'historical_analogies': ai_result.get('historical_analogies', []),
            'locations': ai_result.get('locations', []),
            'socratic_clash': ai_result.get('socratic_clash', []),
            'mnemonics': ai_result.get('mnemonics', []),
            # Singularity Mode Metadata
            'systemic_bias': ai_result.get('systemic_bias', {}),
            'butterfly_effect': ai_result.get('butterfly_effect', []),
            'polymath_angle': ai_result.get('polymath_angle', {}),
            'quote_injection': ai_result.get('quote_injection', {}),
            'roleplay_persona': ai_result.get('roleplay_persona', {}),
            # Akaashic Mode Metadata
            'systems_loops': ai_result.get('systems_loops', []),
            'counter_factuals': ai_result.get('counter_factuals', []),
            'civilizational_parallels': ai_result.get('civilizational_parallels', []),
            'fermi_estimates': ai_result.get('fermi_estimates', {}),
            'global_context': ai_result.get('global_context', [])
        }
        
        # Save or Update
        if article_exists(link):
             article_id = update_article_content_by_link(link, article_data)
             action = 'updated'
        else:
             article_id = save_article(article_data)
             action = 'saved'
        
        return jsonify({
            'success': True,
            'article_id': article_id,
            'action': action,
            'data': {
                **article_data,
                'id': article_id,
                'examQuestions': ai_result.get('exam_questions', []),
                'relatedTopics': ai_result.get('related_topics', []),
                'steepleAnalysis': ai_result.get('steeple_analysis', {}),
                'interLinkages': ai_result.get('inter_linkages', []),
                'mindMap': ai_result.get('mind_map', ''),
                'quiz': ai_result.get('quiz', []),
                'answerFramework': ai_result.get('answer_framework', {}),
                'essayFodder': ai_result.get('essay_fodder', {}),
                'timeline': ai_result.get('timeline', []),
                'dataVisualization': ai_result.get('data_visualization', {}),
                'podcastScript': ai_result.get('podcast_script', ''),
                'interviewQuestions': ai_result.get('interview_questions', []),
                'simulationScenario': ai_result.get('simulation_scenario', {}),
                'futureScenarios': ai_result.get('future_scenarios', {}),
                'historicalAnalogies': ai_result.get('historical_analogies', []),
                'locations': ai_result.get('locations', []),
                'socraticClash': ai_result.get('socratic_clash', []),
                'mnemonics': ai_result.get('mnemonics', []),
                'systemicBias': ai_result.get('systemic_bias', {}),
                'butterflyEffect': ai_result.get('butterfly_effect', []),
                'polymathAngle': ai_result.get('polymath_angle', {}),
                'quoteInjection': ai_result.get('quote_injection', {}),
                'roleplayPersona': ai_result.get('roleplay_persona', {}),
                'systemsLoops': ai_result.get('systems_loops', []),
                'counterFactuals': ai_result.get('counter_factuals', []),
                'civilizationalParallels': ai_result.get('civilizational_parallels', []),
                'fermiEstimates': ai_result.get('fermi_estimates', {}),
                'globalContext': ai_result.get('global_context', [])
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/saved', methods=['GET'])
def get_saved():
    """Get saved articles with optional filters"""
    filters = {}
    
    if request.args.get('paper'):
        filters['paper'] = request.args.get('paper')
    
    if request.args.get('subject'):
        filters['subject'] = request.args.get('subject')
    
    if request.args.get('importance'):
        filters['importance'] = int(request.args.get('importance'))
    
    if request.args.get('bookmarked') == 'true':
        filters['bookmarked'] = True
    
    if request.args.get('search'):
        filters['search'] = request.args.get('search')
    
    articles = get_saved_articles(filters)
    return jsonify(articles)

@bp.route('/<int:article_id>/tags', methods=['PUT'])
def update_tags(article_id):
    """Update article tags"""
    data = request.get_json()
    papers = data.get('papers', [])
    subjects = data.get('subjects', [])
    
    update_article_tags(article_id, papers, subjects)
    return jsonify({'success': True})

@bp.route('/<int:article_id>/importance', methods=['PUT'])
def update_importance(article_id):
    """Update article importance"""
    data = request.get_json()
    importance = data.get('importance', 2)
    
    update_article_importance(article_id, importance)
    return jsonify({'success': True})

@bp.route('/<int:article_id>/bookmark', methods=['POST'])
def bookmark_article(article_id):
    """Toggle bookmark status"""
    is_bookmarked = toggle_bookmark(article_id)
    return jsonify({'success': True, 'isBookmarked': is_bookmarked})

@bp.route('/<int:article_id>/notes', methods=['PUT'])
def save_notes(article_id):
    """Save user notes"""
    data = request.get_json()
    notes = data.get('notes', '')
    
    update_user_notes(article_id, notes)
    return jsonify({'success': True})

@bp.route('/<int:article_id>/to-anki', methods=['POST'])
def add_to_anki(article_id):
    """Create Anki card from article"""
    # Get article from database
    articles = get_saved_articles()
    article = next((a for a in articles if a['id'] == article_id), None)
    
    if not article:
        return jsonify({'success': False, 'error': 'Article not found'}), 404
    
    try:
        from app.services.upsc_summarizer import generate_flashcard_content
        
        # Generate Q&A
        flashcard = generate_flashcard_content(article['title'], article['upscSummary'])
        
        # Create Anki note
        note = {
            'deckName': 'Current Affairs',
            'modelName': 'Basic',
            'fields': {
                'Front': flashcard['question'],
                'Back': f"{flashcard['answer']}\n\n**Source:** {article['source']}"
            },
            'tags': article['subjects'] + article['papers'] + ['upsc_raven']
        }
        
        # Add note to Anki
        result = anki_client.invoke('addNote', note=note)
        
        if result:
            # Link card to article
            link_anki_card(article_id, result)
            return jsonify({'success': True, 'ankiCardId': result})
        else:
            return jsonify({'success': False, 'error': 'Failed to create Anki card. Is Anki running?'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


