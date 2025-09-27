from google.adk.agents import Agent


voice_agent = Agent(
    name="VoiceAgent",
    model="gemini-live-2.5-flash",
    description="An agent that authenticates users by converting audio into a voice embedding and extracting a 5-digit code, then matching both against the database to return the associated user_card_id or 0",
    instructions=
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
    tools=[]
)

