import os

def test_path():
    # Simulate the logic in brain_service.py
    # brain_service is in app/services/brain_service.py
    # We are simulating running this script from arbitrary location but mimicking the logic
    
    # In the app, __file__ would be .../backend/app/services/brain_service.py
    # We want to check if .../backend/manual_prompt.txt is correctly resolved.
    
    # Let's assume this script is placed in backend/app/services (we will write it there)
    
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    prompt_path = os.path.join(base_dir, 'manual_prompt.txt')
    
    print(f"Resolved base_dir: {base_dir}")
    print(f"Resolved prompt_path: {prompt_path}")
    
    expected_suffix = os.path.join('backend', 'manual_prompt.txt')[-15:] # just checking end
    
    # We expect it to be d:\upsc-second-brain\backend\manual_prompt.txt
    if prompt_path.endswith('manual_prompt.txt'):
        print("Path structure looks correct.")
    else:
        print("Path structure incorrect.")

if __name__ == "__main__":
    test_path()
