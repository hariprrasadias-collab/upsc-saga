import re

with open('frontend/src/components/Planning/StudyPlanDashboard.tsx', 'r') as f:
    content = f.read()

# Add useMemo hooks for allSlots and allActiveSlots right after activePlan
insertion_point = content.find('const renderContent = (viewMode: ViewMode) => {')

if insertion_point != -1:
    memoized_slots = """    const allSlots = React.useMemo(() => plan.flatMap(d => d.slots), [plan]);
    const allActiveSlots = React.useMemo(() => activePlan.flatMap(d => d.slots), [activePlan]);

"""
    content = content[:insertion_point] + memoized_slots + content[insertion_point:]

# Replace plan.flatMap(d => d.slots) with allSlots
content = content.replace('plan.flatMap(d => d.slots)', 'allSlots')

# Replace activePlan.flatMap(d => d.slots) with allActiveSlots
content = content.replace('activePlan.flatMap(d => d.slots)', 'allActiveSlots')

# In monthly map, hoist days.flatMap
monthly_regex = re.compile(r'const \{ consistency, phase \} = getMonthlyAnalytics\(days\.flatMap\(d => d\.slots\)\);\s*const subjectCounts: \{ \[key: string\]: number \} = \{\};\s*days\.flatMap\(d => d\.slots\)\.forEach\(s => \{')
monthly_replacement = r'''const monthSlots = days.flatMap(d => d.slots);
                const { consistency, phase } = getMonthlyAnalytics(monthSlots);
                const subjectCounts: { [key: string]: number } = {};
                monthSlots.forEach(s => {'''
content = monthly_regex.sub(monthly_replacement, content)


with open('frontend/src/components/Planning/StudyPlanDashboard.tsx', 'w') as f:
    f.write(content)
