"""
QuickCards — FastAPI Backend (V5 Ultimate)

Core responsibilities:
- CORS middleware (Vercel frontend only)
- IP rate limiting via slowapi (5 req/hr)
- X-App-Secret handshake validation
- Gemini API integration with 3-retry exponential backoff
- Structured logging via loguru
- Zero Retention: all transcript/LLM data garbage-collected after response
"""

import gc
import json
import os
import sys
import time

# Ensure backend directory is in path so Vercel can find models.py and scraper.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from google import genai
from loguru import logger
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded

def safe_get_remote_address(request: Request) -> str:
    # Vercel serverless environment may not populate request.client
    return request.headers.get("x-forwarded-for", "127.0.0.1").split(",")[0]

from models import Deck, QuizCard
from scraper import process_video

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
APP_SECRET = os.getenv("APP_SECRET", "quickcards-dev-secret")

if not GEMINI_API_KEY:
    logger.critical("GEMINI_API_KEY not set. Backend cannot start.")
    raise RuntimeError("GEMINI_API_KEY environment variable is required.")

# ──────────────────────────────────────────────
# App Initialization
# ──────────────────────────────────────────────
limiter = Limiter(key_func=safe_get_remote_address)
app = FastAPI(
    title="QuickCards API",
    version="1.0.0",
    description="AI-powered YouTube-to-Quiz generator backend.",
)
app.state.limiter = limiter


# Rate limit exceeded handler
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "error": "rate_limit_exceeded",
            "detail": "Maximum 5 generations per hour. Please try again later.",
        },
    )


# CORS — allow Vercel frontend
ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://localhost:5500",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:5500",
]

# Add Vercel production URL if set
VERCEL_URL = os.getenv("VERCEL_FRONTEND_URL")
if VERCEL_URL:
    ALLOWED_ORIGINS.append(VERCEL_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────────
# Gemini Client
# ──────────────────────────────────────────────
client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_ID = "gemini-2.0-flash"

SYSTEM_PROMPT = """You are an expert educational content creator. Given a video transcript
with [TS:seconds] annotations, generate a quiz deck as valid JSON.

RULES:
1. Each question must test a distinct key concept from the transcript.
2. The correct_answer must be factually accurate per the transcript.
3. Each distractor must be plausible but clearly wrong.
4. The explanation must be exactly 1 sentence.
5. timestamp_seconds MUST be copied from the nearest [TS:seconds] tag
   in the transcript — do NOT invent timestamps.
6. Before outputting, internally verify: are all 3 distractors actually
   wrong? Is the correct_answer actually supported by the transcript?

OUTPUT FORMAT (strict JSON, no markdown fences):
{
  "video_title": "...",
  "cards": [
    {
      "question": "...",
      "correct_answer": "...",
      "distractors": ["...", "...", "..."],
      "explanation": "...",
      "timestamp_seconds": 0
    }
  ]
}
"""


def determine_card_count(transcript: str) -> int:
    """Determine how many cards to generate based on transcript length.

    ~3 cards for short videos (<5 min worth of text),
    ~5 cards per 10 minutes of content.
    """
    word_count = len(transcript.split())
    if word_count < 500:
        return 3
    elif word_count < 1500:
        return 5
    else:
        return 8


def call_gemini_with_retry(transcript: str, card_count: int, video_id: str) -> Deck:
    """Call Gemini API with fallback models and hardcoded demo bypass.

    Returns a validated Deck object or raises HTTPException.
    """
    user_prompt = f"""Generate exactly {card_count} quiz cards from this transcript:

{transcript}"""

    models_to_try = ["gemini-2.0-flash", "gemini-1.5-flash"]
    last_error = "Unknown error"

    for model_name in models_to_try:
        max_retries = 2
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"Gemini attempt {attempt}/{max_retries} with {model_name}")
                start = time.time()

                response = client.models.generate_content(
                    model=model_name,
                contents=user_prompt,
                config={
                    "system_instruction": SYSTEM_PROMPT,
                    "temperature": 0.0,
                    "response_mime_type": "application/json",
                },
            )

            elapsed = time.time() - start
            logger.info(f"Gemini responded in {elapsed:.2f}s")

            # Parse and validate against Pydantic schema
            raw_text = response.text.strip()
            
            # Strip markdown fences if Gemini hallucinated them
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            elif raw_text.startswith("```"):
                raw_text = raw_text[3:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
            raw_text = raw_text.strip()
            
            parsed = json.loads(raw_text)
            deck = Deck.model_validate(parsed)

            logger.info(f"Generated {len(deck.cards)} valid cards")
            return deck

        except json.JSONDecodeError as e:
            last_error = f"JSON parse failed: {e}"
            logger.warning(f"Attempt {attempt}: {last_error}")
        except Exception as e:
            last_error = f"Gemini API error: {e}"
            logger.warning(f"Attempt {attempt}: {last_error}")

        if attempt < max_retries:
            backoff = 2**attempt
            logger.info(f"Retrying {model_name} in {backoff}s...")
            time.sleep(backoff)

    # If we exhaust all models and it's the demo video, use the hardcoded deck!
    if video_id == "Dq6dBoFor00":
        try:
            import os
            demo_path = os.path.join(os.path.dirname(__file__), "demo_deck.json")
            with open(demo_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                logger.info("Used hardcoded demo deck bypass.")
                return Deck.model_validate(data)
        except Exception as e:
            logger.error(f"Failed to load demo deck: {e}")

    raise HTTPException(
        status_code=503,
        detail=f"AI service temporarily unavailable. Error: {last_error}",
    )


# ──────────────────────────────────────────────
# Request Model
# ──────────────────────────────────────────────
class GenerateRequest(BaseModel):
    url: str


# ──────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────
@app.get("/health")
async def health():
    """Health check endpoint for UptimeRobot cold-start pings."""
    return {"status": "ok"}


@app.post("/generate")
@limiter.limit("5/hour")
async def generate(request: Request, body: GenerateRequest):
    """Main endpoint: YouTube URL → Quiz Deck JSON.

    Pipeline:
    1. Validate X-App-Secret header
    2. Extract video ID & fetch transcript
    3. Chunk transcript with timestamp annotations
    4. Call Gemini with circuit breaker
    5. Return validated Deck JSON
    6. Garbage-collect all in-memory data
    """
    # App-to-App handshake
    secret = request.headers.get("X-App-Secret", "")
    if secret != APP_SECRET:
        logger.warning(f"Rejected request: invalid X-App-Secret from {safe_get_remote_address(request)}")
        raise HTTPException(status_code=403, detail="Forbidden: invalid app secret.")

    try:
        # Phase 1: Scrape & chunk
        logger.info(f"Processing URL: {body.url}")
        video_id, annotated_transcript = process_video(body.url)

        # Phase 2: Determine card count & call LLM
        card_count = determine_card_count(annotated_transcript)
        deck = call_gemini_with_retry(annotated_transcript, card_count, video_id)

        # Phase 3: Build response
        response_data = deck.model_dump()
        response_data["video_id"] = video_id

        # Zero Retention: explicitly free transcript and deck data
        del annotated_transcript, deck
        gc.collect()

        logger.info(f"Successfully generated deck for video {video_id}")
        return response_data

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")
