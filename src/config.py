import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.1-8b-instant")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

_client = None

def get_client():
    global _client
    if _client is None:
        from groq import Groq
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not found in environment variables.")
        _client = Groq(api_key=GROQ_API_KEY)
    return _client
