import vertexai
from vertexai.preview.generative_models import GenerativeModel, Part
from pathlib import Path
from dotenv import load_dotenv
import base64
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
import mimetypes

# Load environment variables once at startup
load_dotenv()

class AudioProcessor:
    def __init__(self):
        # Initialize Vertex AI once
        self.PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
        self.LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
        vertexai.init(project=self.PROJECT, location=self.LOCATION)
        
        # Reuse model instance
        self.model = GenerativeModel('gemini-2.5-flash')
        
        # Thread pool for I/O operations
        self.executor = ThreadPoolExecutor(max_workers=4)

    def audio_to_base64_optimized(self, file_path):
        """Optimized audio to base64 conversion with proper MIME type detection"""
        file_path = Path(file_path)
        
        # Detect MIME type automatically
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type is None or not mime_type.startswith('audio/'):
            mime_type = 'audio/mp3'  # fallback
        
        # Read file efficiently
        with open(file_path, 'rb') as audio_file:
            encoded = base64.b64encode(audio_file.read()).decode('utf-8')
            return f"data:{mime_type};base64,{encoded}"

    def process_audio_direct(self, file_path):
        """Use direct file upload instead of base64 if supported"""
        try:
            # Try direct file approach first (more efficient)
            audio_part = Part.from_data(
                data=Path(file_path).read_bytes(),
                mime_type=mimetypes.guess_type(str(file_path))[0] or 'audio/mp3'
            )
            
            response = self.model.generate_content([
                "Extract the 5 secret numbers from this audio file:",
                audio_part
            ])
            return response.text
            
        except Exception as e:
            print(f"Direct upload failed, falling back to base64: {e}")
            return self.process_audio_base64(file_path)

    def process_audio_base64(self, file_path):
        """Fallback base64 method"""
        base64_audio = self.audio_to_base64_optimized(file_path)
        
        response = self.model.generate_content([
            'Extract the 5 secret numbers from this audio file:',
            base64_audio
        ])
        return response.text

    async def process_audio_async(self, file_path):
        """Async version for handling multiple files"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor, 
            self.process_audio_direct, 
            file_path
        )

    def process_with_enhanced_prompt(self, file_path):
        """Enhanced prompt for better accuracy with JSON output"""
        try:
            audio_part = Part.from_data(
                data=Path(file_path).read_bytes(),
                mime_type=mimetypes.guess_type(str(file_path))[0] or 'audio/mp3'
            )
            
            enhanced_prompt = """
            Carefully analyze this audio file and extract exactly 5 secret numbers.
            
            Instructions:
            - Listen for spoken numbers, spelled-out numbers, or encoded numbers
            - Pay attention to background sounds, reversed audio, or hidden layers
            - Look for patterns like DTMF tones, morse code, or frequency-encoded data
            - Return ONLY valid JSON format with no additional text or explanation
            
            Required JSON format:
            {"numbers": [number1, number2, number3, number4, number5]}
            
            Example: {"numbers": [7, 42, 13, 89, 5]}
            """
            
            response = self.model.generate_content([enhanced_prompt, audio_part])
            return self.parse_json_response(response.text)
            
        except Exception as e:
            print(f"Enhanced processing failed: {e}")
            return self.process_audio_direct(file_path)
    
    def parse_json_response(self, response_text):
        """Parse and validate JSON response"""
        import json
        import re
        
        try:
            # Try to parse directly first
            return json.loads(response_text.strip())
        except json.JSONDecodeError:
            # Extract JSON from response if wrapped in other text
            json_match = re.search(r'\{[^}]*"numbers"[^}]*\}', response_text)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass
            
            # Fallback: extract numbers and format as JSON
            numbers = re.findall(r'\b\d+\b', response_text)
            if numbers:
                return {"numbers": [int(n) for n in numbers[:5]]}
            
            return {"numbers": [], "error": "Could not extract numbers"}
    
    def process_json_output(self, file_path):
        """Simple method that returns JSON format"""
        try:
            audio_part = Part.from_data(
                data=Path(file_path).read_bytes(),
                mime_type=mimetypes.guess_type(str(file_path))[0] or 'audio/mp3'
            )
            
            prompt = '''Extract exactly 5 secret numbers from this audio file. 
            Return only this JSON format: {"numbers": [num1, num2, num3, num4, num5]}'''
            
            response = self.model.generate_content([prompt, audio_part])
            return self.parse_json_response(response.text)
            
        except Exception as e:
            return {"numbers": [], "error": str(e)}

# Usage examples
def main():
    processor = AudioProcessor()
    
    # Method 1: JSON output (recommended)
    result = processor.process_json_output('../prototype/Voice1.mp3')
    print("JSON result:", result)
    
    # Access the numbers array
    if 'numbers' in result:
        numbers = result['numbers']
        print(f"Extracted numbers: {numbers}")
    
    # Method 2: Enhanced prompt with JSON
    # result = processor.process_with_enhanced_prompt('../prototype/Voice1.mp3')
    # print("Enhanced JSON result:", result)
    
    # Method 3: Direct processing (returns text, not JSON)
    # result = processor.process_audio_direct('../prototype/Voice1.mp3')
    # print("Direct result:", result)

if __name__ == "__main__":
    main()