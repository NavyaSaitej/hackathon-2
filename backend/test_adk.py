import asyncio
from pydantic import BaseModel
from dotenv import load_dotenv

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.models import Gemini
from google.genai.types import Content, Part

load_dotenv()


class TestOutput(BaseModel):
    message: str
    word_count: int


async def main():
    # Pass a fake api key to test failure
    custom_model = Gemini(model_name="gemini-2.0-flash", api_key="fake-key")
    agent = Agent(
        name="test_agent",
        model=custom_model,
        instruction="You are a helpful assistant. Always output JSON matching the schema.",
        output_schema=TestOutput,
    )
    session_service = InMemorySessionService()
    runner = Runner(
        app_name="test_app",
        agent=agent,
        session_service=session_service,
        auto_create_session=True,
    )
    message = Content(role="user", parts=[Part.from_text(text="Say hi in 5 words")])
    try:
        async for event in runner.run_async(
            user_id="test_user", session_id="test_session", new_message=message
        ):
            print("Event type:", type(event))
    except Exception as e:
        print("Caught exception:", type(e))


if __name__ == "__main__":
    asyncio.run(main())
