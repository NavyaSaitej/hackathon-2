# Actionable Task Breakdown

## Phase 1: Repository Configuration & Compliance (Swecha Standard)
- `[ ]` Scaffold fundamental `.gitignore`, `.editorconfig`, and `.env.example`.
- `[ ]` Initialize frontend dev tooling (`package.json`, `biome.json`, `.prettierrc`, `.eslintrc.js`, `.eslintignore`).
- `[ ]` Initialize git hooks and changelog (`.husky/`, `.pre-commit-config.yaml`, `cliff.toml`).
- `[ ]` Define Swecha pipeline in `.gitlab-ci.yml`.
- `[ ]` Scaffold Backend (`Dockerfile`, `.dockerignore`, `uv.lock`).
- `[ ]` Integrate `loguru` in FastAPI for structured telemetry logging.

## Phase 2: Data Governance & Ingestion
- `[ ]` Implement robust YouTube URL regex validator (Enforce 20-min max length).
- `[ ]` Implement `youtube-transcript-api` integration.
- `[ ]` Implement Transcript Chunker: Parse raw dictionary into a text block annotated with timestamp IDs.
- `[ ]` `[Requires Compute]` Implement the `presidio-analyzer` PII scrubbing pipeline.

## Phase 3: AI / Model Layer
- `[ ]` Configure deterministic LLM utility settings (`seed=42`, `temperature=0.0`).
- `[ ]` Implement the strict OOV/mixed-script fallback mechanism (`<UNK>` mapping).
- `[ ]` Define advanced Pydantic models (`QuizCard`, `Deck`).
- `[ ]` Integrate the Gemini API call with a 3-retry exponential backoff circuit breaker.
- `[ ]` Configure App-to-App Security (`X-App-Secret` validation).

## Phase 4: Frontend / Application Layer (ES6 Modules)
- `[ ]` Build the ES6 Module structure (`api.js`, `ui.js`, `state.js`, `video.js`).
- `[ ]` Implement PWA compliance (`sw.js`, `manifest.json`).
- `[ ]` **Landing:** Add "Paste Demo URL" button and disable "Generate" until Regex validates input.
- `[ ]` **Loading:** Implement Progressive Loading text ("Fetching..." -> "Analyzing..." -> "Generating...").
- `[ ]` **Quiz:** Implement CSS Glassmorphism with `will-change: transform`.
- `[ ]` **Quiz:** Implement colorblind-accessible feedback (Checkmark/X icons + color).
- `[ ]` **Accessibility:** Implement dynamic `aria-hidden` toggling synced with CSS card flips.
- `[ ]` **Video:** Implement the collapsible PiP `youtube-nocookie.com` iframe embed. 
- `[ ]` **Summary:** Implement the "Export to Anki" button to generate `.txt` (TSV).

## Phase 5: Rigorous Evaluation
- `[ ]` Execute unit tests (`pytest`) against backend pipelines.
- `[ ]` Verify CI/CD pipeline runs `biome` and `prettier` without failing.
- `[ ]` Run Google Lighthouse to verify 100% Accessibility and PWA scores.

## Phase 6: Documentation & Handoff
- `[ ]` Write `README.md` and `USER_MANUAL.md`.
- `[ ]` Write `AGENTS.md` and initialize `STRESS_TEST_CHECKPOINT.md` and `state_checkpoint.json`.
- `[ ]` Write compliance docs: `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`.
- `[ ]` Add an open-source `LICENSE` file.
- `[ ]` Generate automated `CHANGELOG.md` via `git-cliff`.
- `[ ]` Outline the Hackathon Pitch Deck (`QuickCards_Pitch.pptx`).
- `[ ]` Configure UptimeRobot to ping the Render backend every 14 minutes.
