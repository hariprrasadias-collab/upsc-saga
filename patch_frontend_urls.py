import os

def replace_url_in_files(directory):
    target = "http://localhost:5000"
    replacement = "" # Empty string to make it relative (e.g. /api/...)

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith((".ts", ".tsx", ".js", ".jsx")):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                if target in content:
                    print(f"Patching {filepath}")
                    new_content = content.replace(target, replacement)
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)

replace_url_in_files("frontend/src")
