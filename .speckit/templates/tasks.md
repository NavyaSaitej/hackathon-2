# Actionable Task Breakdown

## Phase 1: Environment & Reproducibility
- `[ ]` Scaffold repository structure (`frontend/` and `backend/`).
- `[ ]` Initialize and strictly lock backend dependencies using `uv init` and `uv.lock`.
- `[ ]` Set up deterministic seed configurations (`seed=42`) and temperature settings (`0.0`) in the LLM utility.

## Phase 2: Data Governance & Ingestion
- `[ ]` Implement YouTube URL parser and validator (max length 20 mins).
- `[ ]` Implement `youtube-transcript-api` integration in the backend.
- `[ ]` Implement the PII scrubbing pipeline (Regex for emails/phones).
- `[ ]` Implement hard-failure / dead-letter logic for "No Subtitles Found" errors.

## Phase 3: AI / Model Layer
- `[ ]` Implement the strict OOV/mixed-script fallback mechanism (`<UNK>` mapping).
- `[ ]` Write the strict JSON-enforced system prompt for flashcard generation.
- `[ ]` Integrate the LLM API call in the backend.

## Phase 4: Frontend / Application Layer
- `[ ]` Scaffold main UI layout (Vanilla HTML/CSS).
- `[ ]` Implement the 3D CSS flip animation for the flashcards.
- `[ ]` Integrate UI with the backend FastAPI endpoint.

## Phase 5: Rigorous Evaluation
- `[ ]` Execute unit tests against the PII pipeline and OOV mapping.
- `[ ]` Test end-to-end latency with a 10-minute video to ensure it meets the < 15.0 seconds benchmark.

## Phase 6: Documentation & Handoff
- `[ ]` Write `README.md` with explicit `uv run` reproduction instructions.
- `[ ]` Generate `walkthrough.md`.
