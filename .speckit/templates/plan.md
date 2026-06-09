# Technical Architecture Blueprint

**Project Name:** QuickCards (V2)
**Status:** APPROVED

## 1. System Overview
The application consists of a Vanilla frontend and a serverless FastAPI backend. The backend fetches the YouTube transcript (with timestamps), scrubs PII, enforces a Pydantic schema, and uses the Gemini API to generate a structured JSON array containing Questions, Answers, Distractors, Explanations, and Timestamp IDs in a *single pass*.

## 2. Technology Stack Selection & Justification
- **Frontend/UI:** Vanilla HTML5, CSS3, JavaScript. LocalStorage for Quiz scores.
- **Backend/API:** Python, `fastapi`, `uvicorn`.
- **Data/AI Frameworks:** `youtube-transcript-api`, `presidio-analyzer`, `google-genai`, `pydantic`.
- **Storage/Database:** None (Stateless MVP).

## 3. Data Ingestion & Governance Strategy
- **Lineage & Ingestion:** Fetched directly from YouTube. Prefers manual `en` captions, falls back to `a.en`.
- **Transcript Chunking [V2]:** The backend must pre-process the transcript to append a `[TS_ID]` to transcript chunks so the LLM can reference valid timestamps without hallucinating broken YouTube links.
- **PII Scrubbing:** `presidio-analyzer` will sanitize text.
- **Zero Retention Policy:** The backend operates purely in memory. Transcripts and generated JSON are explicitly garbage-collected.
- **Failure Modes:** Explicit 400 Bad Request on: missing captions, video > 20 mins, malformed URL, or word count < 100.
- **Security & Secrets:** Strict CORS middleware; Gemini API keys loaded via `.env`.
- **Rate Limiting:** `slowapi` enforces 5 requests/hr IP limit.

## 4. AI / Model Strategy
- **Approach:** Zero-shot prompting with strict JSON schema enforcement using `pydantic`.
- **[V2] Single-Pass Payload:** The Pydantic model (`QuizCard`) will demand `question`, `correct_answer`, `distractors` (list of 3), `explanation`, and `timestamp_id` in one generation to prevent token explosion and latency spikes.
- **Base Model:** Gemini 1.5 Flash.
- **NLP & OOV Protocol:** `<UNK>` fallback mapping for unknown tokens.

## 5. Absolute Reproducibility Protocol
- **Environment:** Backend dependencies strictly locked using `uv.lock`.
- **Determinism:** LLM API calls will use `temperature=0.0` and a fixed `random_seed=42`.

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
│   ├── models.py      # V2 Pydantic schemas (QuizCard)
│   └── uv.lock        # Locked environment
└── README.md
```

## 7. Evaluation Framework & Deployment
- **Methodology:** Automated unit testing via `pytest`.
- **Deployment:** Vercel (Frontend) and Render (Backend).
- **Cold-Start Mitigation:** UptimeRobot cron job configured to ping the backend every 14 minutes.
- **UX Milestone Strategy:** The frontend will implement "Progressive Loading" states ("Fetching..." -> "Analyzing..." -> "Generating...") to mask latency.
