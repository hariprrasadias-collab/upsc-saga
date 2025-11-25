# backend/app/routes/ravens.py
from flask import Blueprint, request, jsonify
import feedparser
from app.db_models.current_affairs import (
    init_current_affairs_table, 
    save_article, 
    get_saved_articles,
    update_article_tags,
    update_article_importance,
    toggle_bookmark,
    update_user_notes,
    link_anki_card,
    article_exists
)
from app.services.upsc_summarizer import (
    summarize_for_upsc,
    extract_image_from_article,
    find_related_pyqs
)
import anki_client

bp = Blueprint('ravens', __name__, url_prefix='/api/ravens')

# Database table will be initialized when app starts

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
            'https://www.project-syndicate.org/rss',
            'https://www.livemint.com/rss/opinion'
        ]
    }
    
    news_items = []
    target_feeds = feeds.get(raven_type, feeds['munin'])
    
    for url in target_feeds:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:10]:
                summary = entry.get('summary', '')[:200] + "..."
                
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
    content = data.get('summary', '')
    
    # Check for duplicates before processing
    if article_exists(link):
        return jsonify({'success': True, 'message': 'Article already exists', 'skipped': True})

    try:
        # Get AI summary and tags
        ai_result = summarize_for_upsc(title, content, link)
        
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
            'original_summary': content,
            'upsc_summary': ai_result['upsc_summary'],
            'key_points': ai_result['key_points'],
            'papers': ai_result['papers'],
            'subjects': ai_result['subjects'],
            'importance': ai_result['importance'],
            'image_url': image_url,
            'related_pyqs': related_pyqs
        }
        
        # Save to database
        article_id = save_article(article_data)
        
        return jsonify({
            'success': True,
            'article_id': article_id,
            'data': {
                **article_data,
                'id': article_id,
                'examQuestions': ai_result.get('exam_questions', []),
                'relatedTopics': ai_result.get('related_topics', [])
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
        # Create Anki note
        note = {
            'deckName': 'Current Affairs',
            'modelName': 'Basic',
            'fields': {
                'Front': f"{article['title']}\n\nTags: {', '.join(article['papers'])} | {', '.join(article['subjects'])}",
                'Back': f"{article['upscSummary']}\n\n**Key Points:**\n" + '\n'.join(f"• {point}" for point in article['keyPoints'])
            },
            'tags': article['subjects'] + article['papers']
        }
        
        # Add note to Anki
        result = anki_client.invoke('addNote', note=note)
        
        if result:
            # Link card to article
            link_anki_card(article_id, result)
            return jsonify({'success': True, 'ankiCardId': result})
        else:
            return jsonify({'success': False, 'error': 'Failed to create Anki card'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
