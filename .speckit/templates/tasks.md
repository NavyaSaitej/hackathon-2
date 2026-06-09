# Actionable Task Breakdown

## Phase 1: Environment & Reproducibility
- `[ ]` Scaffold repository structure (`frontend/` and `backend/`).
- `[ ]` Initialize and strictly lock backend dependencies (`fastapi`, `uvicorn`, `youtube-transcript-api`, `pydantic`, `presidio-analyzer`, `slowapi`) using `uv init` and `uv.lock`.
- `[ ]` Create `.env.example` for secure Gemini API key management.
- `[ ]` Set up deterministic seed configurations (`seed=42`) and temperature settings (`0.0`) in the LLM utility.
- `[ ]` Configure strict CORS middleware and IP rate-limiting (`slowapi`) in `main.py`.

## Phase 2: Data Governance & Ingestion
- `[ ]` Implement robust YouTube URL regex validator (supporting `youtu.be` and `watch?v=`). Enforce 20-min max length.
- `[ ]` Implement `youtube-transcript-api` integration (fetch manual `en`, fallback to auto `a.en`).
- `[ ]` `[Requires Compute]` Implement the `presidio-analyzer` PII scrubbing pipeline.
- `[ ]` Implement hard-failure / dead-letter logic (400 Bad Request) for "No Subtitles Found" errors.

## Phase 3: AI / Model Layer
- `[ ]` Implement the strict OOV/mixed-script fallback mechanism (`<UNK>` mapping).
- `[ ]` Define Pydantic models (`Flashcard`, `Deck`) to rigidly enforce the LLM's JSON output structure.
- `[ ]` Integrate the LLM API call in the backend, passing the Pydantic schema.
- `[ ]` Implement explicit backend memory garbage collection (Zero Retention) to drop transcripts post-generation.

## Phase 4: Frontend / Application Layer
- `[ ]` Scaffold main UI layout (Vanilla HTML/CSS).
- `[ ]` Implement specific UI error states (e.g., "Video too short", "Rate Limited", "No Captions").
- `[ ]` Implement Progressive Loading UX ("Fetching..." -> "Analyzing..." -> "Generating...") to mask backend latency.
- `[ ]` Implement the 3D CSS flip animation for the flashcards.
- `[ ]` Implement the "Export to Anki" button to generate a downloadable `.txt` (TSV) file.
- `[ ]` Ensure keyboard navigability (Tab to focus, Enter/Space to flip) for WCAG 2.1 AA compliance.
- `[ ]` Integrate UI with the backend FastAPI endpoint via async `fetch`.

## Phase 5: Rigorous Evaluation
- `[ ]` Execute unit tests (`pytest`) against the PII pipeline, URL regex, and OOV mapping.
- `[ ]` Test end-to-end latency with a 10-minute video to ensure it meets the < 15.0 seconds benchmark.
- `[ ]` Run Google Lighthouse to verify 100% Accessibility score.

## Phase 6: Documentation & Handoff
- `[ ]` Write `README.md` with explicit `uv run` reproduction instructions and `.env` setup guide.
- `[ ]` Configure UptimeRobot (or similar cron) to ping the Render backend every 14 minutes.
- `[ ]` Generate `walkthrough.md`.
