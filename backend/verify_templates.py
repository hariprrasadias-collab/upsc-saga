import requests

def test_templates():
    print("Testing Answer Templates API...\n")
    
    # Test 1: List all templates
    print("1. Fetching all templates...")
    response = requests.get('http://localhost:5000/api/templates/list')
    
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            print(f"✅ Success! Found {len(data['templates'])} templates")
            for template in data['templates']:
                print(f"   • {template['name']}: {template['description']}")
        else:
            print("❌ API returned success=False")
    else:
        print(f"❌ HTTP Error: {response.status_code}")
    
    print("\n2. Fetching specific template (examine)...")
    response = requests.get('http://localhost:5000/api/templates/examine')
    
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            template = data['template']
            print(f"✅ Success! Template: {template['name']}")
            print(f"   Word Count: {template['wordCount']}")
            print(f"   Tips: {len(template['tips'])} tips")
            print(f"   Structure: {len(template['structure'])} sections")
        else:
            print("❌ API returned success=False")
    else:
        print(f"❌ HTTP Error: {response.status_code}")

if __name__ == "__main__":
    test_templates()
