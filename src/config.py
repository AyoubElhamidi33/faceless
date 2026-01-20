import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path)

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
# Voice IDs (ElevenLabs)
AVAILABLE_VOICES = {
    "Adam (Male, Deep Narration)": "pNInz6obpgDQGcFmaJgB",
    "Antoni (Male, Crisp)": "ErXwobaYiN019PkySvjV",
    "Rachel (Female, Standard)": "21m00Tcm4TlvDq8ikWAM",
    "Domi (Female, Strong)": "AZnzlk1XvdvUeBnXmlld"
}
VOICE_ID = "pNInz6obpgDQGcFmaJgB" # Default to Adam
FONT_PATH = "arial.ttf" # Placeholder, ensure this exists or use system font
# Backend Config
IMAGE_BACKEND = os.getenv("IMAGE_BACKEND", "openai") # 'openai' or 'comfyui'
CAPTION_BACKEND = os.getenv("CAPTION_BACKEND", "whisper") # 'whisper' (local) or 'openai_api' (not impl yet)

# DIRS
TEMP_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "temp")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)))

# Ensure temp dir exists
os.makedirs(TEMP_DIR, exist_ok=True)
