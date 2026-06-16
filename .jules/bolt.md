## 2023-11-22 - Refactored N+1 query in weak area analyzer
**Learning:** Found N+1 bottleneck where analyze_all_performance analyzed each topic via separate DB queries and transactions.
**Action:** Replaced O(N) looping with O(1) bulk GROUP BY extraction, local score calculation, and executemany insertion, significantly reducing execution time.
## 2023-11-22 - Avoid package.json modification
**Learning:** Found that modifying package.json to fix duplicate keys violates the "Never do" rule for Bolt and breaks CI.
**Action:** Do not modify package.json or tsconfig.json without explicit instruction, even to fix apparent syntax bugs.
