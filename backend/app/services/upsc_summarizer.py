# backend/app/services/upsc_summarizer.py
"""
UPSC-focused news summarization using Google Gemini Pro.
Provides a function to summarise an article and infer UPSC paper and subject tags.
If Gemini fails or returns generic tags, a keyword‑based fallback is applied.
"""
import os
import json
import re
import time
import socket
import ipaddress
from urllib.parse import urlparse, urljoin
from dotenv import load_dotenv
from app.services.model_manager import model_manager

# Load environment variables
load_dotenv()

# GEMINI_API_KEY removed here - managed by ModelManager
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '') # Keep for internal check if needed


# UPSC Paper and Subject classifications
PAPERS = ['GS1', 'GS2', 'GS3', 'GS4', 'Essay', 'Optional']
SUBJECTS = [
    'Polity & Governance', 'Economics', 'International Relations',
    'Environment & Ecology', 'Science & Technology', 'Internal Security',
    'Disaster Management', 'Social Issues', 'History & Culture',
    'Geography', 'Ethics', 'Current Affairs'
]

def is_safe_url(url):
    """
    Validates that a URL is safe to fetch (SSRF protection).
    Ensures the scheme is http/https and the hostname resolves to a public IP.
    """
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ('http', 'https'):
            return False

        hostname = parsed.hostname
        if not hostname:
            return False

        # Resolve hostname to IP
        try:
            ip_str = socket.gethostbyname(hostname)
        except socket.gaierror:
            return False # Can't resolve

        ip = ipaddress.ip_address(ip_str)

        # Check against private, loopback, and reserved ranges
        if ip.is_loopback or ip.is_private or ip.is_link_local or ip.is_multicast or ip.is_reserved:
            return False

        return True
    except Exception:
        return False

def retry_with_backoff(func, *args, **kwargs):
    """Retry a function with exponential backoff for rate limits."""
    max_retries = 3
    base_delay = 10  # Start with 10 seconds (since limit is 10 RPM)
    
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e: # Simplified exception handling as google_exceptions not imported
             if attempt == max_retries - 1:
                raise
             delay = base_delay * (2 ** attempt)
             print(f"⚠️ Error. Retrying in {delay} seconds...")
             time.sleep(delay)

def get_gemini_text(response):
    """Safely extract text from Gemini response, handling safety blocks."""
    try:
        return response.text.strip()
    except ValueError:
        # This happens if the response was blocked by safety filters
        if hasattr(response, 'prompt_feedback'):
            print(f"⚠️ Gemini Safety Block: {response.prompt_feedback}")
        return ""

def _infer_tags(title: str, content: str):
    """Keyword‑based inference for UPSC papers and subjects.
    Returns a tuple (papers, subjects). Used as a lightweight fallback when Gemini
    does not provide useful tags.
    """
    txt = (title + " " + content).lower()
    # Mapping of keywords to papers
    paper_keywords = {
        'gs1': ['history', 'culture', 'geography', 'society'],
        'gs2': ['polity', 'governance', 'constitution', 'rights', 'international relations', 'social justice'],
        'gs3': ['economy', 'economic', 'finance', 'budget', 'inflation', 'tax', 'science', 'environment', 'security', 'technology', 'energy'],
        'gs4': ['ethics', 'moral', 'integrity']
    }
    # Mapping of keywords to subjects
    subject_keywords = {
        'Polity & Governance': ['polity', 'governance', 'constitution', 'rights'],
        'Economics': ['economy', 'economic', 'finance', 'budget', 'inflation', 'tax'],
        'International Relations': ['international', 'relations', 'foreign', 'diplomacy', 'defence', 'security'],
        'Environment & Ecology': ['environment', 'ecology', 'climate', 'pollution', 'biodiversity'],
        'Science & Technology': ['science', 'technology', 'tech', 'research', 'innovation', 'space', 'energy'],
        'Internal Security': ['security', 'terror', 'law and order', 'crime'],
        'Disaster Management': ['disaster', 'flood', 'earthquake', 'relief'],
        'Social Issues': ['social', 'women', 'caste', 'religion', 'health'],
        'History & Culture': ['history', 'culture', 'heritage', 'archaeology'],
        'Geography': ['geography', 'map', 'terrain', 'climate'],
        'Ethics': ['ethics', 'morality', 'integrity'],
        'Current Affairs': []
    }
    inferred_papers = []
    for paper, keys in paper_keywords.items():
        if any(k in txt for k in keys):
            inferred_papers.append(paper.upper())
    if not inferred_papers:
        inferred_papers.append('GS2')  # safe default
    inferred_subjects = []
    for subj, keys in subject_keywords.items():
        if keys and any(k in txt for k in keys):
            inferred_subjects.append(subj)
    if not inferred_subjects:
        inferred_subjects.append('Current Affairs')
    return inferred_papers, inferred_subjects

