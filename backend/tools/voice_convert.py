import vertexai
from vertexai.preview.generative_models import GenerativeModel

from pathlib import Path
from dotenv import load_dotenv
import os

# The client automatically picks up credentials (ADC or Service Account JSON)
# based on the environment.
PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")

vertexai.init(project=PROJECT, location=LOCATION)

model = GenerativeModel('gemini-2.5-flash')
response = model.generate_content('What is the capital of Viet Nam?')

print(response.text)