from app.services.pyq_analytics import analyze_pyq_distribution

# Test the actual API filters
print("Testing PYQ Analytics Filters:\n")

# 1. Test without any filters
all_data = analyze_pyq_distribution()
print(f"1. No filters: {all_data['stats']['total_questions']} questions")

# 2. Test subject filter
history_data = analyze_pyq_distribution(subject='History')
print(f"2. Subject=History: {history_data['stats']['total_questions']} questions")

# 3. Test paper filter (this might fail if column doesn't exist)
try:
    gs1_data = analyze_pyq_distribution(paper='GS1')
    print(f"3. Paper=GS1: {gs1_data['stats']['total_questions']} questions")
except Exception as e:
    print(f"3. Paper filter ERROR: {e}")

# 4. Test year range
year_data = analyze_pyq_distribution(year_start=2020, year_end=2022)
print(f"4. Years 2020-2022: {year_data['stats']['total_questions']} questions")

# 5. Test combined filters
combined_data = analyze_pyq_distribution(subject='Polity', year_start=2020)
print(f"5. Subject=Polity + Year>=2020: {combined_data['stats']['total_questions']} questions")

print("\n✓ All working filters tested!")
