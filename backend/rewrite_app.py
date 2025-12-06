import os

file_path = r'd:\upsc-second-brain\frontend\src\App.tsx'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Line numbers are 1-indexed in view_file, so we adjust for 0-indexed list
# Remove 76-86 (indices 75-86)
# Remove 93-104 (indices 92-104)

# We need to be careful with indices shifting.
# We'll construct the new list of lines.

new_lines = []

# Keep 1-75 (indices 0-74)
new_lines.extend(lines[0:75])

# Skip 76-86 (indices 75-85) -> 11 lines
# Check if we are skipping the right thing
print(f"Skipping block 1 starting with: {lines[75]}")

# Keep 87-92 (indices 86-91)
new_lines.extend(lines[86:92])

# Skip 93-104 (indices 92-103) -> 12 lines
print(f"Skipping block 2 starting with: {lines[92]}")

# Keep 105-end (indices 104-end)
new_lines.extend(lines[104:])

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("App.tsx rewritten.")
