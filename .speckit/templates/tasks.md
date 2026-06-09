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
- `[ ]` Implement Transcript Chunker: Parse raw dictionary into a text block annotated with timestamp IDs.
- `[ ]` `[Requires Compute]` Implement the `presidio-analyzer` PII scrubbing pipeline.
- `[ ]` Implement hard-failure / dead-letter logic (400 Bad Request).

## Phase 3: AI / Model Layer
- `[ ]` Implement the strict OOV/mixed-script fallback mechanism (`<UNK>` mapping).
- `[ ]` Define advanced Pydantic models (`QuizCard`, `Deck`) including distractors, explanations, and timestamp IDs.
- `[ ]` Integrate the LLM API call in the backend, passing the Pydantic schema (Single-Pass execution).
- `[ ]` Implement explicit backend memory garbage collection (Zero Retention).

## Phase 4: Frontend / Application Layer
- `[ ]` Build the 4-State Vanilla JS Router (Landing, Loading, Quiz, Summary).
- `[ ]` **Landing:** Add "Paste Demo URL" button and disable "Generate" until Regex validates input.
- `[ ]` **Loading:** Implement Progressive Loading text ("Fetching..." -> "Analyzing..." -> "Generating...").
- `[ ]` **Quiz:** Implement CSS Glassmorphism with `will-change: transform` performance protections.
- `[ ]` **Quiz:** Implement colorblind-accessible feedback (Checkmark/X icons + color).
- `[ ]` **Video:** Implement the collapsible PiP `youtube-nocookie.com` iframe embed. Link card flips to iframe API seeking.
- `[ ]` **Summary:** Implement the "Export to Anki" button to generate a downloadable `.txt` (TSV) file.

## Phase 5: Rigorous Evaluation
- `[ ]` Execute unit tests (`pytest`) against the PII pipeline, URL regex, and Timestamp Chunker.
- `[ ]` Test end-to-end latency with a 10-minute video.
- `[ ]` Run Google Lighthouse to verify 100% Accessibility score.

## Phase 6: Documentation & Handoff
- `[ ]` Write `README.md` with explicit `.env` setup and `uv run` instructions.
- `[ ]` Write `USER_MANUAL.md` explaining how to use QuickCards.
- `[ ]` Write `AGENTS.md` to guide future AI agent handoffs.
- `[ ]` Write compliance docs: `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`.
- `[ ]` Add an open-source `LICENSE` file.
- `[ ]` Create `state_checkpoint.json` for state persistence.
- `[ ]` Initialize `CHANGELOG.md`.
- `[ ]` Outline the Hackathon Pitch Deck (`QuickCards_Pitch.pptx`).
- `[ ]` Configure UptimeRobot (or similar cron) to ping the Render backend every 14 minutes.
- `[ ]` Generate `walkthrough.md`.
