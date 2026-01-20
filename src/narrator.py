import os
import requests
from openai import OpenAI
from .config import ELEVENLABS_API_KEY, OPENAI_API_KEY

class AudioEngine:
    def __init__(self):
        self.eleven_key = ELEVENLABS_API_KEY
        self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
        # Default Voice ID (Adam - Serious Male)
        self.voice_id = "pNInz6obpgDQGcFmaJgB" 

    def generate_voice(self, text: str, job_dir: str, voice_style: str = "serious_male") -> str:
        filepath = os.path.join(job_dir, "voiceover.mp3")
        
        # Try ElevenLabs first
        if self.eleven_key:
            try:
                print("[*] Narrator: Using ElevenLabs...")
                return self._generate_elevenlabs(text, filepath)
            except Exception as e:
                print(f"[!] ElevenLabs Failed: {e}. Falling back to OpenAi.")
        
        # Fallback to OpenAI
        print("[*] Narrator: Using OpenAI TTS...")
        return self._generate_openai_tts(text, filepath)

    def _generate_elevenlabs(self, text: str, filepath: str) -> str:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.eleven_key
        }
        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
        }
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                f.write(response.content)
            return filepath
        else:
            raise Exception(f"Status {response.status_code}: {response.text}")

    def _generate_openai_tts(self, text: str, filepath: str) -> str:
        response = self.openai_client.audio.speech.create(
            model="tts-1",
            voice="onyx", # Deep/Serious male equivalent
            input=text
        )
        response.stream_to_file(filepath)
        return filepath
