import sys

# Read the original file
with open('app/services/upsc_summarizer.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Append the two new functions
new_functions = '''
def generate_one_liner(title: str, content: str) -> str:
    """Generate a concise one-liner summary for quick revision."""
    prompt = f"""You are an expert UPSC educator. Create a ONE-LINE summary for quick revision.

Topic: {title}
Content: {content[:500]}

Requirements:
- MUST be exactly ONE sentence (40-50 words max)
- Capture the MOST IMPORTANT concept/fact
- Use active voice and clear language
- Include key dates/names if relevant
- Make it memorable and easy to recall

ONE-LINER:"""

    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        one_liner = response.text.strip()
        return one_liner
    except Exception as e:
        print(f"Error generating one-liner: {e}")
        return f"Quick Summary: {title}"

def generate_mnemonic(text: str, mnemonic_type: str = "facts") -> str:
    """Generate memory aids (mnemonics) for facts, dates, lists, concepts."""
    type_instructions = {
        "facts": "Create a memorable acronym or phrase to remember key facts",
        "dates": "Create a rhyme or pattern to remember important dates",
        "list": "Create an acronym or story using first letters of list items",
        "concept": "Create an analogy or visual metaphor to understand the concept"
    }
    
    instruction = type_instructions.get(mnemonic_type, type_instructions["facts"])
    
    prompt = f"""You are a creative UPSC memory coach. {instruction}.

Content: {text[:300]}

Requirements:
- Make it MEMORABLE and FUN
- Use vivid imagery or clever wordplay
- Keep it short (2-3 lines max)
- Make it easy to recall under exam pressure
- Be creative but appropriate

MNEMONIC:"""

    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        mnemonic = response.text.strip()
        return mnemonic
    except Exception as e:
        print(f"Error generating mnemonic: {e}")
        return "Memory aid could not be generated"
'''

# Write the updated content
with open('app/services/upsc_summarizer.py', 'w', encoding='utf-8') as f:
    f.write(content + new_functions)

print("✅ Successfully added generate_one_liner and generate_mnemonic functions")
