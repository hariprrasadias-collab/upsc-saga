import re

files_to_check = [
    "frontend/src/components/MindPalace/MindPalace.tsx",
    "frontend/src/components/PomodoroTimer/PomodoroTimer.tsx",
    "frontend/src/components/Mimir/Mimir.tsx"
]

def process_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Use re.DOTALL in case attributes wrap across lines, though here they likely don't
    pattern = re.compile(r'<button(.*?)>([✕×])</button>', re.DOTALL)

    def replacer(match):
        attributes = match.group(1)
        icon = match.group(2)

        # If it already has aria-label, skip adding it
        if "aria-label=" not in attributes:
            new_attrs = f'{attributes} aria-label="Close"'
        else:
            new_attrs = attributes

        return f'<button{new_attrs}><span aria-hidden="true">{icon}</span></button>'

    new_content = pattern.sub(replacer, content)

    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {file_path}")
    else:
        print(f"No changes in {file_path}")

for f in files_to_check:
    process_file(f)
