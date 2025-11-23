# Comprehensive test of Ravens system
import requests
import json

BASE_URL = "http://localhost:5000/api/ravens"

print("=" * 60)
print("TESTING RAVENS CURRENT AFFAIRS SYSTEM")
print("=" * 60)

# Test 1: Fetch live news
print("\n1. Testing live news fetch...")
try:
    response = requests.get(f"{BASE_URL}?type=munin")
    if response.status_code == 200:
        news = response.json()
        print(f"✓ Fetched {len(news)} articles from MUNIN")
        if news:
            print(f"  Sample: {news[0]['title'][:60]}...")
    else:
        print(f"✗ Failed: {response.status_code}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 2: Process a sample article
print("\n2. Testing AI processing...")
sample_article = {
    "title": "Government launches new renewable energy policy",
    "link": "http://example.com",
    "source": "Test Source",
    "published": "2025-01-23",
    "summary": "The government has announced a comprehensive renewable energy policy aimed at achieving net-zero emissions by 2070. The policy includes incentives for solar and wind energy projects, focusing on rural electrification and sustainable development."
}

try:
    response = requests.post(f"{BASE_URL}/process", json=sample_article)
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Article processed successfully")
        print(f"  Papers: {result['data']['papers']}")
        print(f"  Subjects: {result['data']['subjects']}")
        print(f"  Importance: {result['data']['importance']}")
        article_id = result['article_id']
    else:
        print(f"✗ Failed: {response.status_code} - {response.text}")
        article_id = None
except Exception as e:
    print(f"✗ Error: {e}")
    article_id = None

# Test 3: Retrieve saved articles
print("\n3. Testing saved articles retrieval...")
try:
    response = requests.get(f"{BASE_URL}/saved")
    if response.status_code == 200:
        articles = response.json()
        print(f"✓ Retrieved {len(articles)} saved articles")
        if articles:
            print(f"  Latest: {articles[0]['title'][:60]}...")
            print(f"  Tags: {articles[0]['papers']} | {articles[0]['subjects']}")
    else:
        print(f"✗ Failed: {response.status_code}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 4: Filter by GS Paper
print("\n4. Testing filter by GS3...")
try:
    response = requests.get(f"{BASE_URL}/saved?paper=GS3")
    if response.status_code == 200:
        articles = response.json()
        print(f"✓ Found {len(articles)} GS3 articles")
    else:
        print(f"✗ Failed: {response.status_code}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 5: Update importance
if article_id:
    print(f"\n5. Testing importance update for article {article_id}...")
    try:
        response = requests.put(f"{BASE_URL}/{article_id}/importance", 
                               json={"importance": 3})
        if response.status_code == 200:
            print(f"✓ Importance updated to High")
        else:
            print(f"✗ Failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {e}")

print("\n" + "=" * 60)
print("TEST SUMMARY COMPLETE")
print("=" * 60)
