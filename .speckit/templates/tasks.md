# Actionable Task Breakdown

## Phase 1: Environment & Reproducibility
- `[ ]` Scaffold repository structure (`frontend/` and `backend/`).
- `[ ]` Initialize and strictly lock backend dependencies using `uv init` and `uv.lock`.
- `[ ]` Create `.env.example` for secure Gemini API key management.
- `[ ]` Configure deterministic LLM utility settings (`seed=42`, `temperature=0.0`).
- `[ ]` Configure strict CORS middleware and IP rate-limiting (`slowapi`) in `main.py`.

## Phase 2: Data Governance & Ingestion
- `[ ]` Implement robust YouTube URL regex validator (Enforce 20-min max length).
- `[ ]` Implement `youtube-transcript-api` integration.
- `[ ]` **[V2]** Implement Transcript Chunker: Parse raw dictionary output into a text block annotated with precise timestamp IDs.
- `[ ]` `[Requires Compute]` Implement the `presidio-analyzer` PII scrubbing pipeline.
- `[ ]` Implement hard-failure / dead-letter logic (400 Bad Request).

## Phase 3: AI / Model Layer
- `[ ]` Implement the strict OOV/mixed-script fallback mechanism (`<UNK>` mapping).
- `[ ]` **[V2]** Define advanced Pydantic models (`QuizCard`, `Deck`) including distractors, explanations, and timestamp IDs.
- `[ ]` Integrate the LLM API call in the backend, passing the Pydantic schema (Single-Pass execution).
- `[ ]` Implement explicit backend memory garbage collection (Zero Retention).

## Phase 4: Frontend / Application Layer
- `[ ]` Scaffold main UI layout (Vanilla HTML/CSS).
- `[ ]` Implement specific UI error states.
- `[ ]` Implement Progressive Loading UX ("Fetching..." -> "Analyzing..." -> "Generating...").
- `[ ]` **[V2]** Implement Quiz UI logic: Render multiple choice buttons, calculate local score, show explanation on failure.
- `[ ]` **[V2]** Implement Contextual Deep Link: Render a `target="_blank"` YouTube link to the exact timestamp parsed from the LLM JSON.
- `[ ]` Implement the 3D CSS flip animation for the flashcards.
- `[ ]` Implement the "Export to Anki" button to generate a downloadable `.txt` (TSV) file.
- `[ ]` Ensure keyboard navigability for WCAG 2.1 AA compliance.
- `[ ]` Integrate UI with the backend FastAPI endpoint via async `fetch`.

## Phase 5: Rigorous Evaluation
- `[ ]` Execute unit tests (`pytest`) against the PII pipeline, URL regex, and Timestamp Chunker.
- `[ ]` Test end-to-end latency with a 10-minute video.
- `[ ]` Run Google Lighthouse to verify 100% Accessibility score.

## Phase 6: Documentation & Handoff
- `[ ]` Write `README.md` with explicit `.env` setup and `uv run` instructions.
- `[ ]` Configure UptimeRobot (or similar cron) to ping the Render backend every 14 minutes.
- `[ ]` Generate `walkthrough.md`.
