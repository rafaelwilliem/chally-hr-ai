import os
from dotenv import load_dotenv

# Load .env file jika ada
load_dotenv()

# Lokasi Direktori
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
TRANSCRIPT_DIR = os.path.join(DATA_DIR, "transcripts")
CONTEXT_DIR = os.path.join(DATA_DIR, "context")

# Konfigurasi AI
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-1.5-flash"

def ensure_dirs():
    """Memastikan semua direktori yang diperlukan ada."""
    for d in [TRANSCRIPT_DIR, CONTEXT_DIR]:
        if not os.path.exists(d):
            os.makedirs(d)
