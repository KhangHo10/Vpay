import sys
import os
from pathlib import Path
from typing import Dict, List, Any

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from google.adk.agents import Agent
from tools.voice_to_embedded import get_audio_hash, generate_100d_voice_embedding, generate_hash_based_embedding
from tools.voice_to_number import AudioProcessor

# Create simple wrapper functions with proper type hints
def get_file_hash(audio_file_path: str) -> str:
    """
    Generate a hash of the audio file for consistency checking.
    
    Args:
        audio_file_path: Path to the audio file
        
    Returns:
        MD5 hash of the file as a string
    """
    return get_audio_hash(audio_file_path)

def generate_voice_embedding(audio_file_path: str) -> Dict[str, Any]:
    """
    Generate a 100-dimensional voice embedding from an audio file.
    
    Args:
        audio_file_path: Path to the audio file (MP3, WAV, etc.)
        
    Returns:
        Dictionary containing voice_embedding array and metadata
    """
    return generate_100d_voice_embedding(audio_file_path)

def extract_secret_numbers(audio_file_path: str) -> Dict[str, Any]:
    """
    Extract 5 secret numbers spoken in the audio file.
    
    Args:
        audio_file_path: Path to the audio file
        
    Returns:
        Dictionary with 'numbers' key containing list of 5 integers
    """
    processor = AudioProcessor()
    return processor.process_json_output(audio_file_path)

def process_voice_file(audio_file_path: str) -> Dict[str, Any]:
    """
    Complete voice authentication processing - generates embedding and extracts numbers.
    
    Args:
        audio_file_path: Path to the audio file to process
        
    Returns:
        Dictionary containing both voice embedding and extracted numbers
    """
    try:
        # Generate embedding
        embedding_result = generate_100d_voice_embedding(audio_file_path)
        
        # Extract numbers
        processor = AudioProcessor()
        numbers_result = processor.process_json_output(audio_file_path)
        
        # Get file hash
        file_hash = get_audio_hash(audio_file_path)
        
        return {
            "success": True,
            "voice_embedding": embedding_result.get("voice_embedding", []),
            "embedding_method": embedding_result.get("method", "unknown"),
            "extracted_numbers": numbers_result.get("numbers", []),
            "file_hash": file_hash,
            "dimensions": len(embedding_result.get("voice_embedding", []))
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "voice_embedding": [],
            "extracted_numbers": [],
            "file_hash": "",
            "dimensions": 0
        }

root_agent = Agent(
    name="voice_agent",
    model="gemini-2.5-flash",
    description="An agent that authenticates users by converting audio into a voice embedding and extracting a 5-digit code",
    instruction="""
    You are a voice authentication agent. Your job is to process audio files for user authentication.

    Available functions:
    1. process_voice_file(audio_file_path) - Complete processing (recommended)
    2. generate_voice_embedding(audio_file_path) - Generate voice embedding only
    3. extract_secret_numbers(audio_file_path) - Extract 5 numbers only
    4. get_file_hash(audio_file_path) - Get file hash for verification

    For voice authentication:
    1. Use process_voice_file() with the audio file path
    2. The function returns both voice embedding and extracted numbers
    3. Return the complete result in JSON format

    Example usage:
    - Call: process_voice_file("../prototype/Voice1.mp3")
    - Returns: Complete authentication data including embedding and numbers
    """,
    tools=[
        process_voice_file,
        generate_voice_embedding,
        extract_secret_numbers,
        get_file_hash
    ]
)
# Compare both the embedding and the 5 numbers with records stored in the database.

#     Make a decision:
#     If a record matches (embedding similarity ≥ threshold and numbers match the enrolled secret), return that record’s user_card_id.
#     If no record matches, return 0