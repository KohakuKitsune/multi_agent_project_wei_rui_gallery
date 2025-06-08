import os
from dotenv import load_dotenv
import openai

# Load .env file
load_dotenv()

# Read the key from environment
openai.api_key = os.getenv("OPENAI_API_KEY")

# Test print (optional)
print("API Key Loaded:", "Yes" if openai.api_key else "No")
print("OPENAI_API_KEY =", openai.api_key)