import os
from dotenv import load_dotenv
from google import genai

# Load .env file jika ada
load_dotenv()

# Lokasi Direktori
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
TRANSCRIPT_DIR = os.path.join(DATA_DIR, "transcripts")
CONTEXT_DIR = os.path.join(DATA_DIR, "context")

# Konfigurasi AI
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
MODEL_NAME = "gemini-1.5-flash"

_client = None

def get_client() -> genai.Client:
    global _client
    if _client is None:
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found in environment variables.")
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client

def ensure_dirs():
    """Memastikan semua direktori yang diperlukan ada."""
    for d in [TRANSCRIPT_DIR, CONTEXT_DIR, os.path.join(CONTEXT_DIR, "cv_batch")]:
        if not os.path.exists(d):
            os.makedirs(d)

# Jalankan pemastian direktori
ensure_dirs()