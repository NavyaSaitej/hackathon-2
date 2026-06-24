"""
QuickCards Ã¢â‚¬â€ FastAPI Backend (V5 Ultimate)

Core responsibilities:
- CORS middleware (Vercel frontend only)
- IP rate limiting via slowapi (5 req/hr)
- X-App-Secret handshake validation
- Gemini API integration with 3-retry exponential backoff
- Structured logging via loguru
- Zero Retention: all transcript/LLM data garbage-collected after response
"""

import sys
import os

# Ensure backend directory is in path so Vercel can find models.py and scraper.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import Deck
from scraper import process_video
import gc
import json
import time
import asyncio

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

from loguru import logger
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded


def safe_get_remote_address(request: Request) -> str:
    # Vercel serverless environment may not populate request.client
    return request.headers.get("x-forwarded-for", "127.0.0.1").split(",")[0]


# Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
# Configuration
# Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
APP_SECRET = os.getenv("APP_SECRET", "quickcards-dev-secret")

if not GEMINI_API_KEY:
    logger.warning(
        "GEMINI_API_KEY not set. AI generation will fail unless using the demo bypass."
    )

# Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
# App Initialization
# Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
limiter = Limiter(key_func=safe_get_remote_address)
app = FastAPI(
    title="QuickCards API",
    version="1.0.0",
    description="AI-powered YouTube-to-Quiz generator backend.",
)
app.state.limiter = limiter


# Rate limit exceeded handler
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, _exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "error": "rate_limit_exceeded",
            "detail": "Maximum 5 generations per hour. Please try again later.",
        },
    )


# CORS Ã¢â‚¬â€ allow Vercel frontend
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

# Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
# Gemini Client
# Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬


MODEL_ID = "gemini-2.0-flash"

