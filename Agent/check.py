from dotenv import load_dotenv
import os

# Explicit full path to your .env
dotenv_path = r"C:\Users\AdityaJi\Agent\.env"
load_dotenv(dotenv_path)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
print("Loaded GEMINI_API_KEY:", GEMINI_API_KEY)
