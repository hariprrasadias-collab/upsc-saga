import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app import create_app
from app.services.night_watchman import night_watchman

app = create_app()

mock_articles = [
    {
        'title': 'Supreme Court strikes down Electoral Bonds Scheme',
        'source': 'The Hindu',
        'summary': 'The Supreme Court on Thursday struck down the electoral bonds scheme, calling it unconstitutional and arbitrary. The court said the scheme violates the right to information under Article 19(1)(a).',
        'link': 'http://example.com'
    },
    {
        'title': 'India achieves target of 40% non-fossil fuel energy capacity',
        'source': 'PIB',
        'summary': 'India has achieved its target of 40% installed electric capacity from non-fossil fuels ahead of 2030. This is a significant milestone in the countrys energy transition journey.',
        'link': 'http://example.com'
    },
    {
        'title': 'Editorial: The need for judicial accountability',
        'source': 'The Hindu Editorial',
        'summary': 'The recent judgments highlight the need for a robust mechanism for judicial accountability. The collegium system needs reform to ensure transparency.',
        'link': 'http://example.com'
    }
]

with app.app_context():
    print("🧪 Testing Night Watchman Synthesis...")
    briefing = night_watchman._synthesize_briefing(mock_articles)
    
    print("\n📝 Generated Briefing Summary:")
    print(briefing.get('summary')[:500] + "...")
    
    print(f"\n🔗 Static Linkage: {briefing.get('static_linkage', 'N/A')}")
    print(f"\n🧠 Mind Map:\n{briefing.get('mind_map', 'N/A')}")
    
    print("\n⚡ Generated Flashcards:")
    if 'flashcards' in briefing:
        for card in briefing['flashcards']:
            print(f"- [Front]: {card['front']}")
            print(f"  [Back]: {card['back']}")
            print(f"  [Tags]: {card.get('tags')}")
    else:
        print("No flashcards found in output.")