def _simple_extraction(title, content):
    """Fallback extraction when Gemini is unavailable or fails.
    Uses keyword heuristics to guess papers and subjects.
    """
    papers, subjects = _infer_tags(title, content)
    return {
        'upsc_summary': content,  # NO TRUNCATION
        'key_points': [title],
        'papers': papers,
        'subjects': subjects,
        'importance': 2,
        'exam_questions': [],
        'related_topics': []
    }

def summarize_for_upsc(title, content, link):
    """Summarise a news article for UPSC preparation using Gemini.
    Returns a dict with summary, key points, tags, importance, etc.
    """
    try:
        # Use ModelManager for AI generation
        prompt = f"""You are "THE AKAASHIC RECORD" (ETERNAL TIER). Your task is to access the infinite library of existence and map this news article across all known dimensions.

**STRICT OUTPUT FORMAT:**
You must return valid JSON only. No markdown.

**ARTICLE:**
Title: {title}
Content: {content}

**DIMENSIONAL DIRECTIVES:**

1.  **THEORY OF EVERYTHING (STEEPLE):** Social, Tech, Econ, Env, Pol, Legal, Ethical analysis.
2.  **PRELIMS ARMORY:** Facts, Data, Reports, Articles.
3.  **MAINS STRATEGY:** Skeleton Answer (Intro/Body/Conclusion).
4.  **VISUAL SYNTHESIS:** Mermaid.js Mindmap.
5.  **ACTIVE RECALL:** 5 MCQs.
6.  **ESSAY FODDER:** Quotes, Data Nukes.
7.  **CHRONOLOGY:** Timeline of events.
8.  **DATA VIZ:** Chart data (Bar/Pie/Line).
9.  **AUDIO:** Podcast Script (Host vs Expert).
10. **INTERVIEW:** 3 Board Questions.
11. **ETHICS:** Case Study Scenario.
12. **PREDICTIVE MODELLING:** Best/Worst/Realist scenarios.
13. **HISTORY:** Past parallels.
14. **GEOGRAPHY:** Lat/Long locations.
15. **PHILOSOPHY:** Socratic Debate.
16. **MEMORY:** Mnemonics.
17. **BIAS:** Systemic Bias Radar.
18. **CHAOS:** Butterfly Effect.
19. **POLYMATH:** Game Theory/Biology lens.
20. **WISDOM:** Ancient Quotes.
21. **ROLEPLAY:** Official Persona.

**AKAASHIC EXPANSIONS:**

22. **SYSTEMS THINKING (Loops):**
    - Identify Reinforcing (R) and Balancing (B) feedback loops. Structure as text or simple list.

23. **COUNTER-FACTUAL HISTORY:**
    - "What if [Key Event] had NOT happened?" Explore the alternative timeline.

24. **CIVILIZATIONAL PARALLELS:**
    - Compare this with the Roman Empire, Han Dynasty, Gupta Empire, or Ottoman Empire governance.

25. **FERMI ESTIMATION:**
    - Perform a rough back-of-the-envelope calculation of the impact (e.g., Economic loss, Carbon footprint).

26. **GLOBAL MIRROR:**
    - Where else in the world is this EXACT thing happening right now? Compare and contrast.

**JSON SCHEMA:**
{{
  "upsc_summary": "...",
  "prelims_pointers": [],
  "mains_dimensions": [],
  "steeple_analysis": {{}},
  "inter_linkages": [],
  "mind_map": "graph TD; ...",
  "quiz": [{{ "question": "...", "options": [], "answer": "...", "explanation": "..." }}],
  "answer_framework": {{}},
  "essay_fodder": {{}},
  "timeline": [],
  "data_visualization": {{}},
  "podcast_script": "...",
  "interview_questions": [],
  "simulation_scenario": {{}},
  "future_scenarios": {{ "best_case": "...", "worst_case": "...", "realist_case": "..." }},
  "historical_analogies": [{{ "event": "...", "year": "...", "parallel": "..." }}],
  "locations": [{{ "name": "...", "lat": 0.0, "lng": 0.0, "context": "..." }}],
  "socratic_clash": [{{ "speaker": "...", "text": "..." }}],
  "mnemonics": [{{ "phrase": "...", "context": "..." }}],
  "systemic_bias": {{ "political_leaning": "...", "emotional_tone": "...", "fallacies": [] }},
  "butterfly_effect": [{{ "order": "1st", "consequence": "..." }}],
  "polymath_angle": {{ "domain": "...", "analysis": "..." }},
  "quote_injection": {{ "source": "...", "quote": "..." }},
  "roleplay_persona": {{ "role": "...", "task": "..." }},
  "systems_loops": [{{ "type": "Reinforcing", "description": "..." }}],
  "counter_factuals": [{{ "scenario": "...", "outcome": "..." }}],
  "civilizational_parallels": [{{ "empire": "...", "parallel": "..." }}],
  "fermi_estimates": {{ "metric": "...", "calculation": "...", "result": "..." }},
  "global_context": [{{ "country": "...", "issue": "..." }}],
  "papers": ["GS1", "GS2"],
  "subjects": ["Subject 1"],
  "importance": 3,
  "exam_questions": []
}}"""

        # Call ModelManager with 'pro' model for peak performance
        response = model_manager.generate_content(prompt, model_type='pro')
        text = get_gemini_text(response)
        if not text:
            print(f"Empty or blocked response for: {title}")
            return _simple_extraction(title, content)
            
        # Clean possible code fences
        text = text.strip()
        if text.startswith("```"):
            text = text.replace('```json', '').replace('```', '').strip()
            
        start = text.find('{')
        end = text.rfind('}')
        
        if start != -1 and end != -1:
            json_str = text[start : end + 1]
            result = json.loads(json_str)
        else:
            print(f"No JSON found in Gemini response for: {title}")
            return _simple_extraction(title, content)
            
        # result = json.loads(json_str) # Removed duplicate Load
        # Detect generic fallback from Gemini (only GS2 & Current Affairs)
        if result.get('papers') == ['GS2'] and result.get('subjects') == ['Current Affairs']:
            print(f"Generic tags detected for {title}, applying keyword fallback")
            inferred_papers, inferred_subjects = _infer_tags(title, content)
            result['papers'] = inferred_papers
            result['subjects'] = inferred_subjects
        # Validate presence of tags
        if not result.get('papers'):
            print(f"Invalid papers for: {title}, using keyword fallback")
            inferred_papers, _ = _infer_tags(title, content)
            result['papers'] = inferred_papers
        if not result.get('subjects'):
            print(f"Invalid subjects for: {title}, using keyword fallback")
            _, inferred_subjects = _infer_tags(title, content)
            result['subjects'] = inferred_subjects
        # Ensure required keys exist - NO TRUNCATION on fallback
        result.setdefault('importance', 2)
        result.setdefault('exam_questions', [])
        result.setdefault('related_topics', [])
        result.setdefault('upsc_summary', content)  # NO TRUNCATION
        result.setdefault('key_points', [title])
        print(f"✓ Processed: {title[:50]}... → {result['papers']} | {result['subjects']}")
        return result
    except Exception as e:
        print(f"Gemini error for {title}: {e}")
        return _simple_extraction(title, content)

