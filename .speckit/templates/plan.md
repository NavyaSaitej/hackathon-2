# Technical Architecture Blueprint

**Project Name:** QuickCards
**Status:** APPROVED

## 1. System Overview
The application consists of a lightweight Vanilla frontend that communicates with a serverless FastAPI backend. The backend fetches the YouTube transcript, scrubs PII, enforces a Pydantic schema, and forwards it to the Gemini API to generate structured JSON flashcards, which are returned and rendered by the client.

## 2. Technology Stack Selection & Justification
- **Frontend/UI:** Vanilla HTML5, CSS3, JavaScript. *Justification:* Agnostic UI ensures zero build-step overhead for the hackathon, providing maximum reliability.
- **Backend/API:** Python, `fastapi`, `uvicorn`. *Justification:* Fast to spin up, native async support for API calls.
- **Data/AI Frameworks:** `youtube-transcript-api` (transcript fetching), `presidio-analyzer` (PII scrubbing), `google-genai` (LLM), `pydantic` (Schema validation). *Justification:* Leverages existing robust open-source tools.
- **Storage/Database:** None (Stateless MVP). *Justification:* Infinite scalability with zero data persistence.

## 3. Data Ingestion & Governance Strategy
- **Lineage & Ingestion:** Fetched directly from YouTube. Prefers manual `en` captions, falls back to `a.en` (auto-generated).
- **PII Scrubbing:** `presidio-analyzer` will sanitize the text of phone numbers, emails, and names. If deployment size is an issue, a compiled Python Regex pipeline will be the strict fallback.
- **Failure Modes:** Explicit 400 Bad Request on: missing captions, video > 20 mins, or malformed URL. No silent data drops.
- **[New] Security:** The FastAPI backend will implement strict CORS middleware to only accept POST requests from the Vercel frontend domain.

## 4. AI / Model Strategy
- **Approach:** Zero-shot prompting with strict JSON schema enforcement using `pydantic` output parsers.
- **Base Model:** Gemini 1.5 Flash.
- **NLP & OOV Protocol:** Utilizes the standard Gemini BPE tokenizer. If out-of-vocabulary (OOV) tokens or unsupported mixed scripts are encountered, the fallback sequence is a deterministic mapping to the `<UNK>` token. No hallucination of characters is permitted.

## 5. Absolute Reproducibility Protocol
- **Environment:** Backend dependencies strictly locked using `uv.lock`.
- **Determinism:** LLM API calls will use `temperature=0.0` and a fixed `random_seed=42`. Pydantic models guarantee the exact JSON structure on every execution.

## 6. Directory Structure
```text
.
├── .speckit/          # Project Governance
├── frontend/          # HTML/CSS/JS Source
│   ├── index.html
│   ├── style.css
│   └── app.js
├── backend/           # FastAPI Logic
│   ├── main.py        # FastAPI routes & CORS
│   ├── scraper.py     # youtube-transcript-api logic & PII scrubber
│   ├── models.py      # Pydantic schemas
│   └── uv.lock        # Locked environment
└── README.md
```

## 7. Evaluation Framework & Deployment
- **Methodology:** Automated unit testing via `pytest` for the PII scrubber, OOV fallback logic, and Pydantic schema validation.
- **Deployment:** Vercel (Frontend) and Render (Backend).
