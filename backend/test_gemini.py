# Test Gemini API directly
import os
os.environ['GEMINI_API_KEY'] = 'AIzaSyAmr9F5ia-DXkW2GeAqhtorXvCRYoClUpo'

from app.services.upsc_summarizer import summarize_for_upsc

# Test article
title = "India and US discuss trade partnership"
content = "India and the United States held extensive discussions on strengthening bilateral trade relations. The talks focused on reducing tariffs, increasing market access, and promoting investments in key sectors including technology and renewable energy."

print("Testing Gemini API...")
print(f"Title: {title}")
print(f"Content: {content[:100]}...\n")

result = summarize_for_upsc(title, content, "http://test.com")

print("\n=== RESULT ===")
print(f"Papers: {result['papers']}")
print(f"Subjects: {result['subjects']}")
print(f"Summary: {result['upsc_summary'][:100]}...")
print(f"Key Points: {result['key_points'][:2]}")
print(f"Importance: {result['importance']}")
