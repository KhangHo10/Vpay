from google.cloud import storage

def download_from_bucket(source_blob_name, destination_file_name):
    """Download a file from the audio-voice-vpay bucket."""
    
    storage_client = storage.Client()
    bucket = storage_client.bucket('audio-voice-vpay')
    blob = bucket.blob(source_blob_name)
    
    # Download to local file
    blob.download_to_filename(destination_file_name)
    
    print(f"Downloaded {source_blob_name} to {destination_file_name}")

# Usage
download_from_bucket("Voice1.mp3", "../prototype/Downloaded_Voice1.mp3")