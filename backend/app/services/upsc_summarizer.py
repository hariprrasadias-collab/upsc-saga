# backend/app/services/upsc_summarizer.py
"""
UPSC-focused news summarization using Google Gemini Pro.
Provides a function to summarise an article and infer UPSC paper and subject tags.
If Gemini fails or returns generic tags, a keyword‑based fallback is applied.
"""
import os
import json
import re
import google.generativeai as genai

# Configure Gemini API
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# UPSC Paper and Subject classifications
PAPERS = ['GS1', 'GS2', 'GS3', 'GS4', 'Essay', 'Optional']
SUBJECTS = [
    'Polity & Governance', 'Economics', 'International Relations',
    'Environment & Ecology', 'Science & Technology', 'Internal Security',
    'Disaster Management', 'Social Issues', 'History & Culture',
    'Geography', 'Ethics', 'Current Affairs'
]

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
        'upsc_summary': content[:300] + '...' if len(content) > 300 else content,
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
    if not GEMINI_API_KEY:
        return _simple_extraction(title, content)
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""You are a UPSC expert analyzer. Tag articles accurately based on content.

EXAMPLES OF CORRECT TAGGING:

Example 1:
Title: \"RBI announces new monetary policy rates\"
→ Papers: [\"GS3\"], Subjects: [\"Economics\"]

Example 2:
Title: \"Supreme Court ruling on Right to Privacy\"
→ Papers: [\"GS2\"], Subjects: [\"Polity & Governance\"]

Example 3:
Title: \"India-France defense cooperation agreement\"
→ Papers: [\"GS2\", \"GS3\"], Subjects: [\"International Relations\", \"Internal Security\"]

Example 4:
Title: \"New renewable energy targets announced\"
→ Papers: [\"GS3\"], Subjects: [\"Environment & Ecology\", \"Economics\"]

Example 5:
Title: \"Constitution Bench verdict on federalism\"
→ Papers: [\"GS2\"], Subjects: [\"Polity & Governance\"]

TAGGING RULES:
- GS1: History, Culture, Geography, Society
- GS2: Polity, Governance, IR, Social Justice
- GS3: Economy, Science, Environment, Security
- GS4: Ethics

SUBJECTS:
Polity & Governance | Economics | International Relations | Environment & Ecology | Science & Technology | Internal Security | Disaster Management | Social Issues | History & Culture | Geography | Ethics

NOW TAG THIS ARTICLE:
Title: {title}
Content: {content[:1500]}

Return ONLY this JSON (no markdown, no explanation):
{{"upsc_summary": "...", "key_points": ["...", "..."], "papers": ["GS_"], "subjects": ["..."], "importance": 1-3, "exam_questions": ["..."], "related_topics": ["..."]}}"""
        response = model.generate_content(prompt)
        text = response.text.strip()
        # Clean possible code fences
        text = text.replace('```json', '').replace('```', '').strip()
        start = text.find('{')
        end = text.rfind('}') + 1
        if start == -1 or end == 0:
            print(f"No JSON found in Gemini response for: {title}")
            return _simple_extraction(title, content)
        json_str = text[start:end]
        result = json.loads(json_str)
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
        # Ensure required keys exist
        result.setdefault('importance', 2)
        result.setdefault('exam_questions', [])
        result.setdefault('related_topics', [])
        result.setdefault('upsc_summary', content[:300] + '...' if len(content) > 300 else content)
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
        response = requests.get(link, timeout=10)
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

def find_related_pyqs(subjects, papers):
    """Placeholder for fetching related previous year questions.
    Returns up to three mock PYQs based on subject.
    """
    pyq_database = {
        'Polity & Governance': [
            {'year': 2023, 'paper': 'GS2', 'question': 'Discuss the role of Governor in state administration.'},
            {'year': 2022, 'paper': 'GS2', 'question': 'What is the significance of 73rd and 74th amendments?'}
        ],
        'Economics': [
            {'year': 2023, 'paper': 'GS3', 'question': 'Analyze the impact of GST on Indian economy.'},
            {'year': 2022, 'paper': 'GS3', 'question': 'Discuss the challenges in agricultural marketing.'}
        ]
    }
    related_pyqs = []
    for subject in subjects:
        if subject in pyq_database:
            related_pyqs.extend(pyq_database[subject][:2])
    return related_pyqs[:3]
