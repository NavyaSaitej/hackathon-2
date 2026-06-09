# Technical Architecture Blueprint

**Project Name:** QuickCards (V5 - Ultimate Edition)
**Status:** APPROVED

## 1. System Overview
The application consists of a modular PWA Vanilla frontend and a Dockerized FastAPI backend. The backend incorporates structured logging (`loguru`), Pydantic schema enforcement, and an exponential backoff circuit breaker for Gemini API reliability.

## 2. Technology Stack Selection & Justification
- **Frontend/UI:** ES6 Vanilla JS Modules (`api.js`, `ui.js`, `state.js`, `video.js`). `sw.js` for PWA. Zero Node.js build step required.
- **Backend/API:** Python, `fastapi`, `uvicorn`, Docker, `loguru` (Structured Logging).
- **Data/AI Frameworks:** `youtube-transcript-api`, `google-genai`, `pydantic`.
- **Code Quality/CI:** `biome` (JS Linting), `prettier`, `pre-commit`, `git-cliff` (Changelog), `gitlab-ci.yml`.

## 3. Data Ingestion & Governance Strategy
- **Transcript Chunking:** Backend chunks transcripts with `[TS_ID]` for accurate timestamping.
- **Zero Retention Policy:** Transcripts and JSON are explicitly garbage-collected.
- **Security & Privacy:** Strict CORS, `youtube-nocookie.com`, and strict `.gitignore`.
- **App-to-App Handshake:** Frontend passes an `X-App-Secret` to block direct API abuse.

## 4. AI / Model Strategy
- **Approach:** Zero-shot prompting with strict JSON schema enforcement using `pydantic` (`QuizCard`).
- **Self-Correction Prompting:** The prompt instructs the LLM to verify distractors against transcript context to reduce hallucination.
- **Base Model:** Gemini 1.5 Flash.

## 5. CSS / Performance Strategy
- **Glassmorphism Guardrails:** `will-change: transform` on flipping cards.
- **Accessibility Sync:** Dynamic `aria-hidden` toggling during CSS flips.

## 6. Directory Structure (Modular ES6 Standard)
```text
.
├── .git/
├── .husky/            
├── .speckit/          
├── frontend/          
│   ├── index.html
│   ├── style.css
│   ├── js/            # ES6 Modular Architecture
│   │   ├── api.js     # Fetch and Error handling
│   │   ├── ui.js      # DOM and ARIA manipulation
│   │   ├── state.js   # 4-State Router logic
│   │   └── video.js   # YouTube iframe API logic
│   ├── sw.js          
│   └── manifest.json  
├── backend/           
│   ├── main.py        
│   ├── scraper.py     
│   ├── models.py      
│   ├── Dockerfile     
│   ├── .dockerignore
│   └── uv.lock        
├── .env.example
├── .editorconfig
├── .eslintignore
├── .eslintrc.js
├── .gitignore
├── .gitlab-ci.yml     
├── .pre-commit-config.yaml
├── .prettierrc
├── biome.json
├── cliff.toml
├── package.json       
├── README.md
├── USER_MANUAL.md
├── AGENTS.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── STRESS_TEST_CHECKPOINT.md
├── state_checkpoint.json
├── CHANGELOG.md
└── LICENSE
```

## 7. Evaluation Framework & Deployment
- **Deployment:** Vercel (Frontend) and Render (Backend via Docker).
- **CI/CD:** GitLab CI runs `biome`, `prettier`, and `pytest`.
