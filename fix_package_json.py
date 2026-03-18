import json

try:
    with open('package.json', 'r') as f:
        data = f.read()

    # We see it has duplicate "scripts" keys
    # Let's fix it by parsing it carefully or just replacing it
    new_data = '''{
  "devDependencies": {
    "terser": "^5.44.1"
  },
  "scripts": {
    "build": "cd frontend && pnpm install --frozen-lockfile && npm run build && cd .. && rm -rf dist && cp -r frontend/dist dist"
  }
}'''
    with open('package.json', 'w') as f:
        f.write(new_data)

    print("Fixed package.json")
except Exception as e:
    print(f"Error: {e}")
