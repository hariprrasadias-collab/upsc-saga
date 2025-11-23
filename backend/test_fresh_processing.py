# Test with fresh article processing
import requests
import json

print("Clearing database and testing with fresh articles...\n")

# Process 3 diverse articles
test_articles = [
    {
        "title": "RBI keeps repo rate unchanged at 6.5%",
        "link": "http://test1.com",
        "source": "Test",
        "published": "2025-01-23",
        "summary": "The Reserve Bank of India's Monetary Policy Committee decided to keep the repo rate unchanged at 6.5% citing inflationary concerns and growth stability."
    },
    {
        "title": "Supreme Court verdict on Article 370 constitutional validity",
        "link": "http://test2.com",
        "source": "Test",
        "published": "2025-01-23",
        "summary": "The Supreme Court delivered a landmark judgment upholding the constitutional validity of the abrogation of Article 370 in Jammu and Kashmir."
    },
    {
        "title": "India launches Green Hydrogen Mission with Rs 19,000 crore allocation",
        "link": "http://test3.com",
        "source": "Test",
        "published": "2025-01-23",
        "summary": "The government announced the National Green Hydrogen Mission with an outlay of Rs 19,000 crore to promote clean energy and achieve net-zero emissions by 2070."
    }
]

for i, article in enumerate(test_articles, 1):
    print(f"\n{i}. Processing: {article['title']}")
    print("-" * 60)
    
    try:
        response = requests.post('http://localhost:5000/api/ravens/process', json=article)
        if response.status_code == 200:
            result = response.json()
            data = result.get('data', {})
            print(f"✓ SUCCESS")
            print(f"  Papers: {data.get('papers', [])}")
            print(f"  Subjects: {data.get('subjects', [])}")
            print(f"  Importance: {data.get('importance', 'N/A')}")
        else:
            print(f"✗ FAILED: {response.status_code}")
            print(f"  Response: {response.text[:200]}")
    except Exception as e:
        print(f"✗ ERROR: {e}")

print("\n" + "=" * 60)
print("Fetching all saved articles...")
print("=" * 60)

try:
    response = requests.get('http://localhost:5000/api/ravens/saved')
    if response.status_code == 200:
        articles = response.json()
        print(f"\nTotal articles in DB: {len(articles)}\n")
        for article in articles:
            print(f"Title: {article['title'][:50]}...")
            print(f"  Papers: {article.get('papers', [])}")
            print(f"  Subjects: {article.get('subjects', [])}")
            print()
    else:
        print(f"Failed to fetch: {response.status_code}")
except Exception as e:
    print(f"Error: {e}")
