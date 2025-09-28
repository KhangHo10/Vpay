from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import base64
import tempfile
import os
import sys
from pathlib import Path
import json

# Add your agents directory to the path
sys.path.insert(0, str(Path(__file__).parent))

# Import your agents based on your directory structure
from voiceF.agent import root_agent as transcribe_agent
# TODO: Add other agents once imports are fixed
# from voice.agent import root_agent as voice_agent  
# from payment.agent import root_agent as payment_agent

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Define models
class AudioRequest(BaseModel):
    audio_data: str
    audio_format: str
    sample_rate: int

class AudioResponse(BaseModel):
    transcript: str | None = None
    # payment_result: dict | None = None
    # authentication_result: dict | None = None
    message: str

@app.post("/obtain_audio")  
async def obtain_audio(audio_request: AudioRequest):
    print(f"Received audio format: {audio_request.audio_format}")
    print(f"Sample rate: {audio_request.sample_rate}")
    print(f"Audio data length: {len(audio_request.audio_data)}")
    
    try:
        # Decode the base64 audio data
        audio_bytes = base64.b64decode(audio_request.audio_data)
        print(f"Decoded audio bytes length: {len(audio_bytes)}")
        
        # Save audio to temporary file for agent processing
        with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_file:
            temp_file.write(audio_bytes)
            temp_file_path = temp_file.name
        
        try:
            # Step 1 ONLY: Transcribe using your voice transcription agent
            print("Step 1: Transcribing audio with voiceF transcription agent...")
            
            # Try calling the agent's tool function directly instead of run_async
            try:
                # Import and call the transcription function directly
                from voiceF.agent import transcribe_voice_file
                
                print(f"Calling transcribe_voice_file directly with: {temp_file_path}")
                transcribe_response = transcribe_voice_file(temp_file_path)
                print(f"Direct function response: {transcribe_response}")
                
            except Exception as direct_error:
                print(f"Direct function call failed: {direct_error}")
                
                # If direct call fails, return error
                raise direct_error
            
            # Parse transcription result
            try:
                transcription_data = json.loads(transcribe_response)
                if transcription_data.get("success"):
                    transcript = transcription_data.get("transcript", "")
                    
                    # Log any confidence/accuracy metrics to console 
                    if "confidence" in transcription_data:
                        print(f"Transcription confidence: {transcription_data['confidence']}")
                    if "accuracy" in transcription_data:
                        print(f"Transcription accuracy: {transcription_data['accuracy']}")
                    if "quality_score" in transcription_data:
                        print(f"Audio quality score: {transcription_data['quality_score']}")
                    
                    # Log full response data for debugging (console only)
                    print(f"Full transcription data: {json.dumps(transcription_data, indent=2)}")
                    
                else:
                    transcript = transcription_data.get("error", "Transcription failed")
                    print(f"Transcription failed with error: {transcript}")
            except json.JSONDecodeError:
                # If not JSON, use the response directly
                transcript = transcribe_response
                print(f"Non-JSON response received: {transcript}")
            
            print(f"Clean transcript for frontend: '{transcript}'")
            
            return AudioResponse(
                transcript=transcript,
                message="Step 1 complete: Audio transcribed successfully"
            )
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        
    except Exception as e:
        print(f"Error processing audio: {str(e)}")
        import traceback
        traceback.print_exc()
        return AudioResponse(
            transcript=f"Error: {str(e)}",
            message="Error processing audio"
        )

def extract_recipient_from_transcript(transcript: str) -> str:
    """Extract recipient name from transcript - simple regex approach"""
    import re
    
    # Look for patterns like "to [name]" or "for [name]"
    patterns = [
        r'to\s+([a-zA-Z\s]+?)(?:\s|$)',
        r'for\s+([a-zA-Z\s]+?)(?:\s|$)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, transcript, re.IGNORECASE)
        if match:
            recipient = match.group(1).strip().title()
            # Clean up recipient name
            recipient = re.sub(r'[^\w\s]', '', recipient)
            return recipient
    
    return "Unknown Recipient"

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "agents": ["transcribe"]}

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Voice Payment API - Step 1 Testing (Transcription Only)"}

# Test endpoint for transcription agent only
@app.post("/test_agent/transcribe")
async def test_transcribe_agent(message: str):
    """Test transcription agent only"""
    try:
        response = ""
        async for chunk in transcribe_agent.run_async(message):
            response += str(chunk)
        return {"agent": "transcribe", "response": response}
    except Exception as e:
        return {"error": str(e)}