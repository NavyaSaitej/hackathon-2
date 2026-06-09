# Actionable Task Breakdown

## Phase 1: Environment & Reproducibility
- `[ ]` Scaffold repository structure (`frontend/` and `backend/`).
- `[ ]` Lock backend dependencies (`requirements.txt`).
- `[ ]` Configure deterministic LLM API settings.

## Phase 2: Data Governance & Ingestion
- `[ ]` Implement YouTube URL parser and validator.
- `[ ]` Implement `youtube-transcript-api` integration in the backend.
- `[ ]` Implement hard-failure logic for "No Subtitles Found" errors.

## Phase 3: AI / Model Layer
- `[ ]` Write the strict JSON-enforced system prompt for flashcard generation.
- `[ ]` Integrate the LLM API call in the backend.
- `[ ]` Create a mock endpoint returning static JSON for UI development.

## Phase 4: Frontend / Application Layer
- `[ ]` Build the `index.html` UI layout (URL input, loading states).
- `[ ]` Implement the 3D CSS flip animation for the flashcards.
- `[ ]` Write `app.js` to fetch from the backend and dynamically render cards.

## Phase 5: Rigorous Evaluation
- `[ ]` Test with 5 distinct educational videos.
- `[ ]` Verify cross-browser compatibility of the flip animation.

## Phase 6: Documentation & Handoff
- `[ ]` Write `README.md` with explicit local run instructions.
- `[ ]` Create `walkthrough.md`.
