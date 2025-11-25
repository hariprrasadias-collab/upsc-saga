import re

with open('d:/upsc-second-brain/frontend/src/components/DashboardMain.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Add pomodoro timer to header
content = content.replace(
    '        <h1 className="header-title">CHARACTER</h1>\r\n        <div className="runes-decoration" />',
    '        <h1 className="header-title">CHARACTER</h1>\r\n        <div className="pomodoro-header-center"><PomodoroTimer /></div>\r\n        <div className="runes-decoration" />'
)

# Remove old pomodoro timer from center panel 
content = content.replace(
    '          {/* Pomodoro timer positioned above character head */}\r\n          <div className="pomodoro-above-head"><PomodoroTimer /></div>\r\n          ',
    '          '
)

with open('d:/upsc-second-brain/frontend/src/components/DashboardMain.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("File updated successfully!")