def extract_image_from_article(link):
    """Extract the main image URL from an article.
    Tries Open Graph, Twitter meta, then first <img> tag.
    """
    try:
        import requests
        from bs4 import BeautifulSoup

        # SSRF Check: Validate initial URL
        if not is_safe_url(link):
             print(f"Blocked unsafe URL for image extraction: {link}")
             return None

        # Basic request - no complex redirect logic needed here as it's secondary
        # But for consistency, we should be safe.
        response = requests.get(link, timeout=10, allow_redirects=False)
        if response.is_redirect:
            # Follow one hop if safe
            loc = response.headers.get('Location')
            if loc:
                link = urljoin(link, loc)
                if is_safe_url(link):
                     response = requests.get(link, timeout=10)
                else:
                     return None
            else:
                 return None

        soup = BeautifulSoup(response.content, 'html.parser')
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            return og_image['content']
        twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
        if twitter_image and twitter_image.get('content'):
            return twitter_image['content']
        first_img = soup.find('img')
        if first_img and first_img.get('src'):
            return first_img['src']
        return None
    except Exception as e:
        print(f"Image extraction failed for {link}: {e}")
        return None

def fetch_article_content(url):
    """Fetch full article content from URL with SSRF protection."""
    try:
        import requests
        from bs4 import BeautifulSoup
        
        # SSRF Check: Validate initial URL
        if not is_safe_url(url):
             print(f"Blocked unsafe URL: {url}")
             return ""

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.google.com/'
        }

        # Disable auto-redirects to check each hop
        response = requests.get(url, headers=headers, timeout=15, allow_redirects=False)

        # Handle redirects manually (up to 3 times)
        redirects = 0
        while response.is_redirect and redirects < 3:
            location = response.headers.get('Location')
            if not location:
                break

            next_url = urljoin(url, location)

            if not is_safe_url(next_url):
                print(f"Blocked unsafe redirect to: {next_url}")
                return ""

            url = next_url
            response = requests.get(url, headers=headers, timeout=15, allow_redirects=False)
            redirects += 1

        # If still redirecting after max retries, treat as failed or just take what we have
        if response.is_redirect:
             print(f"Max redirects exceeded for {url}")
             return ""

        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove junk elements
        for element in soup(["script", "style", "nav", "header", "footer", "aside", "form", "iframe", "ads"]):
            element.extract()

        # Specific cleanup for known garbage classes/IDs
        garbage_selectors = [
            '.ad-container', '.advertisement', '.related-articles', '.read-more',
            '.share-buttons', '.social-share', '.comment-section', '.copyright',
            '#bottom-bar', '#cookie-banner', '.newsletter-signup'
        ]
        for selector in garbage_selectors:
            for div in soup.select(selector):
                div.extract()
            
        # Try to find main content based on common classes/ids
        content = None
        
        # The Hindu
        if 'thehindu.com' in url:
            content = soup.find('div', {'id': re.compile(r'content-body-.*')})
            
        # Indian Express
        if not content and 'indianexpress.com' in url:
            content = soup.find('div', class_='story_details') or soup.find('div', class_='full-details')
            
        # PIB (Press Information Bureau)
        if not content and 'pib.gov.in' in url:
            content = soup.find('div', class_='innner-page-main-about-us-content-right-part')

        # Generic fallback: find the element with the most <p> tags
        if not content:
             candidates = soup.find_all('div')
             best_candidate = None
             max_p = 0
             for c in candidates:
                 # Check direct children paragraphs
                 p_count = len(c.find_all('p', recursive=False))
                 # Bonus for long paragraphs (likely content)
                 score = 0
                 for p in c.find_all('p', recursive=False):
                     if len(p.get_text()) > 100:
                         score += 2
                     else:
                         score += 1

                 if score > max_p:
                     max_p = score
                     best_candidate = c
             content = best_candidate

        if content:
            # Clean text
            text = content.get_text(separator=' ', strip=True)
            # Normalize whitespace
            text = re.sub(r'\s+', ' ', text)
        else:
            # Fallback to all paragraphs
            text = ' '.join([p.get_text() for p in soup.find_all('p')])
            text = re.sub(r'\s+', ' ', text)
            
        return text[:20000] # Increased limit for deep analysis
    except Exception as e:
        print(f"Failed to fetch content from {url}: {e}")
        return ""

