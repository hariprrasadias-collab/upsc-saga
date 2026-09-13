import re

with open('frontend/src/components/Planning/StudyPlanDashboard.tsx', 'r') as f:
    content = f.read()

# Hoist allSlots out of the render loop and wrap in useMemo
insertion_point = content.find('const getWeeklyAnalytics')

if insertion_point != -1:
    memoized_slots = """    const allSlots = React.useMemo(() => plan.flatMap(d => d.slots), [plan]);
    const allActiveSlots = React.useMemo(() => activePlan.flatMap(d => d.slots), [activePlan]);

"""
    content = content[:insertion_point] + memoized_slots + content[insertion_point:]

content = content.replace('plan.flatMap(d => d.slots)', 'allSlots')
content = content.replace('activePlan.flatMap(d => d.slots)', 'allActiveSlots')

# In monthly map, hoist days.flatMap
monthly_regex = re.compile(r'const \{ consistency, phase \} = getMonthlyAnalytics\(days\.flatMap\(d => d\.slots\)\);\s*const subjectCounts: \{ \[key: string\]: number \} = \{\};\s*days\.flatMap\(d => d\.slots\)\.forEach\(s => \{')
monthly_replacement = r'''const monthSlots = days.flatMap(d => d.slots);
                const { consistency, phase } = getMonthlyAnalytics(monthSlots);
                const subjectCounts: { [key: string]: number } = {};
                monthSlots.forEach(s => {'''
content = monthly_regex.sub(monthly_replacement, content)

# But wait! 'plan.flatMap(d => d.slots)' was used inside useEffect where activePlan might not be defined or allSlots might be stale? No, allSlots is derived from plan, so it updates when plan updates. BUT we can't use allSlots inside useEffect unless we include it in the dependency array.
# Alternatively, I can just leave StudyPlanDashboard alone and optimize CommandPalette! It's much simpler and less risky to break logic.