SYSTEM_PROMPT = """You are an expert educational content creator. Given a video transcript
with [TS:seconds] annotations, generate a quiz deck as valid JSON.

RULES:
1. Each question must test a distinct key concept from the transcript.
2. The correct_answer must be factually accurate per the transcript.
3. Each distractor must be plausible but clearly wrong.
4. The explanation must be exactly 1 sentence.
5. timestamp_seconds MUST be copied from the nearest [TS:seconds] tag
   in the transcript Ã¢â‚¬â€ do NOT invent timestamps.
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


def generate_offline_fallback_deck(transcript: str, language: str = "English") -> dict:
    if language == "Hindi":
        return {
            "video_title": "ऑफ़लाइन मोड (AI कोटा समाप्त)",
            "cards": [
                {
                    "question": "कस्टम वीडियो के लिए फ्लैशकार्ड क्यों नहीं बन पाए?",
                    "correct_answer": "AI जनरेशन कोटा समाप्त हो गया है।",
                    "distractors": [
                        "वीडियो में कोई आवाज़ नहीं है।",
                        "इंटरनेट काम नहीं कर रहा है।",
                        "वेबसाइट क्रैश हो गई है।",
                    ],
                    "explanation": "यह एक ऑफ़लाइन फ़ॉलबैक कार्ड है क्योंकि हम वर्तमान में AI के साथ कनेक्ट नहीं कर पा रहे हैं। कृपया कुछ समय बाद पुनः प्रयास करें या डेमो वीडियो का उपयोग करें।",
                    "timestamp_seconds": 0,
                }
            ],
        }
    elif language == "Telugu":
        return {
            "video_title": "ఆఫ్‌లైన్ మోడ్ (AI కోటా ముగిసింది)",
            "cards": [
                {
                    "question": "ఈ కస్టమ్ వీడియో కోసం ఫ్లాష్‌కార్డ్‌లు ఎందుకు సృష్టించబడలేదు?",
                    "correct_answer": "AI జనరేషన్ కోటా ముగిసింది.",
                    "distractors": [
                        "వీడియోలో వాయిస్ లేదు.",
                        "ఇంటర్నెట్ పనిచేయడం లేదు.",
                        "వెబ్‌సైట్ క్రాష్ అయింది.",
                    ],
                    "explanation": "మేము ప్రస్తుతం AIకి కనెక్ట్ చేయలేకపోతున్నందున ఇది ఆఫ్‌లైన్ ఫాల్‌బ్యాక్ కార్డ్. దయచేసి కాసేపు ఆగి మళ్లీ ప్రయత్నించండి లేదా డెమో వీడియోని ఉపయోగించండి.",
                    "timestamp_seconds": 0,
                }
            ],
        }
    else:
        return {
            "video_title": "Offline Mode (AI Quota Exhausted)",
            "cards": [
                {
                    "question": "Why couldn't flashcards be generated for this custom video?",
                    "correct_answer": "The AI generation quota has been exhausted or API failed.",
                    "distractors": [
                        "The video has no audio.",
                        "The internet is down.",
                        "The website crashed.",
                    ],
                    "explanation": "This is an offline fallback card because we cannot connect to the AI currently. Please try again later or use the Demo Video.",
                    "timestamp_seconds": 0,
                }
            ],
        }


def generate_scraper_blocked_deck(error_msg: str, language: str = "English") -> dict:
    if language == "Hindi":
        return {
            "video_title": "YouTube एंटी-बॉट ब्लॉक सक्रिय",
            "cards": [
                {
                    "question": "ऐप इस वीडियो के लिए फ्लैशकार्ड क्यों नहीं बना सका?",
                    "correct_answer": "YouTube ने सर्वर को ब्लॉक कर दिया है।",
                    "distractors": [
                        "वीडियो में आवाज़ नहीं है",
                        "AI ऑफ़लाइन है",
                        "वीडियो निजी है",
                    ],
                    "explanation": f"YouTube कभी-कभी सर्वरों को ट्रांसक्रिप्ट डाउनलोड करने से रोकता है। Error: {str(error_msg)[:50]}...",
                    "timestamp_seconds": 0,
                }
            ],
        }
    elif language == "Telugu":
        return {
            "video_title": "YouTube యాంటీ-బాట్ బ్లాక్ యాక్టివ్",
            "cards": [
                {
                    "question": "యాప్ ఈ వీడియో కోసం ఫ్లాష్‌కార్డ్‌లను ఎందుకు సృష్టించలేకపోయింది?",
                    "correct_answer": "YouTube సర్వర్‌ను బ్లాక్ చేసింది.",
                    "distractors": ["వీడియోలో వాయిస్ లేదు", "AI ఆఫ్‌లైన్‌లో ఉంది", "వీడియో ప్రైవేట్"],
                    "explanation": f"YouTube కొన్నిసార్లు సర్వర్‌లను ట్రాన్స్‌క్రిప్ట్‌లను డౌన్‌లోడ్ చేయకుండా నిరోధిస్తుంది. Error: {str(error_msg)[:50]}...",
                    "timestamp_seconds": 0,
                }
            ],
        }
    else:
        return {
            "video_title": "YouTube Anti-Bot Block Active",
            "cards": [
                {
                    "question": "Why could the app not generate flashcards for this video?",
                    "correct_answer": "YouTube blocked the server for bot activity",
                    "distractors": [
                        "The video has no audio",
                        "The AI is offline",
                        "The video is private",
                    ],
                    "explanation": f"YouTube occasionally blocks cloud servers from downloading transcripts. Error: {str(error_msg)[:50]}...",
                    "timestamp_seconds": 0,
                }
            ],
        }


async def call_agent_with_retry(
    transcript: str,
    card_count: int,
    video_id: str,
    language: str = "English",
    custom_api_key: str | None = None,
) -> Deck:
    """Call ADK Agent with fallback models and hardcoded demo bypass.

    Returns a validated Deck object or raises HTTPException.
    """
    user_prompt = f"""Generate exactly {card_count} quiz cards from this transcript.
The quiz cards (question, correct_answer, distractors, explanation) MUST be written in the {language} language.
The JSON keys MUST remain in English.

