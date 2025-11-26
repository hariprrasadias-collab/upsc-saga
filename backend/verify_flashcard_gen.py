from app.services.upsc_summarizer import generate_flashcard_content

def test_generation():
    title = "India's New Space Policy 2023"
    summary = "The policy aims to privatize the space sector, allowing non-government entities to carry out end-to-end space activities. ISRO will focus on R&D."
    
    print("Generating Flashcard...")
    card = generate_flashcard_content(title, summary)
    
    print("\n--- Generated Card ---")
    print(f"Q: {card['question']}")
    print(f"A: {card['answer']}")
    
    if card['question'] and card['answer']:
        print("\n✅ Generation Successful")
    else:
        print("\n❌ Generation Failed")

if __name__ == "__main__":
    test_generation()
