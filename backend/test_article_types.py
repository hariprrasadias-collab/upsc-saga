# Test specific articles with different topics
import os
# os.environ['GEMINI_API_KEY'] = os.getenv('GEMINI_API_KEY')  # Use env variable

from app.services.upsc_summarizer import summarize_for_upsc

test_articles = [
    {
        "title": "Government announces new renewable energy policy",
        "content": "The Ministry of Power has announced a comprehensive renewable energy policy aimed at achieving net-zero emissions by 2070. The policy includes significant incentives for solar and wind energy projects, with a focus on rural electrification and sustainable development. It also outlines plans for green hydrogen production and electric vehicle infrastructure."
    },
    {
        "title": "Supreme Court ruling on Article 370",
        "content": "The Supreme Court delivered a landmark judgment on the constitutional validity of the abrogation of Article 370. The five-judge constitution bench examined the extent of Parliament's powers under Article 370 and its relationship with India's federal structure. The verdict has significant implications for center-state relations and constitutional law."
    },
    {
        "title": "India-Russia defense cooperation agreement signed",
        "content": "India and Russia signed a major defense cooperation agreement covering joint production of military equipment and technology transfer. The agreement strengthens strategic ties between the two nations and includes provisions for joint exercises and intelligence sharing. This comes amid evolving geopolitical dynamics in the Indo-Pacific region."
    }
]

print("Testing Gemini with different article types...\n")
for article in test_articles:
    print(f"Article: {article['title']}")
    result = summarize_for_upsc(article['title'], article['content'], "http://test")
    print(f"  Papers: {result['papers']}")
    print(f"  Subjects: {result['subjects']}")
    print(f"  Importance: {result['importance']}\n")