def find_related_pyqs(subjects, papers):
    """Fetch related previous year questions from the database.
    Returns up to three real PYQs based on subject.
    """
    import sqlite3
    
    # Determine DB path
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(base_dir, 'upsc_saga.db')
    
    related_pyqs = []
    
    # Map AI subjects to DB subjects
    subject_mapping = {
        'Economics': 'Economy',
        'Internal Security': 'Polity & Governance', # Fallback
        'Disaster Management': 'Geography', # Fallback
        'Ethics': 'Polity & Governance' # Fallback or maybe empty
    }
    
    db_subjects = []
    for s in subjects:
        db_subjects.append(subject_mapping.get(s, s))
        
    # Remove duplicates
    db_subjects = list(set(db_subjects))
    
    if not db_subjects:
        return []

    try:
        conn = sqlite3.connect(db_path, timeout=30.0)
        conn.execute('PRAGMA journal_mode=WAL')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        placeholders = ','.join(['?'] * len(db_subjects))
        query = f"""
            SELECT year, subject, question_text as question, topic
            FROM pyq_questions
            WHERE subject IN ({placeholders})
            ORDER BY year DESC
            LIMIT 5
        """
        
        rows = cursor.execute(query, db_subjects).fetchall()
        
        for row in rows:
            related_pyqs.append({
                'year': row['year'],
                'question': row['question'],
                'subject': row['subject'],
                'topic': row['topic']
            })
            
        conn.close()
        
    except Exception as e:
        print(f"Error fetching PYQs: {e}")
        
    return related_pyqs[:3]

