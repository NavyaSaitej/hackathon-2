# QuickCards — Agent Handoff Guide

## Project Overview

**QuickCards** is a web application that generates interactive quiz flashcards from YouTube videos using Google Gemini AI. It consists of a Vanilla JS PWA frontend and a FastAPI Python backend.

**Live URL:** TBD (Vercel + Render deployment)

## Architecture

```text
frontend/           ES6 Vanilla JS Modules (No build step)
├── js/state.js     Entry point — 4-State Router
├── js/api.js       Backend communication + X-App-Secret
├── js/ui.js        Quiz rendering, ARIA, Anki export
├── js/video.js     YouTube iframe (nocookie) + PiP toggle
├── sw.js           Service Worker (PWA)
└── manifest.json   PWA Manifest

backend/            FastAPI + Gemini
├── main.py         App entry — CORS, rate limiting, /generate
├── scraper.py      YouTube transcript fetch & TS chunking
├── models.py       Pydantic QuizCard/Deck schemas
└── Dockerfile      Docker container for Render
```

## Agent Workflow

1. Read `README.md` for the user-facing overview.
2. Read this `AGENTS.md` for architecture and continuation context.
3. Read `.speckit/templates/specify.md`, `plan.md`, and `tasks.md` for full specifications.
4. Inspect `frontend/index.html`, `frontend/js/`, and `backend/main.py` before editing.
5. Run the frontend via `python -m http.server 5500 -d frontend`.
6. Run the backend via `cd backend && uvicorn main:app --reload`.
7. Keep changes small and consistent with the existing Vanilla JS + FastAPI structure.

## Key Design Decisions

- **No Node.js build step** for the frontend. ES6 modules run natively in the browser.
- **X-App-Secret header** prevents direct API abuse via Postman/cURL.
- **youtube-nocookie.com** domain for privacy-enhanced video embeds.
- **3-retry exponential backoff** circuit breaker for Gemini API calls.
- **Dynamic `aria-hidden` toggling** on 3D card flips for screen reader accessibility.
- **Transcript chunking with `[TS:seconds]`** to prevent LLM timestamp hallucination.

## Checks Before Handoff

- [ ] Frontend loads without console errors
- [ ] Backend starts without import errors
- [ ] "Demo" button fills URL and enables "Generate"
- [ ] `/generate` endpoint returns valid Deck JSON
- [ ] Card flip animations work smoothly
- [ ] Anki export downloads a `.txt` file
- [ ] Video PiP collapses and expands
