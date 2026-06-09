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
- **Lineage & Ingestion:** Fetched directly from YouTube. Prefers manual `en` captions, falls back to `a.en` (auto-generated). *Risk Note: YouTube may rate-limit datacenter IPs, so we rely on the library's built-in proxy support if needed.*
- **PII Scrubbing:** `presidio-analyzer` will sanitize text. Compiled Python Regex pipeline is the strict fallback.
- **Zero Retention Policy:** The backend operates purely in memory. Transcripts and generated JSON are explicitly garbage-collected and never written to a database or persistent log file.
- **Failure Modes:** Explicit 400 Bad Request on: missing captions, video > 20 mins, malformed URL, or word count < 100. No silent data drops.
- **Security & Secrets:** Strict CORS middleware ensures only the Vercel frontend domain can access the backend. All Gemini API keys must be loaded via `.env` and injected securely at runtime.
- **Rate Limiting:** `slowapi` (or similar simple rate limiter) will enforce the 5 requests/hr IP limit.

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
- **Cold-Start Mitigation:** Render's free tier sleeps after 15 mins. A cron job (e.g., UptimeRobot) must be configured to ping the backend every 14 minutes during the hackathon demo period to prevent 50-second wake-up latencies.
- **UX Milestone Strategy:** To mask the 15-second latency, the frontend will implement "Progressive Loading" states (e.g., swapping text from "Fetching..." -> "Analyzing..." -> "Generating...") rather than a static spinner.
