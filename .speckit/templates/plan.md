# Technical Architecture Blueprint

**Project Name:** Video-to-Flashcards Auto-Study Buddy
**Status:** APPROVED

## 1. System Overview
The application consists of a lightweight Vanilla frontend that communicates with a serverless backend proxy. The proxy fetches the YouTube transcript and forwards it to an LLM API to generate structured JSON flashcards, which are then returned and rendered by the client.

## 2. Technology Stack Selection & Justification
- **Frontend/UI:** Vanilla HTML5, CSS3, JavaScript. *Justification:* Ensures zero build-step overhead for the hackathon, providing maximum reliability and alignment with the "Framework-Agnostic" mandate.
- **Backend/API:** Python/FastAPI (or Node.js Serverless Function). *Justification:* Fast to spin up, excellent open-source libraries available for both transcript fetching and LLM integration.
- **Data/AI Frameworks:** `youtube-transcript-api` (Open Source Python library) + Gemini/OpenAI API. *Justification:* Leverages existing robust open-source tools for the heavy lifting.
- **Storage/Database:** None (Stateless MVP). *Justification:* Ensures infinite scalability for the hackathon demo.

## 3. Data Ingestion & Governance Strategy
- **Lineage & Ingestion:** Data is fetched directly from YouTube's public caption track in real-time.
- **PII Scrubbing:** Not strictly necessary for public educational videos, but API endpoints will strip out HTML tags and metadata before sending to the LLM.
- **Failure Modes:** If a video lacks captions or is too long, the pipeline explicitly crashes with a user-friendly error message rather than failing silently.

## 4. AI / Model Strategy
- **Approach:** Zero-shot prompting with strict JSON schema enforcement.
- **Base Model:** Gemini 1.5 Flash (or equivalent fast model).
- **Telugu Processing:** N/A for this specific MVP, but the prompt architecture is language-agnostic and can support Telugu if the source video has Telugu captions.

## 5. Absolute Reproducibility Protocol
- **Environment:** Backend dependencies will be strictly locked using `requirements.txt` or `uv.lock`.
- **Determinism:** LLM API calls will use `temperature=0.2` to ensure relatively deterministic outputs.

## 6. Directory Structure
```text
.
├── .speckit/          # Project Governance
├── frontend/          # HTML/CSS/JS Source
│   ├── index.html
│   ├── style.css
│   └── app.js
├── backend/           # Serverless API Logic
│   ├── main.py
│   └── requirements.txt
└── README.md
```

## 7. Evaluation Framework & Deployment
- **Methodology:** Manual integration testing of 5 diverse YouTube URLs to ensure consistent JSON formatting and UI rendering.
- **Deployment:** Vercel (Frontend) and Render/Vercel (Backend).
