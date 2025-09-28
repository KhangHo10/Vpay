# Suppress the ALTS warning
import os
import logging

os.environ['GRPC_VERBOSITY'] = 'ERROR'
os.environ['GLOG_minloglevel'] = '2'

# Optional: Suppress other Google Cloud logging
logging.getLogger('google.cloud').setLevel(logging.ERROR)

from google.cloud import speech

def transcribe_file(speech_file):
    """Transcribe the given audio file."""
    client = speech.SpeechClient()

    with open(speech_file, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    
    # Updated config for MP3 files
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.MP3,
        sample_rate_hertz=44100,  # Common MP3 sample rate
        language_code="en-US",
        enable_automatic_punctuation=True,  # Optional: adds punctuation
    )

    try:
        response = client.recognize(config=config, audio=audio)

        if response.results:
            for result in response.results:
                print(f"Transcript: {result.alternatives[0].transcript}")
                print(f"Confidence: {result.alternatives[0].confidence}")
        else:
            print("No speech detected in the audio file.")
            
    except Exception as e:
        print(f"Error during transcription: {e}")

# If you want to test the function, use this instead:
if __name__ == "__main__":
    # This only runs when you execute this file directly with: python voice_transcribe.py
    transcribe_file("../prototype/Voice1.mp3")