# QuickCards ⚡

**AI-powered YouTube-to-Quiz Flashcard Generator**

Transform any YouTube video into an interactive multiple-choice quiz deck — powered by Google Gemini.

## Features

- 🧠 **AI-Powered Quiz Generation** — Gemini generates smart questions with 3 plausible distractors and explanations.
- ⏱️ **Contextual Timestamp Links** — Every card links to the exact moment in the video via an embedded PiP player.
- 📤 **1-Click Anki Export** — Download your deck as a ready-to-import `.txt` file.
- 🎨 **Premium Glassmorphic UI** — Dark mode, 3D card flips, micro-animations.
- 📱 **PWA Installable** — Works offline and can be installed on mobile devices.
- 🔒 **Privacy-First** — Uses `youtube-nocookie.com` embeds. Zero data retention.

## Quick Start

### Prerequisites
- Python 3.12+
- A [Google Gemini API Key](https://aistudio.google.com/apikey)

### Backend Setup
```bash
cd backend
cp ../.env.example .env
# Edit .env and add your GEMINI_API_KEY

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend Setup
```bash
# No build step required!
cd frontend
python -m http.server 5500
# Open http://localhost:5500
```

### Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | Yes | Google Gemini API key |
| `APP_SECRET` | Yes | Shared secret for frontend↔backend auth |
| `VERCEL_FRONTEND_URL` | No | Production frontend URL for CORS |

## Architecture

```text
frontend/           Vanilla HTML/CSS/JS (ES6 Modules, PWA)
├── js/
│   ├── state.js    4-State Router (Landing→Loading→Quiz→Summary)
│   ├── api.js      Backend fetch with X-App-Secret header
│   ├── ui.js       Quiz logic, ARIA, Anki export
│   └── video.js    YouTube PiP iframe (nocookie)
├── sw.js           Service Worker for offline caching
└── manifest.json   PWA manifest

backend/            FastAPI + Gemini
├── main.py         CORS, rate limiting, /generate endpoint
├── scraper.py      YouTube transcript fetch & chunking
├── models.py       Pydantic QuizCard/Deck schemas
└── Dockerfile      Container for Render deployment
```

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Vanilla HTML5, CSS3 (Glassmorphism), ES6 Modules |
| Backend | Python, FastAPI, Uvicorn |
| AI | Google Gemini 2.0 Flash |
| Data | youtube-transcript-api, Pydantic |
| Security | slowapi (rate limiting), X-App-Secret handshake |
| Deployment | Vercel (frontend), Render (backend) |
| CI/CD | GitLab CI (.gitlab-ci.yml) |

## License

This project is licensed under the GNU General Public License v3.0 — see the [LICENSE](LICENSE) file.

## Author

**Navya Sai Tej**
