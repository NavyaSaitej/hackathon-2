"""
QuickCards — Pydantic Models (V5)

Defines the strict JSON schema that the Gemini LLM must conform to.
Single-pass payload: one API call returns the full Deck.
"""

from pydantic import BaseModel, Field


class QuizCard(BaseModel):
    """A single flashcard with quiz capabilities and timestamp context."""

    question: str = Field(
        ..., description="A clear, concise question derived from the video transcript."
    )
    correct_answer: str = Field(
        ..., description="The correct answer to the question."
    )
    distractors: list[str] = Field(
        ...,
        min_length=3,
        max_length=3,
        description="Exactly 3 plausible but incorrect answers.",
    )
    explanation: str = Field(
        ...,
        description="A 1-sentence explanation of why the correct answer is right.",
    )
    timestamp_seconds: int = Field(
        ...,
        ge=0,
        description="The timestamp (in seconds) in the video where this concept is discussed.",
    )


class Deck(BaseModel):
    """The complete quiz deck returned by the LLM in a single pass."""

    video_title: str = Field(..., description="Title of the source YouTube video.")
    cards: list[QuizCard] = Field(
        ..., min_length=1, description="The list of generated quiz cards."
    )
