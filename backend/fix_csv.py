import re
import os

csv_path = r'd:\upsc-second-brain\frontend\public\UPSC_Prelims_2024_2022_GS1_Complete.csv'
temp_path = csv_path + '.tmp'

def is_start_of_row(line):
    # Check if line starts with a year like 2020, 2021, etc.
    return re.match(r'^20\d\d,', line) or line.startswith('year,')

def fix_csv():
    print(f"Repairing {csv_path}...")
    with open(csv_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    fixed_lines = []
    current_line = ""

    for line in lines:
        line = line.strip('\n') # Remove newline char
        if not line.strip(): continue # Skip empty lines

        if is_start_of_row(line):
            if current_line:
                fixed_lines.append(current_line)
            current_line = line
        else:
            # It's a continuation of the previous line
            current_line += " " + line

    # Append the last line
    if current_line:
        fixed_lines.append(current_line)

    with open(temp_path, 'w', encoding='utf-8') as f:
        for line in fixed_lines:
            f.write(line + '\n')

    print(f"Fixed {len(lines)} lines into {len(fixed_lines)} rows.")
    
    # Backup original
    os.replace(csv_path, csv_path + '.bak')
    # Move temp to original
    os.replace(temp_path, csv_path)
    print("Repair complete.")

if __name__ == '__main__':
    fix_csv()
