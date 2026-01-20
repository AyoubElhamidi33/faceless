import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

if not OPENAI_API_KEY:
    print("Warning: OPENAI_API_KEY not found in environment variables.")

if not ELEVENLABS_API_KEY:
    print("Warning: ELEVENLABS_API_KEY not found in environment variables.")

# Constants
VIDEO_ASPECT_RATIO = (9, 16)
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
VOICE_ID = "21m00Tcm4TlvDq8ikWAM" # Placeholder (Rachel - defaults often work well)
FONT_PATH = "arial.ttf" # Placeholder, ensure this exists or use system font
TEMP_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "temp")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)))

# Ensure temp dir exists
os.makedirs(TEMP_DIR, exist_ok=True)
