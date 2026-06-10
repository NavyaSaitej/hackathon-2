from models import QuizCard, Deck

def test_deck_validation():
    deck = Deck(
        video_title="Test Video",
        cards=[
            QuizCard(
                question="What is 2+2?",
                correct_answer="4",
                distractors=["3", "5", "6"],
                explanation="2+2 is 4",
                timestamp_seconds=0
            )
        ]
    )
    assert deck.video_title == "Test Video"
    assert len(deck.cards) == 1
    assert deck.cards[0].correct_answer == "4"
