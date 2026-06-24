import re

with open('backend/main.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Imports
code = code.replace('from google import genai', '')

import_insert = '''from fastapi.responses import JSONResponse
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part'''
code = code.replace('from fastapi.responses import JSONResponse', import_insert)

# 2. Remove genai initialization
genai_init = '''try:
    client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as e:
    logger.warning(f"Failed to initialize Gemini Client: {e}")
    client = None'''
code = code.replace(genai_init, '')

# 3. Define the ADK Agent (global)
agent_def = '''MODEL_ID = "gemini-2.0-flash"

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

quiz_agent = Agent(
    name="quiz_generator",
    model=MODEL_ID,
    instruction=SYSTEM_PROMPT,
    output_schema=Deck
)'''

# Replace the old MODEL_ID and SYSTEM_PROMPT definitions
old_sys_prompt = '''MODEL_ID = "gemini-2.0-flash"

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
"""'''

code = code.replace(old_sys_prompt, agent_def)

# 4. Replace call_gemini_with_retry
old_call = '''def call_gemini_with_retry(
    transcript: str,
    card_count: int,
    video_id: str,
    language: str = "English",
    custom_client=None,
) -> Deck:
    """Call Gemini API with fallback models and hardcoded demo bypass.

    Returns a validated Deck object or raises HTTPException.
    """
    user_prompt = f"""Generate exactly {card_count} quiz cards from this transcript.
The quiz cards (question, correct_answer, distractors, explanation) MUST be written in the {language} language.
The JSON keys MUST remain in English.

Transcript:
{transcript}"""

    models_to_try = ["gemini-2.0-flash", "gemini-1.5-flash"]
    last_error = "Unknown error"

    active_client = custom_client if custom_client else client

    if active_client:
        for model_name in models_to_try:
            max_retries = 2
            for attempt in range(1, max_retries + 1):
                try:
                    logger.info(
                        f"Gemini attempt {attempt}/{max_retries} with {model_name}"
                    )
                    start = time.time()

                    response = active_client.models.generate_content(
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

    logger.error(f"All Gemini models failed. Last error: {last_error}")
    raise HTTPException(
        status_code=429,
        detail="AI Quota Exceeded. Please configure a custom API Key (BYOK) or Local AI in Settings.",
    )'''

new_call = '''async def call_agent_with_retry(
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
    )'''

code = code.replace(old_call, new_call)

# 5. Update generate endpoint to await call_agent_with_retry
old_endpoint_call = '''        custom_client = None
        if body.api_key:
            try:
                custom_client = genai.Client(api_key=body.api_key)
            except Exception as e:
                logger.warning(f"Failed to init custom Gemini client: {e}")

        deck = call_gemini_with_retry(
            annotated_transcript, card_count, video_id, body.language, custom_client
        )'''

new_endpoint_call = '''        deck = await call_agent_with_retry(
            annotated_transcript, card_count, video_id, body.language, body.api_key
        )'''

code = code.replace(old_endpoint_call, new_endpoint_call)

with open('backend/main.py', 'w', encoding='utf-8') as f:
    f.write(code)