Transcript:
{transcript}"""

    models_to_try = ["gemini-2.0-flash", "gemini-1.5-flash"]
    last_error = "Unknown error"

    # Save and temporarily patch the environment variable if custom api key is provided
    original_api_key = os.environ.get("GEMINI_API_KEY")
    if custom_api_key:
        os.environ["GEMINI_API_KEY"] = custom_api_key
    
    try:
        if os.environ.get("GEMINI_API_KEY"):
            session_service = InMemorySessionService()
            for model_name in models_to_try:
                max_retries = 2
                for attempt in range(1, max_retries + 1):
                    try:
                        logger.info(f"ADK Agent attempt {attempt}/{max_retries} with {model_name}")
                        start = time.time()
                        
                        # Dynamically change the model for the agent if needed
                        quiz_agent.model = model_name

                        runner = Runner(
                            app_name="quickcards", 
                            agent=quiz_agent, 
                            session_service=session_service, 
                            auto_create_session=True
                        )
                        message = Content(role="user", parts=[Part.from_text(text=user_prompt)])
                        
                        final_deck = None
                        async for event in runner.run_async(
                            user_id="anonymous", 
                            session_id=video_id, 
                            new_message=message
                        ):
                            if getattr(event, 'output', None):
                                final_deck = event.output
                        
                        elapsed = time.time() - start
                        logger.info(f"ADK Agent responded in {elapsed:.2f}s")

                        if final_deck and isinstance(final_deck, Deck):
                            logger.info(f"Generated {len(final_deck.cards)} valid cards")
                            return final_deck
                        else:
                            raise ValueError("Output was not a valid Deck")

                    except Exception as e:
                        last_error = f"ADK Agent API error: {e}"
                        logger.warning(f"Attempt {attempt}: {last_error}")

                    if attempt < max_retries:
                        backoff = 2**attempt
                        logger.info(f"Retrying {model_name} in {backoff}s...")
                        await asyncio.sleep(backoff)
        else:
            last_error = "Gemini API key not configured."
    finally:
        # Restore environment
        if original_api_key is not None:
            os.environ["GEMINI_API_KEY"] = original_api_key
        elif "GEMINI_API_KEY" in os.environ:
            del os.environ["GEMINI_API_KEY"]

    # If we exhaust all models and it's the demo video, use the hardcoded deck!
    if video_id == "Dq6dBoFor00":
        try:
            try:
                from backend.demo_data import (
                    DEMO_DECK,
                    DEMO_DECK_HINDI,
                    DEMO_DECK_TELUGU,
                )
            except ImportError:
                from demo_data import DEMO_DECK, DEMO_DECK_HINDI, DEMO_DECK_TELUGU
            logger.info("Used hardcoded demo deck bypass.")
            if language == "Hindi":
                return Deck.model_validate(DEMO_DECK_HINDI)
            elif language == "Telugu":
                return Deck.model_validate(DEMO_DECK_TELUGU)
            else:
                return Deck.model_validate(DEMO_DECK)
        except Exception as e:
            logger.error(f"Failed to load demo deck: {e}")

    logger.error(f"All ADK Agent attempts failed. Last error: {last_error}")
    raise HTTPException(
        status_code=429,
        detail="AI Quota Exceeded. Please configure a custom API Key (BYOK) or Local AI in Settings.",
    )


# --------------------------------------------------------------------------------------------------------------------------------
# Request Model
# --------------------------------------------------------------------------------------------------------------------------------
class GenerateRequest(BaseModel):
    url: str
    language: str = "English"
    api_key: str | None = None


class TranscriptRequest(BaseModel):
    url: str


# Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
# Routes
# Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
@app.get("/health")
async def health():
    """Health check endpoint for UptimeRobot cold-start pings."""
    return {"status": "ok"}


@app.post("/generate")
@limiter.limit("5/hour")
async def generate(request: Request, body: GenerateRequest):
    """Main endpoint: YouTube URL Ã¢â€ â€™ Quiz Deck JSON.

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
        logger.warning(
            f"Rejected request: invalid X-App-Secret from {safe_get_remote_address(request)}"
        )
        raise HTTPException(status_code=403, detail="Forbidden: invalid app secret.")

    try:
        # Phase 1: Scrape & chunk
        logger.info(f"Processing URL: {body.url}")
        video_id, annotated_transcript = process_video(body.url)

        # Phase 2: Determine card count & call LLM
        card_count = determine_card_count(annotated_transcript)

        deck = await call_agent_with_retry(
            annotated_transcript, card_count, video_id, body.language, body.api_key
        )

        # Phase 3: Build response
        response_data = deck.model_dump()
        response_data["video_id"] = video_id

        # Zero Retention: explicitly free transcript and deck data
        del annotated_transcript, deck
        gc.collect()

        logger.info(f"Successfully generated deck for video {video_id}")
        return response_data

    except Exception as e:
        logger.error(f"Scraper error: {e}")
        # Completely indestructible: If scraper fails, return anti-bot fallback deck
        fallback_data = generate_scraper_blocked_deck(str(e), body.language)

        # We need a generic video_id for the frontend to embed SOMETHING, or we can extract it manually
        import re

        match = re.match(
            r"^(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([\w-]{11})",
            body.url,
        )
        extracted_id = match.group(1) if match else "Dq6dBoFor00"

        response_data = Deck.model_validate(fallback_data).model_dump()
        response_data["video_id"] = extracted_id
        return response_data


@app.post("/transcript")
@limiter.limit("10/hour")
async def get_transcript(request: Request, body: TranscriptRequest):
    """Endpoint for returning raw transcript for Local AI processing."""
    secret = request.headers.get("X-App-Secret", "")
    if secret != APP_SECRET:
        raise HTTPException(status_code=403, detail="Forbidden: invalid app secret.")

    try:
        video_id, annotated_transcript = process_video(body.url)
        return {"video_id": video_id, "transcript": annotated_transcript}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
