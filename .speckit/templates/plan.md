# Technical Architecture Blueprint

**Project Name:** Video-to-Flashcards Auto-Study Buddy
**Status:** APPROVED

## 1. System Overview
The application consists of a lightweight Vanilla frontend that communicates with a serverless FastAPI backend. The backend fetches the YouTube transcript, scrubs PII, and forwards it to the Gemini API to generate structured JSON flashcards, which are returned and rendered by the client.

## 2. Technology Stack Selection & Justification
- **Frontend/UI:** Vanilla HTML5, CSS3, JavaScript. *Justification:* Agnostic UI ensures zero build-step overhead for the hackathon, providing maximum reliability.
- **Backend/API:** Python/FastAPI. *Justification:* Fast to spin up, excellent open-source libraries available for data processing.
- **Data/AI Frameworks:** `youtube-transcript-api` (Open Source) + Gemini API. *Justification:* Leverages existing robust open-source tools for the heavy lifting.
- **Storage/Database:** None (Stateless MVP). *Justification:* Infinite scalability with zero data persistence.

## 3. Data Ingestion & Governance Strategy
- **Lineage & Ingestion:** Data is fetched directly from YouTube's public caption track in real-time.
- **PII Scrubbing:** A dedicated Python module using Regex and `presidio-analyzer` (if size permits, else strict regex) will scrub the text of phone numbers, emails, and names before any LLM processing.
- **Failure Modes:** If a video lacks captions, is over 20 minutes, or a row is malformed, the pipeline will explicitly crash and return a 400 Bad Request. No silent data drops.

## 4. AI / Model Strategy
- **Approach:** Zero-shot prompting with strict JSON schema enforcement via API parameters.
- **Base Model:** Gemini 1.5 Flash.
- **NLP & OOV Protocol:** We will utilize the standard Gemini BPE tokenizer. If out-of-vocabulary (OOV) tokens or unsupported mixed scripts are encountered during preprocessing, the fallback sequence is a deterministic mapping to the `<UNK>` token. No hallucination of characters is permitted.

## 5. Absolute Reproducibility Protocol
- **Environment:** Backend dependencies will be strictly locked using `uv.lock`.
- **Determinism:** LLM API calls will use `temperature=0.0` and a fixed `random_seed=42` to ensure deterministic outputs.

## 6. Directory Structure
```text
.
├── .speckit/          # Project Governance
├── frontend/          # HTML/CSS/JS Source
│   ├── index.html
│   ├── style.css
│   └── app.js
├── backend/           # FastAPI Logic
│   ├── main.py
│   ├── scraper.py
│   └── uv.lock        # Locked environment
└── README.md
```

## 7. Evaluation Framework & Deployment
- **Methodology:** Automated unit testing via `pytest` for the PII scrubber and OOV fallback logic.
- **Deployment:** Vercel (Frontend) and Render (Backend).
