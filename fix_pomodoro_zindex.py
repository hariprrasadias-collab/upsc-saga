import re

# Read the CSS file
with open('frontend/src/components/DashboardMain.css', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace z-index: 10 in pomodoro-header-center with z-index: 100000
content = re.sub(
    r'(\.pomodoro-header-center\s*\{[^}]*z-index:\s*)10(;)',
    r'\g<1>100000\g<2>',
    content
)

# Replace z-index: 9999 in pomodoro-widget with z-index: 100001
content = re.sub(
    r'(\.pomodoro-header-center\s+\.pomodoro-widget\s*\{[^}]*z-index:\s*)9999(;)',
    r'\g<1>100001\g<2>',
    content
)

# Write back
with open('frontend/src/components/DashboardMain.css', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated z-index values successfully!")
print("- pomodoro-header-center: z-index 10 -> 100000")
print("- pomodoro-widget: z-index 9999 -> 100001")
