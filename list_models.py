import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

print("API Key Loaded:", api_key is not None)

client = genai.Client(api_key=api_key)

print("Fetching models...")

models = client.models.list()

count = 0

for model in models:
    print(model.name)
    count += 1

print(f"\nFound {count} models.")