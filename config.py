import os

# API KEYS
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")

# STUDIO CONFIG
PREMIUM_MODE = True # HARD LOCK: Enforce CLIP and specific models
