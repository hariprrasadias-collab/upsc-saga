import requests
import json

# Fetch one article from the API
response = requests.get('http://localhost:5000/api/ravens/saved')
articles = response.json()

if articles:
    print("=" * 80)
    print("SAMPLE ARTICLE FROM DATABASE")
    print("=" * 80)
    article = articles[0]
    print(f"\nTitle: {article['title']}")
    print(f"\nSource: {article['source']}")
    print(f"\nPublished: {article['published']}")
    print(f"\nUpsc Summary Length: {len(article.get('upscSummary', ''))}")
    print(f"\nUpsc Summary:\n{article.get('upscSummary', 'N/A')}")
    print(f"\n\nKey Points: {json.dumps(article.get('keyPoints', []), indent=2)}")
    print(f"\n\nPapers: {article.get('papers', [])}")
    print(f"Subjects: {article.get('subjects', [])}")
    print("\n" + "=" * 80)
else:
    print("No articles found")
