# QuickCards ⚡

This is the QuickCards application - an AI-powered YouTube-to-Quiz Flashcard Generator. It transforms any educational YouTube video into an interactive multiple-choice quiz deck, allowing users to rapidly assess their learning and review content with contextual timestamp links straight to the video.

Website Link:- https://hackathon-2-navyasaitejs-projects.vercel.app

## Features

**AI-Powered Quiz Generation:** Leverages Google Gemini to automatically generate smart multiple-choice questions, complete with 3 plausible distractors and detailed explanations, straight from video transcripts.

**Contextual Timestamp Links:** Every flashcard links directly to the exact moment in the source video where the answer is discussed, embedding a YouTube PiP player right next to the quiz.

**Indestructible Transcript Scraping:** Features a multi-layered transcript scraping backend that utilizes `yt-dlp` and falls back dynamically to community-driven parsers, seamlessly bypassing bot-blocking for custom YouTube videos.

**Interactive Flashcard UI:** 
- Renders an immersive, glassmorphic dark-mode quiz interface.
- 3D card flips, micro-animations, and dynamic progress bars enhance the learning experience.

**1-Click Anki Export:** Instantly download your completed quiz deck as a formatted `.txt` file, ready for seamless import into the popular spaced-repetition software, Anki.

**State Persistence:** Auto-saves the current quiz state, preventing data loss on accidental reloads.

**PWA Installable:** Progressive Web App support enables offline caching and installation to your mobile or desktop device.

## Technologies Used

**HTML5:** Semantic markup and structure for the interactive quiz layout.

**CSS3:** Custom glassmorphic styling, responsive 3D card flip animations, and modern typography.

**JavaScript (Vanilla):** Core application logic, client-side API requests, 4-state routing engine, and Anki export formatting.

**Python (FastAPI):** High-performance backend handling transcript fetching, prompt construction, and rate-limiting.

**Google Gemini 2.0 Flash:** Generative AI for extracting educational concepts and structuring multiple-choice questions.

**yt-dlp & youtube-transcript-api:** Backend libraries for fetching and parsing YouTube subtitle tracks.

## Getting Started

### Prerequisites

- Any modern web browser (Chrome, Firefox, Edge, Safari)
- Python 3.12+
- Node.js (for linting and local server tools)
- A [Google Gemini API Key](https://aistudio.google.com/apikey)

### Installation

Clone the repository:

```bash
git clone https://code.swecha.org/Navya_sai_tej/hackathon-2.git
cd hackathon-2
```

### Running the Backend

The backend is a FastAPI server that handles transcript fetching and Gemini AI communication.

```bash
cd backend
python -m venv venv
# On Windows: venv\Scripts\activate
# On Mac/Linux: source venv/bin/activate

pip install -r requirements.txt

# Create your environment configuration
cp ../.env.example .env
# Open .env and add your GEMINI_API_KEY and APP_SECRET

# Start the server
uvicorn main:app --reload --port 8000
```

### Running the Frontend

The frontend requires no build steps. You can serve the `frontend` directory using any local HTTP server.

```bash
cd frontend

# Using Python 3.x
python -m http.server 5500

# Using Node.js
npx http-server -p 5500
```

Then open: `http://localhost:5500`

## Building for Production

No build step is required for the frontend. The project is a static web application and can be deployed directly to Vercel, GitHub Pages, or GitLab Pages. The backend is designed to be deployed as serverless functions on Vercel or as a standalone service on Render.

Production deployment: https://hackathon-2-navyasaitejs-projects.vercel.app

## Project Structure

```text
.
|-- frontend/                 # Client-side application
|   |-- js/
|   |   |-- state.js          # 4-State Router (Landing -> Loading -> Quiz -> Summary)
|   |   |-- api.js            # Backend communication with secret headers
|   |   |-- ui.js             # DOM manipulation, quiz logic, and Anki export
|   |   `-- video.js          # YouTube PiP iframe controller
|   |-- index.html            # Main application shell
|   |-- style.css             # Glassmorphic UI and animations
|   |-- sw.js                 # Service Worker for PWA
|   `-- manifest.json         # PWA configuration
|-- backend/                  # API server
|   |-- main.py               # FastAPI routes, rate limiting, fallback generation
|   |-- scraper.py            # YouTube transcript fetch & chunking pipeline
|   |-- models.py             # Pydantic schemas for data validation
|   |-- demo_data.py          # Hardcoded fallback data for demo videos
|   `-- test_main.py          # Pytest suite
|-- .env.example              # Example environment variables
|-- .gitlab-ci.yml            # GitLab CI/CD pipeline configuration
`-- README.md                 # Project documentation
```

## Contributing

1. Fork the repository.
2. Create your feature branch (`git checkout -b feature/my-feature`).
3. Commit your changes (`git commit -m "feat: add my feature"`).
4. Push to the branch (`git push origin feature/my-feature`).
5. Open a Merge Request or Pull Request.

## License

This project is licensed under the GNU General Public License v3.0 — see the [LICENSE](LICENSE) file.