def generate_one_liner(title: str, content: str) -> str:
    """Generate a concise one-liner summary for quick revision."""
    prompt = f"""You are an expert UPSC educator. Create a HIGH-YIELD REVISION SUMMARY for this topic.
    
Topic: {title}
Context: {content[:1000] if content else "Generate based on your knowledge of this UPSC topic."}

Requirements:
- Create a dense, information-rich summary (2-3 sentences max).
- Focus on KEYWORDS, FACTS, DATES, and CONSTITUTIONAL ARTICLES relevant to UPSC.
- If the topic is broad, focus on the most examinable aspects.
- Make it punchy and memorable.
- Do not use fluff words.

SUMMARY:"""

    try:
        if not GEMINI_API_KEY:
            print("ERROR: GEMINI_API_KEY not configured in environment")
            return f"⚠️ AI service not configured. Please add GEMINI_API_KEY to backend/.env file."
        
        # model = genai.GenerativeModel('gemini-2.0-flash-001')  # Using stable latest version
        # response = model.generate_content(prompt)
        response = model_manager.generate_content(prompt, model_type='fast')
        one_liner = get_gemini_text(response)
        if not one_liner:
             return "Summary unavailable (Safety Block)"
             
        print(f"Successfully generated one-liner for: {title}")
        return one_liner
    except Exception as e:
        print(f"ERROR generating one-liner for '{title}': {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"⚠️ AI generation failed: {str(e)[:100]}"

def generate_mnemonic(text: str, mnemonic_type: str = "facts") -> str:
    """Generate memory aids (mnemonics) for facts, dates, lists, concepts."""
    
    # Check if Gemini API key is configured
    if not GEMINI_API_KEY:
        return "⚠️ Gemini API Key not configured. Please add GEMINI_API_KEY to your environment variables to use AI-powered mnemonic generation."
    
    type_instructions = {
        "facts": "Create a memorable acronym or phrase to remember key facts",
        "dates": "Create a rhyme or pattern to remember important dates",
        "list": "Create an acronym or story using first letters of list items",
        "concept": "Create an analogy or visual metaphor to understand the concept"
    }
    
    instruction = type_instructions.get(mnemonic_type, type_instructions["facts"])
    
    prompt = f"""You are a creative UPSC memory coach. {instruction}.

Content: {text[:300]}

Requirements:
- Make it MEMORABLE and FUN
- Use vivid imagery or clever wordplay
- Keep it short (2-3 lines max)
- Make it easy to recall under exam pressure
- Be creative but appropriate

MNEMONIC:"""

    try:
        model = None # genai.GenerativeModel('gemini-2.0-flash-001')
        # response = model.generate_content(prompt)
        response = model_manager.generate_content(prompt, model_type='fast')
        mnemonic = get_gemini_text(response)
        if not mnemonic:
            return "Mnemonic unavailable (Safety Block)"
            
        return mnemonic
    except Exception as e:
        print(f"Error generating mnemonic: {e}")
        return f"⚠️ Error generating mnemonic: {str(e)}. Please check your Gemini API configuration."
