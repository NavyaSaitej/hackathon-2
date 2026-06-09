# Implementation Steps

## Phase 1: Skeleton & UI
1. Initialize `index.html`, `style.css`, and `app.js`.
2. Build the main layout: Header, URL Input field, and "Generate" button.
3. Build the Flashcard CSS: Implement the 3D flip animation (`transform-style: preserve-3d`, `rotateY`).
4. Hardcode a mock flashcard in HTML to test the flip interaction.

## Phase 2: Logic & Integration
1. Implement the YouTube URL parser in `app.js` to extract the video ID.
2. Build the mock `ai-service.js` (for testing without API costs) that returns a hardcoded JSON array of flashcards after a 2-second timeout.
3. Write the DOM manipulation logic to take the JSON array and dynamically render the flashcard HTML elements.
4. Implement the "Next" and "Previous" card navigation logic.

## Phase 3: The "Real" Backend (Optional / Final Polish)
1. Set up a lightweight API proxy (or use a free RapidAPI endpoint) to actually fetch transcripts for a given YouTube ID.
2. Connect the transcript string to the LLM API (Gemini/OpenAI) using the defined JSON prompt.
3. Replace the mock `ai-service.js` call with the real fetch call.

## Phase 4: Polish & Edge Cases
1. Add loading spinners and "Analyzing Video..." states.
2. Handle errors: "Invalid YouTube URL", "No subtitles available", "Video too long".
3. Ensure mobile responsiveness (cards should scale nicely on phone screens).
