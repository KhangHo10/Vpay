from google.adk.agents import Agent
import sys
from pathlib import Path
import json
from typing import Optional

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from tools.voice_transcribe import transcribe_file
from tools.text_to_file import save_text_to_file

def transcribe_and_return(file_path: str) -> dict:
    """Modified transcription function that returns structured data."""
    try:
        import io
        from contextlib import redirect_stdout, redirect_stderr
        
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            transcribe_file(file_path)
        
        stdout_result = stdout_capture.getvalue()
        stderr_result = stderr_capture.getvalue()
        
        if stdout_result.strip():
            return {
                "success": True,
                "transcript": stdout_result.strip(),
                "file": file_path
            }
        else:
            return {
                "success": False,
                "error": stderr_result or "No speech detected",
                "file": file_path
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "file": file_path
        }

def transcribe_voice_file(file_path: str) -> str:
    """Transcribe an audio file to text."""
    result = transcribe_and_return(file_path)
    return json.dumps(result, indent=2)

def save_transcript_to_file(text: str, filename: Optional[str] = None) -> str:
    """Save text to a file in ../prototype directory."""
    result = save_text_to_file(text, filename)
    return json.dumps(result, indent=2)

def transcribe_and_save(file_path: str, filename: Optional[str] = None) -> str:
    """Transcribe audio and save to file in one step."""
    # Transcribe first
    transcription_result = transcribe_and_return(file_path)
    
    if not transcription_result["success"]:
        return json.dumps(transcription_result, indent=2)
    
    # Save the transcript
    save_result = save_text_to_file(transcription_result["transcript"], filename)
    
    # Combine results
    combined_result = {
        "transcription": transcription_result,
        "file_save": save_result,
        "success": transcription_result["success"] and save_result["success"]
    }
    
    return json.dumps(combined_result, indent=2)

root_agent = Agent(
    name="voice_transcribe_agent",
    model="gemini-2.5-flash",
    description="Voice transcription agent that converts audio to text and saves files",
    instruction="""
    You are a voice transcription agent with these capabilities:
    
    1. transcribe_voice_file(file_path) - Transcribe audio to text
    2. save_transcript_to_file(text, filename) - Save text to ../prototype/filename.txt
    3. transcribe_and_save(file_path, filename) - Do both in one step
    
    All files are saved to the ../prototype directory automatically.
    If no filename is provided, a timestamped filename will be generated.
    
    Always provide clear feedback about the results.
    """,
    tools=[transcribe_voice_file, save_transcript_to_file, transcribe_and_save]
)