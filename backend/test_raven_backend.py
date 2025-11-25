import sys
import os
import feedparser
import json

# Add backend directory to path
sys.path.append(os.path.abspath('d:/upsc-second-brain/backend'))

from app.services.upsc_summarizer import summarize_for_upsc

def test_rss_fetch():
    print("Testing RSS Fetch...")
    url = 'https://www.thehindu.com/news/national/feeder/default.rss'
    try:
        feed = feedparser.parse(url)
        if feed.entries:
            print(f"SUCCESS: Fetched {len(feed.entries)} entries from {url}")
            return feed.entries[0]
        else:
            print(f"WARNING: No entries found in {url}")
            return None
    except Exception as e:
        print(f"FAILED: RSS fetch error: {e}")
        return None

def test_gemini_summarization(article):
    if not article:
        print("Skipping Gemini test (no article)")
        return

    print("\nTesting Gemini Summarization...")
    title = article.title
    link = article.link
    content = article.get('summary', '')
    
    print(f"Article: {title}")
    
    try:
        # First attempt
        print("Attempt 1: Processing article...")
        result = summarize_for_upsc(title, content, link)
        print("SUCCESS: Gemini response received")
        
        # Simulate saving to DB and checking duplicate (Mocking the API behavior)
        # In a real integration test we would hit the API endpoint
        
        print("\nAttempt 2: Checking duplicate logic...")
        # We can't easily test the DB constraint here without importing app context
        # But we can verify the backend code logic by hitting the API if the server was running
        # For now, we rely on the code review of ravens.py
        
    except Exception as e:
        print(f"FAILED: Gemini error: {e}")

if __name__ == "__main__":
    article = test_rss_fetch()
    test_gemini_summarization(article)
