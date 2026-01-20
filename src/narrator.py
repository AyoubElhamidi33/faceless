import os
import requests
from .config import ELEVENLABS_API_KEY, VOICE_ID, TEMP_DIR

class AudioEngine:
    def __init__(self):
        self.api_key = ELEVENLABS_API_KEY
        self.voice_id = VOICE_ID
        self.url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"

    def generate_voice(self, text: str) -> str:
        """
        Generates audio from text using ElevenLabs API.
        Returns the path to the saved MP3 file.
        """
        print("[*] Generating voiceover...")
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }

        try:
            response = requests.post(self.url, json=data, headers=headers)
            
            if response.status_code == 200:
                filepath = os.path.join(TEMP_DIR, "voiceover.mp3")
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                print("[*] Voiceover saved.")
                return filepath
            else:
                raise Exception(f"ElevenLabs API Error: {response.text}")
                
        except Exception as e:
            print(f"[!] Error generating voice: {e}")
            raise

if __name__ == "__main__":
    # Test
    narrator = AudioEngine()
    # narrator.generate_voice("This is a test of the emergency broadcast system.")
