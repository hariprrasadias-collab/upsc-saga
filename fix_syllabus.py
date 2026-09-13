import re

with open('frontend/src/components/Syllabus/SyllabusTracker.tsx', 'r') as f:
    content = f.read()

# Instead of recalculating getProgress inside the render method 12 times!
# Let's wrap getProgress with useCallback so it doesn't get re-created every render,
# OR memoize the paper progress data.

memoized_progress = """    const progressByPaper = useMemo(() => {
        if (!analytics) return {};
        const progress: Record<string, number> = {};
        ['Prelims', 'GS1', 'GS2', 'GS3', 'GS4', 'Optional'].forEach(paper => {
            const total = analytics.totals.find(t => t.paper === paper)?.total || 0;
            if (total === 0) {
                progress[paper] = 0;
                return;
            }
            const completed = analytics.breakdown
                .filter(b => b.paper === paper && b.status === 'Completed')
                .reduce((acc, curr) => acc + curr.count, 0);
            progress[paper] = Math.round((completed / total) * 100);
        });
        return progress;
    }, [analytics]);

    const getProgress = useCallback((paper: string) => {
        return progressByPaper[paper] || 0;
    }, [progressByPaper]);"""

content = re.sub(r'const getProgress = \(paper: string\) => \{.*?return Math\.round\(\(completed / total\) \* 100\);\s*\};', memoized_progress, content, flags=re.DOTALL)

if 'useCallback' not in content:
    content = content.replace("import React, { useState, useEffect, useMemo } from 'react';", "import React, { useState, useEffect, useMemo, useCallback } from 'react';")

with open('frontend/src/components/Syllabus/SyllabusTracker.tsx', 'w') as f:
    f.write(content)
