import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

# Define the default output directory relative to this file
DEFAULT_OUTPUT_DIR = Path(__file__).parent.parent / "prototype"

def save_text_to_file(text: str, filename: Optional[str] = None) -> Dict[str, Any]:
    """
    Save text content to a .txt file in the ../prototype directory.
    
    Args:
        text: The text content to save
        filename: Optional filename. If not provided, generates a timestamped filename.
    
    Returns:
        Dictionary with success status, file path, and any error messages
    """
    try:
        # Ensure prototype directory exists
        DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"transcript_{timestamp}.txt"
        
        # Ensure .txt extension
        if not filename.endswith('.txt'):
            filename += '.txt'
        
        # Create full path
        file_path = DEFAULT_OUTPUT_DIR / filename
        
        # Write text to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        return {
            "success": True,
            "file_path": str(file_path),
            "filename": filename,
            "message": f"Text saved to: {file_path}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Error saving text: {str(e)}"
        }

# Test function
if __name__ == "__main__":
    test_text = "This is a test transcription."
    result = save_text_to_file(test_text)
    print(f"Result: {result}")