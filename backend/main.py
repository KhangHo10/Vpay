from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import base64
import io
import speech_recognition as sr
from google.cloud import speech
import tempfile
import os

app = FastAPI()

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Define the expected request model to match your frontend
class AudioRequest(BaseModel):
    audio_data: str
    audio_format: str
    sample_rate: int

# Define response model
class AudioResponse(BaseModel):
    transcript: str | None = None
    payment_result: dict | None = None
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
        
        # Try direct Google Cloud Speech with WebM
        print("Attempting direct WebM recognition with Google Cloud Speech...")
        
        # Initialize Google Cloud Speech client
        client = speech.SpeechClient()
        
        # Try WebM/Opus encoding first
        audio = speech.RecognitionAudio(content=audio_bytes)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
            sample_rate_hertz=48000,  # WebM typically uses 48kHz
            language_code="en-US",
        )
        
        try:
            # Attempt WebM recognition
            response = client.recognize(config=config, audio=audio)
            
            # Extract the transcript
            transcript = ""
            for result in response.results:
                transcript += result.alternatives[0].transcript
            
            print(f"WebM Transcript: '{transcript}'")
            
            if transcript:
                return AudioResponse(
                    transcript=transcript,
                    payment_result=None,
                    message="Audio processed successfully with WebM"
                )
        
        except Exception as webm_error:
            print(f"WebM recognition failed: {str(webm_error)}")
            # Fall back to writing file and using speech_recognition
            
            # Write audio to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_file:
                temp_file.write(audio_bytes)
                temp_file_path = temp_file.name
            
            try:
                # Use speech_recognition library as fallback
                r = sr.Recognizer()
                with sr.AudioFile(temp_file_path) as source:
                    audio_data = r.record(source)
                
                # Use Google Cloud Speech via speech_recognition
                transcript = r.recognize_google_cloud(
                    audio_data,
                    language="en-US"
                )
                
                print(f"SpeechRecognition Transcript: '{transcript}'")
                
                return AudioResponse(
                    transcript=transcript if transcript else "No speech detected",
                    payment_result=None,
                    message="Audio processed successfully with SpeechRecognition fallback"
                )
                
            except Exception as sr_error:
                print(f"SpeechRecognition also failed: {str(sr_error)}")
                # Final fallback - basic Google recognition
                try:
                    transcript = r.recognize_google(audio_data)
                    print(f"Basic Google Transcript: '{transcript}'")
                    
                    return AudioResponse(
                        transcript=transcript if transcript else "No speech detected",
                        payment_result=None,
                        message="Audio processed with basic Google recognition"
                    )
                except Exception as final_error:
                    print(f"All recognition methods failed: {str(final_error)}")
                    raise final_error
            
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
            payment_result=None,
            message="Error processing audio"
        )

# Add a simple health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Optional: Add a test endpoint to verify server is running
@app.get("/")
async def root():
    return {"message": "Voice Payment API is running"}