# Technical Architecture Blueprint

**Project Name:** QuickCards (V4 - Enterprise Compliance)
**Status:** APPROVED

## 1. System Overview
The application consists of an installable PWA Vanilla frontend and a Dockerized FastAPI backend, wired into a strict Swecha GitLab CI/CD pipeline.

## 2. Technology Stack Selection & Justification
- **Frontend/UI:** Vanilla HTML5, CSS3, JavaScript. `sw.js` (Service Worker) for PWA.
- **Backend/API:** Python, `fastapi`, `uvicorn`, Docker.
- **Data/AI Frameworks:** `youtube-transcript-api`, `google-genai`, `pydantic`.
- **Code Quality/CI:** `biome` (JS Linting), `prettier`, `pre-commit`, `git-cliff` (Changelog), `gitlab-ci.yml`.

## 3. Data Ingestion & Governance Strategy
- **Transcript Chunking:** Backend chunks transcripts with `[TS_ID]` for accurate timestamping.
- **Zero Retention Policy:** Transcripts and JSON are explicitly garbage-collected.
- **Security & Privacy:** Strict CORS, `youtube-nocookie.com`, and strict `.gitignore`.

## 4. AI / Model Strategy
- **Approach:** Zero-shot prompting with strict JSON schema enforcement using `pydantic` (`QuizCard`).
- **Base Model:** Gemini 1.5 Flash.

## 5. CSS / Performance Strategy
- **Glassmorphism Guardrails:** `will-change: transform` on flipping cards.

## 6. Directory Structure (Swecha Compliance Standard)
```text
.
├── .git/
├── .husky/            # Git hooks
├── .speckit/          
├── frontend/          
│   ├── index.html
│   ├── style.css
│   ├── app.js         
│   ├── sw.js          # PWA Service Worker
│   └── manifest.json  # PWA Manifest
├── backend/           
│   ├── main.py        
│   ├── scraper.py     
│   ├── models.py      
│   ├── Dockerfile     # Backend Containerization
│   ├── .dockerignore
│   └── uv.lock        
├── .env.example
├── .editorconfig
├── .eslintignore
├── .eslintrc.js
├── .gitignore
├── .gitlab-ci.yml     # Swecha CI/CD
├── .pre-commit-config.yaml
├── .prettierrc
├── biome.json
├── cliff.toml
├── package.json       # For frontend dev tooling
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
- **CI/CD:** GitLab CI runs `biome`, `prettier`, and `pytest` on every push.
