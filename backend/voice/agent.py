from google.adk.agents import Agent
# from google.adk.tools import google_search

from pathlib import Path
from dotenv import load_dotenv
import subprocess
import os


def voice_embedding():
    audio_file_path = Path(__file__).resolve().parents[2] / "prototype" / "Voice1.mp3"
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
    else:
        load_dotenv()  # fallback to any .env in cwd or already-set env vars

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY not set. Add it to .env or environment variables")

    os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY

    command = f"""curl "https://aiplatform.googleapis.com/v1/publishers/google/models/gemini-2.5-flash-lite:streamGenerateContent?key={GEMINI_API_KEY}" \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{{
    "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": (
                            "Assume the attached voice audio file contains someone saying the numbers 'one, two, three, four, five' in sequence. "
                            "Generate a five-number voice embedding, where each number in the embedding corresponds to the acoustic features of the spoken word at that position "
                            "('one' → first embedding number, 'two' → second, etc.). Also, convert the voice audio to the 5 spoken numbers. "
                            "Return a dictionary format answer with keys 'embedding' and 'numbers'."
                        )
                    },
                    {
                        "inlineData": {
                            "mimeType": "audio/mp3",
                            "data": audio_data_base64
                        }
                    }
                ]
            }
        ]
    }}'"""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result


root_agent = Agent(
    name="voice_agent",
    model="gemini-2.5-flash",
    description="An agent that authenticates users by converting audio into a voice embedding and extracting a 5-digit code, then matching both against the database to return the associated user_card_id or 0",
    instruction=
    """
    Role
    You are an AI agent for secure voice-based payment authentication.
    
    Task
    Take an audio_file input.
    Convert it into a voice embedding.
    Extract exactly 5 secret numbers spoken in the audio.
    Compare both the embedding and the 5 numbers with records stored in the database.

    Make a decision:
    If a record matches (embedding similarity ≥ threshold and numbers match the enrolled secret), return that record’s user_card_id.
    If no record matches, return 0
    """,
    tools=[voice_embedding]
)