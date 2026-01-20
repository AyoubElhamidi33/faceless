import os
import requests
from openai import OpenAI
from .config import OPENAI_API_KEY, ELEVENLABS_API_KEY

def validate_api_keys():
    print("------------------------------------------------")
    print("🔐 VALIDATING API KEYS...")
    print("------------------------------------------------")
    
    # 1. Check if keys exist in Envs
    if not OPENAI_API_KEY:
        print("❌ [FAIL] OPENAI_API_KEY is missing from environment/config.")
        return False
    if not ELEVENLABS_API_KEY:
        print("❌ [FAIL] ELEVENLABS_API_KEY is missing from environment/config.")
        return False

    # 2. Test OpenAI
    print(f"[*] Testing OpenAI Key... (First 5 chars: {OPENAI_API_KEY[:5]}...)")
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        client.models.list()
        print("✅ [PASS] OpenAI API Key is valid.")
    except Exception as e:
        print(f"❌ [FAIL] OpenAI connection failed: {e}")
        return False

    # 3. Test ElevenLabs
    print(f"[*] Testing ElevenLabs Key... (First 5 chars: {ELEVENLABS_API_KEY[:5]}...)")
    try:
        headers = {"xi-api-key": ELEVENLABS_API_KEY}
        r = requests.get("https://api.elevenlabs.io/v1/user", headers=headers)
        if r.status_code == 200:
            print("✅ [PASS] ElevenLabs API Key is valid.")
        else:
            print(f"❌ [FAIL] ElevenLabs rejected key. Status: {r.status_code}, Response: {r.text}")
            return False
    except Exception as e:
        print(f"❌ [FAIL] ElevenLabs connection failed: {e}")
        return False

    print("------------------------------------------------")
    return True
