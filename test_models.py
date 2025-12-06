import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Configure with API key
api_key = os.getenv('GOOGLE_API_KEY')
print(f'Using API key: {api_key[:10]}...')

genai.configure(api_key=api_key)

print('\nAvailable models:')
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f'  {model.name}')
