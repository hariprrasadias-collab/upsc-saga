import os
import re

def fix_localhost_in_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(('.tsx', '.ts')) and file != 'config.ts':
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                if 'localhost:5000' not in content:
                    continue

                # Calculate depth to config
                # e.g., if we are in frontend/src/components/Revision, depth is 2 (../../config)
                # directory is 'frontend/src/components'
                rel_path = os.path.relpath(filepath, directory)
                depth = rel_path.count(os.sep) + 1
                import_path = '../' * depth + 'config'
                
                new_content = content
                
                # Replace 'http://localhost:5000/api...' with `${API_BASE_URL}/api...`
                # Using regex to capture the full string
                # Case 1: 'http://localhost:5000/api/endpoint'
                new_content = re.sub(r"'http://localhost:5000(.*?)'", r"`${API_BASE_URL}\1`", new_content)
                
                # Case 2: `http://localhost:5000/api/${id}`
                new_content = re.sub(r"`http://localhost:5000(.*?)`", r"`${API_BASE_URL}\1`", new_content)

                # Ensure import is present if we replaced something
                if new_content != content:
                    if "import { API_BASE_URL } from" not in new_content:
                        # Find the last import statement or just add to top
                        import_stmt = f"import {{ API_BASE_URL }} from '{import_path}';\n"
                        # just add at line 2 after first line
                        lines = new_content.split('\n')
                        lines.insert(0, import_stmt)
                        new_content = '\n'.join(lines)

                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Fixed {filepath}")

if __name__ == '__main__':
    fix_localhost_in_files('frontend/src/contexts')
    fix_localhost_in_files('frontend/src/services')
