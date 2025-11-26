#!/usr/bin/env python3
"""
Backend API Test Suite
Tests all major API endpoints and generates comprehensive report
"""

import requests
import json
from datetime import datetime
from collections import defaultdict

BASE_URL = "http://localhost:5000"
results = []

def test_api(method, endpoint, body=None, test_name="", expected_status=200):
    """Test a single API endpoint"""
    print(f"\n{'='*60}")
    print(f"Testing: {test_name}")
    print(f"Method: {method} | Endpoint: {endpoint}")
    
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=body, timeout=5)
        elif method == "PUT":
            response = requests.put(url, json=body, timeout=5)
        elif method == "DELETE":
            response = requests.delete(url, timeout=5)
        
        success = response.status_code == expected_status
        status_symbol = "✓ PASS" if success else "✗ FAIL"
        
        print(f"{status_symbol} - Status: {response.status_code}")
        
        try:
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2)[:500]}")
        except:
            print(f"Response: {response.text[:200]}")
        
        results.append({
            "test": test_name,
            "method": method,
            "endpoint": endpoint,
            "status": "PASS" if success else "FAIL",
            "status_code": response.status_code,
            "response": response.text[:500]
        })
        
        return response
        
    except Exception as e:
        print(f"✗ FAIL - Error: {str(e)}")
        results.append({
            "test": test_name,
            "method": method,
            "endpoint": endpoint,
            "status": "FAIL",
            "error": str(e)
        })
        return None

def print_header(title):
    """Print section header"""
    print(f"\n\n{'╔'+'═'*60+'╗'}")
    print(f"║{title:^60}║")
    print(f"{'╚'+'═'*60+'╝'}")

# ===== ANALYTICS APIs =====
print_header("ANALYTICS API TESTS")
test_api("GET", "/api/analytics/overview?timeframe=all", test_name="TC-API-014: Get analytics overview")
test_api("GET", "/api/analytics/overview?timeframe=week", test_name="TC-API-014b: Get weekly analytics")
test_api("GET", "/api/analytics/subject/Polity", test_name="TC-API-015: Get subject analytics (valid)")
test_api("GET", "/api/analytics/subject/InvalidSubject", test_name="TC-API-015b: Get subject analytics (invalid)")

# ===== SYLLABUS APIs =====
print_header("SYLLABUS API TESTS")
test_api("GET", "/api/syllabus/", test_name="TC-API-016: Get all syllabus topics")
test_api("GET", "/api/syllabus/analytics", test_name="TC-API-016b: Get syllabus analytics")
test_api("POST", "/api/syllabus/1/status", {"status": "Reading"}, test_name="TC-API-017: Update topic status")
test_api("POST", "/api/syllabus/1/notes", {"notes": "Test notes"}, test_name="TC-API-018: Save topic notes")
test_api("POST", "/api/syllabus/1/revise", test_name="TC-API-018b: Mark topic as revised")

# ===== WAR MAP APIs =====
print_header("WAR MAP API TESTS")
today = datetime.now().strftime("%Y-%m-%d")
test_api("GET", f"/api/warmap/tasks?date={today}", test_name="TC-API-003: Get tasks for today")
test_api("GET", "/api/warmap/status", test_name="TC-API-006b: Get Google Calendar status")
test_api("POST", "/api/warmap/tasks", {
    "title": "Test Task from API",
    "description": "Testing task creation",
    "date": today,
    "completed": False
}, test_name="TC-API-004: Create new task (positive)")
test_api("POST", "/api/warmap/tasks", {
    "description": "Task without title",
    "date": today
}, test_name="TC-API-005: Create task without title (negative)", expected_status=400)

# ===== RAVENS APIs =====
print_header("RAVENS API TESTS")
test_api("GET", "/api/ravens/articles", test_name="TC-API-009: Get articles list")

# ===== ARENA APIs =====
print_header("ARENA API TESTS")
test_api("GET", "/api/arena/bosses", test_name="TC-API-011: Get all bosses")
test_api("GET", "/api/arena/bosses/year", test_name="TC-API-011b: Get year bosses")
test_api("GET", "/api/arena/bosses/subject", test_name="TC-API-011c: Get subject bosses")
test_api("GET", "/api/arena/bosses/custom", test_name="TC-API-011d: Get custom bosses")

# ===== FLASHCARD APIs =====
print_header("FLASHCARD API TESTS")
test_api("GET", "/api/flashcards/decks", test_name="TC-API-019b: Get all decks")
test_api("POST", "/api/flashcards/decks", {"name": "Test Deck API"}, test_name="TC-API-019: Create new deck (positive)")
test_api("POST", "/api/flashcards/decks", {"name": ""}, test_name="TC-API-019c: Create deck without name (negative)", expected_status=400)

# ===== REVISION APIs =====
print_header("REVISION API TESTS")
test_api("GET", "/api/revision/cards", test_name="TC-API-023: Get all revision cards")
test_api("POST", "/api/revision/one-liner", {
    "title": "Preamble of Indian Constitution",
    "content": "The Constitution soul"
}, test_name="TC-API-022: Generate revision card (positive)")
test_api("POST", "/api/revision/one-liner", {
    "content": "Content without title"
}, test_name="TC-API-022b: Generate card without title (negative)", expected_status=400)

# ===== SUMMARY =====
print_header("TEST SUMMARY")

total = len(results)
passed = sum(1 for r in results if r["status"] == "PASS")
failed = total - passed
pass_rate = (passed / total * 100) if total > 0 else 0

print(f"\nTotal Tests: {total}")
print(f"Passed: {passed} ✓")
print(f"Failed: {failed} ✗")
print(f"Pass Rate: {pass_rate:.2f}%")

# Group failures by category
failures_by_category = defaultdict(list)
for result in results:
    if result["status"] == "FAIL":
        category = result["test"].split(":")[0]  # Get TC-API-XXX part
        failures_by_category[category].append(result["test"])

if failures_by_category:
    print("\n\nFailed Tests by Category:")
    for category, tests in failures_by_category.items():
        print(f"\n{category}:")
        for test in tests:
            print(f"  - {test}")

# Save detailed results
with open("api_test_results.json", "w") as f:
    json.dump({
        "summary": {
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": pass_rate,
            "timestamp": datetime.now().isoformat()
        },
        "results": results
    }, f, indent=2)

print(f"\n\nDetailed results saved to: api_test_results.json")
