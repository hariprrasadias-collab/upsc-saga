import os

file_path = r'd:\upsc-second-brain\frontend\src\App.tsx'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for line in lines:
    # Check for start of first block
    if "fetch('/api/ravens/background-fetch', { method: 'POST' })" in line and "useEffect" in lines[lines.index(line)-1]:
        # We found the inner part, but we need to remove the surrounding useEffect
        # This simple logic might be tricky.
        pass
    
    # Let's use a more robust way: filter out the specific blocks based on content
    
    # Block 1 signature
    if "fetch('/api/ravens/background-fetch'" in line:
        continue
    
    # Block 2 signature
    if "Trigger background news fetch on app load" in line:
        continue
    if "triggerRavens = async () =>" in line:
        continue
    if "await fetch('http://localhost:5000/api/ravens/background-fetch'" in line:
        continue
    if "🦅 Ravens dispatched" in line:
        continue
    if "🦅 Failed to dispatch" in line:
        continue
        
    new_lines.append(line)

# This is too messy. Let's just read the whole content and replace the strings.
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

block1 = """  useEffect(() => {
    fetch('/api/ravens/background-fetch', { method: 'POST' })
      .then(response => {
        if (!response.ok) {
          console.error('Failed to start background fetch');
        } else {
          console.log('Background fetch for Ravens initiated.');
        }
      })
      .catch(error => console.error('Error starting background fetch:', error));
  }, []);"""

block2 = """  // Trigger background news fetch on app load
  useEffect(() => {
    const triggerRavens = async () => {
      try {
        await fetch('http://localhost:5000/api/ravens/background-fetch', { method: 'POST' });
        console.log("🦅 Ravens dispatched for background scouting.");
      } catch (err) {
        console.error("🦅 Failed to dispatch Ravens:", err);
      }
    };
    triggerRavens();
  }, []);"""

# Normalize line endings just in case
content = content.replace(block1, "")
content = content.replace(block2, "")

# Also try with different newlines if it failed
if block1 in content:
    print("Block 1 found and removed.")
else:
    print("Block 1 NOT found.")
    # Try to find it loosely? No, let's just print what we have
    
if block2 in content:
    print("Block 2 found and removed.")
else:
    print("Block 2 NOT found.")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Finished processing App.tsx")
