from google.cloud import storage

def upload_to_bucket(source_file_path, destination_file_name=None):
    """Upload a file to the audio-voice-vpay bucket."""
    
    # Initialize the client
    storage_client = storage.Client()
    
    # Get the bucket
    bucket = storage_client.bucket('audio-voice-vpay')
    
    # Use original filename if destination not specified
    if destination_file_name is None:
        import os
        destination_file_name = os.path.basename(source_file_path)
    
    # Create blob and upload
    blob = bucket.blob(destination_file_name)
    blob.upload_from_filename(source_file_path)
    
    # Fixed the print statement to match actual upload path
    print(f"File {source_file_path} uploaded to audio-voice-vpay/{destination_file_name}")
    return f"gs://audio-voice-vpay/{destination_file_name}"

# Usage examples
upload_to_bucket("../prototype/Voice1.mp3")  # Uploads as "Voice1.mp3"
#upload_to_bucket("../prototype/Voice1.mp3", "recordings/audio_2024.mp3")  # Custom path