from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the expected request model to match your frontend
class AudioRequest(BaseModel):
    audio_data: str
    audio_format: str
    sample_rate: int

# Define response model (optional but good practice)
class AudioResponse(BaseModel):
    transcript: str | None = None
    payment_result: dict | None = None
    message: str

@app.post("/obtain_audio")  
async def obtain_audio(audio_request: AudioRequest):
    # Log the received data for debugging
    print(f"Received audio format: {audio_request.audio_format}")
    print(f"Sample rate: {audio_request.sample_rate}")
    print(f"Audio data length: {len(audio_request.audio_data)}")
    
    # For now, return a mock response to test the connection
    return AudioResponse(
        transcript="Mock transcript: Payment request received",
        payment_result={
            "status": "success",
            "amount": 2000,  # $20.00 in cents
            "recipient": "Test Recipient"
        },
        message="Audio received successfully"
    )

# Add a simple health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Optional: Add a test endpoint to verify server is running
@app.get("/")
async def root():
    return {"message": "Voice Payment API is running"}