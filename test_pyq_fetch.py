import sys
import os

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from app.services.upsc_summarizer import find_related_pyqs

print("Testing find_related_pyqs...")

# Test 1: Economy (Mapped from Economics)
print("\nTest 1: Economics")
pyqs = find_related_pyqs(['Economics'], ['GS3'])
for q in pyqs:
    print(f"- [{q['year']}] {q['question'][:50]}... ({q['subject']})")

# Test 2: Polity & Governance (Direct match)
print("\nTest 2: Polity & Governance")
pyqs = find_related_pyqs(['Polity & Governance'], ['GS2'])
for q in pyqs:
    print(f"- [{q['year']}] {q['question'][:50]}... ({q['subject']})")

# Test 3: Non-existent subject
print("\nTest 3: Random Subject")
pyqs = find_related_pyqs(['Random Subject'], ['GS1'])
print(f"Found {len(pyqs)} questions")
