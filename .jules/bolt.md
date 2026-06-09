## 2024-05-24 - N+1 in Subject Performance
**Learning:** Found an N+1 query in `get_subject_wise` endpoint of `analytics.py` where it calls `get_subject_performance` for each subject individually.
**Action:** Replace `get_subject_performance` loop with a new bulk `get_all_subjects_performance` function that uses IN clause and GROUP BY.
