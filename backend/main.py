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

# Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
# Configuration
# Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
APP_SECRET = os.getenv("APP_SECRET", "quickcards-dev-secret")

if not GEMINI_API_KEY:
    logger.warning("GEMINI_API_KEY not set. AI generation will fail unless using the demo bypass.")

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
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
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
try:
    client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as e:
    logger.warning(f"Failed to initialize Gemini Client: {e}")
    client = None
    
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


import re
import random

def generate_offline_fallback_deck(transcript: str) -> dict:
    # Generate a primitive rule-based deck from the transcript when AI fails.
    blocks = transcript.split('\n\n')
    cards = []
    
    all_words = re.findall(r'\b[a-zA-Z]{5,}\b', transcript.lower())
    if len(all_words) < 10:
        all_words = ['Algorithm', 'Function', 'Variable', 'System', 'Data']
        
    for block in blocks:
        if not block.strip():
            continue
            
        ts_match = re.search(r'\[TS:(\d+)\]', block)
        ts = int(ts_match.group(1)) if ts_match else 0
        
        text = re.sub(r'\[TS:\d+\]', '', block).strip()
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20]
        
        for sentence in sentences:
            words = re.findall(r'\b[a-zA-Z]+\b', sentence)
            if not words: continue
            
            longest_word = max(words, key=len)
            if len(longest_word) < 5:
                continue
                
            question_text = sentence.replace(longest_word, '_____', 1) + '?'
            
            distractors = random.sample(all_words, min(3, len(all_words)))
            distractors = [d.capitalize() for d in distractors if d.lower() != longest_word.lower()]
            while len(distractors) < 3:
                distractors.append(random.choice(['Concept', 'Method', 'Process', 'Theory']))
                
            cards.append({
                'question': question_text.strip().capitalize(),
                'correct_answer': longest_word,
                'distractors': distractors[:3],
                'explanation': 'Offline Fallback: AI quota exhausted. This card was auto-generated via rule-based extraction.',
                'timestamp_seconds': ts
            })
            
            if len(cards) >= 5:
                break
        if len(cards) >= 5:
            break
            
    if not cards:
        cards.append({
            'question': 'Offline Mode Active: AI Quota Exhausted',
            'correct_answer': 'Acknowledge',
            'distractors': ['Retry', 'Error', 'Fail'],
            'explanation': 'The AI service is unavailable and the transcript was too short for rule-based generation.',
            'timestamp_seconds': 0
        })
        
    return {
        'video_title': 'Offline Fallback Deck',
        'cards': cards
    }

def generate_scraper_blocked_deck(error_msg: str) -> dict:
    return {
        'video_title': 'YouTube Anti-Bot Block Active',
        'cards': [
            {
                'question': 'Why could the app not generate flashcards for this video?',
                'correct_answer': 'YouTube blocked the server for bot activity',
                'distractors': ['The video has no audio', 'The AI is offline', 'The video is private'],
                'explanation': f'YouTube occasionally blocks cloud servers from downloading transcripts. Error: {str(error_msg)[:100]}...',
                'timestamp_seconds': 0
            },
            {
                'question': 'How can you fix this issue?',
                'correct_answer': 'Try the Demo Video or wait for the IP ban to lift',
                'distractors': ['Refresh the page 100 times', 'Buy a new computer', 'Uninstall your browser'],
                'explanation': 'IP bans on serverless functions usually rotate or lift over time. The hardcoded Demo Video will always work.',
                'timestamp_seconds': 0
            }
        ]
    }


def call_gemini_with_retry(transcript: str, card_count: int, video_id: str) -> Deck:
    """Call Gemini API with fallback models and hardcoded demo bypass.

    Returns a validated Deck object or raises HTTPException.
    """
    user_prompt = f"""Generate exactly {card_count} quiz cards from this transcript:

{transcript}"""

    models_to_try = ["gemini-2.0-flash", "gemini-1.5-flash"]
    last_error = "Unknown error"

    if client:
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
    else:
        last_error = "Gemini client not initialized (missing API key)."

    # If we exhaust all models and it's the demo video, use the hardcoded deck!
    if video_id == "Dq6dBoFor00":
        try:
            try:
                from backend.demo_data import DEMO_DECK
            except ImportError:
                from demo_data import DEMO_DECK
            logger.info("Used hardcoded demo deck bypass.")
            return Deck.model_validate(DEMO_DECK)
        except Exception as e:
            logger.error(f"Failed to load demo deck: {e}")

    logger.warning("AI generation failed or quota exhausted. Using offline rule-based fallback.")
    offline_data = generate_offline_fallback_deck(transcript)
    return Deck.model_validate(offline_data)


# Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
# Request Model
# Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
class GenerateRequest(BaseModel):
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

    except Exception as e:
        logger.error(f"Scraper error: {e}")
        # Completely indestructible: If scraper fails, return anti-bot fallback deck
        fallback_data = generate_scraper_blocked_deck(str(e))
        
        # We need a generic video_id for the frontend to embed SOMETHING, or we can extract it manually
        import re
        match = re.match(r"^(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([\w-]{11})", body.url)
        extracted_id = match.group(1) if match else "Dq6dBoFor00"
        
        response_data = Deck.model_validate(fallback_data).model_dump()
        response_data["video_id"] = extracted_id
        return response_data
