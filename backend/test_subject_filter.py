from app.services.pyq_analytics import analyze_pyq_distribution

# Test without filter
result_all = analyze_pyq_distribution()
print(f"Total questions (no filter): {result_all['stats']['total_questions']}")

# Test with subject filter
result_history = analyze_pyq_distribution(subject='History')
print(f"Total questions (History filter): {result_history['stats']['total_questions']}")

# Test with Geography
result_geo = analyze_pyq_distribution(subject='Geography')
print(f"Total questions (Geography filter): {result_geo['stats']['total_questions']}")

print("\nSubject filter is working!" if result_history['stats']['total_questions'] < result_all['stats']['total_questions'] else "Subject filter may not be working")
