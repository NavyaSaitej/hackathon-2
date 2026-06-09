# Technical Architecture Blueprint

**Project Name:** QuickCards (V3 - UI Mastered)
**Status:** APPROVED

## 1. System Overview
The application consists of a Vanilla frontend and a serverless FastAPI backend. The frontend handles a complex 4-state Glassmorphic UI and YouTube iframe state. The backend fetches the transcript, scrubs PII, enforces a Pydantic schema, and uses Gemini to generate a structured JSON array in a single pass.

## 2. Technology Stack Selection & Justification
- **Frontend/UI:** Vanilla HTML5, CSS3 (Glassmorphism), JavaScript. FontAwesome for a11y icons.
- **Backend/API:** Python, `fastapi`, `uvicorn`.
- **Data/AI Frameworks:** `youtube-transcript-api`, `presidio-analyzer`, `google-genai`, `pydantic`.
- **Storage/Database:** None (Stateless MVP).

## 3. Data Ingestion & Governance Strategy
- **Lineage & Ingestion:** Fetched directly from YouTube. 
- **Transcript Chunking:** Backend chunks transcripts with `[TS_ID]` for accurate timestamping.
- **PII Scrubbing:** `presidio-analyzer` sanitization.
- **Zero Retention Policy:** The backend operates purely in memory. 
- **Failure Modes:** Explicit 400 Bad Request. Frontend "Generate" button disabled until valid Regex match to prevent backend spam.
- **Security & Privacy:** Strict CORS middleware. Iframe embeds must strictly use `youtube-nocookie.com`.
- **Rate Limiting:** `slowapi` enforces 5 requests/hr IP limit.

## 4. AI / Model Strategy
- **Approach:** Zero-shot prompting with strict JSON schema enforcement using `pydantic` (`QuizCard` payload).
- **Base Model:** Gemini 1.5 Flash.
- **NLP & OOV Protocol:** `<UNK>` fallback mapping.

## 5. CSS / Performance Strategy
- **Glassmorphism Guardrails:** To prevent scrolling lag on cheap devices, `will-change: transform` will be used on flipping cards.

## 6. Directory Structure
```text
.
├── .speckit/          
├── frontend/          
│   ├── index.html
│   ├── style.css
│   └── app.js         # Contains the 4-State UI Router
├── backend/           
│   ├── main.py        
│   ├── scraper.py     
│   ├── models.py      
│   └── uv.lock        
├── README.md
├── USER_MANUAL.md
├── AGENTS.md
├── CONTRIBUTING.md
├── SECURITY.md
├── state_checkpoint.json
└── LICENSE
```

## 7. Evaluation Framework & Deployment
- **Deployment:** Vercel (Frontend) and Render (Backend).
- **Cold-Start Mitigation:** UptimeRobot cron job pings backend every 14 minutes.
