# Video-to-Flashcards Auto-Study Buddy (Project Spec)

## Overview
A web-based application designed for students and self-learners. Users input a YouTube video URL, and the system automatically extracts the transcript, utilizes a Large Language Model (LLM) to identify key concepts, and generates interactive, flippable flashcards.

## Target Audience
- High school and college students.
- Lifelong learners using video courses.
- Anyone looking to improve retention of video content.

## Core Features (MVP)
1. **URL Input:** A simple interface to accept a YouTube URL.
2. **Transcript Extraction:** Backend/API logic to pull the closed captions/transcript from the video.
3. **AI Summarization & QA Generation:** Prompting an LLM to read the transcript and generate 5-10 Question & Answer pairs representing the core concepts.
4. **Interactive Flashcard UI:** A deck of digital flashcards the user can click to flip, swipe, or advance through.
5. **No-Login Experience:** Users can generate and use flashcards instantly without creating an account (for hackathon demo speed).

## Non-Goals (Out of Scope for Hackathon)
- User accounts and saving decks long-term.
- Spaced repetition algorithms (e.g., Anki style).
- Supporting non-YouTube video sources.

## Success Metrics (Hackathon Demo)
- Successfully generating a deck of 5 flashcards from a 10-minute educational video in under 15 seconds.
- A flawless, bug-free flip animation on both mobile and desktop views.
