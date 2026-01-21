import os
import re
import requests
from openai import OpenAI
from moviepy.editor import concatenate_audioclips, AudioFileClip, AudioClip
import numpy as np
from .config import ELEVENLABS_API_KEY, OPENAI_API_KEY

class AudioEngine:
    def __init__(self):
        self.eleven_key = ELEVENLABS_API_KEY
        self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
        self.voice_id = "pNInz6obpgDQGcFmaJgB" 

    def generate_voice(self, text: str, job_dir: str, voice_style: str = "serious_male") -> tuple[str, list]:
        # Check for Silence Markers
        # Format: [SILENCE] or [SILENCE:1.5]
        parts = re.split(r'(\[SILENCE(?::[\d\.]+)?\])', text)
        
        clips = []
        temp_files = []
        metadata = []
        current_time = 0.0
        
        for i, part in enumerate(parts):
            if not part.strip(): continue
            
            # Check if Silence Marker
            silence_match = re.match(r'\[SILENCE(?::([\d\.]+))?\]', part)
            if silence_match:
                dur_str = silence_match.group(1)
                duration = float(dur_str) if dur_str else 1.0
                print(f"[*] Narrator: Inserting silence ({duration}s)...")
                # Create silent clip
                silence_clip = AudioClip(lambda t: [0, 0], duration=duration, fps=44100)
                clips.append(silence_clip)
                
                metadata.append({
                    "start": current_time,
                    "end": current_time + duration,
                    "text": "[SILENCE]",
                    "type": "silence"
                })
                current_time += duration
            else:
                # Text Chunk
                print(f"[*] Narrator: Generating chunk {i}...")
                chunk_path = os.path.join(job_dir, f"chunk_{i}.mp3")
                self._generate_single_chunk(part, chunk_path)
                if os.path.exists(chunk_path):
                    audio_clip = AudioFileClip(chunk_path)
                    clips.append(audio_clip)
                    temp_files.append(chunk_path)
                    
                    duration = audio_clip.duration
                    metadata.append({
                        "start": current_time,
                        "end": current_time + duration,
                        "text": part.strip(),
                        "type": "speech"
                    })
                    current_time += duration
        
        filepath = os.path.join(job_dir, "voiceover.mp3")
        
        if clips:
            final_audio = concatenate_audioclips(clips)
            final_audio.write_audiofile(filepath, fps=44100, codec='libmp3lame', verbose=False, logger=None)
        else:
            return filepath, []
            
        # Cleanup
        for f in temp_files:
            try: os.remove(f)
            except: pass
            
        return filepath, metadata

    def _generate_single_chunk(self, text: str, filepath: str):
        # Try ElevenLabs first
        if self.eleven_key:
            try:
                self._generate_elevenlabs(text, filepath)
                return
            except Exception as e:
                print(f"[!] ElevenLabs Chunk Failed: {e}. Falling back to OpenAi.")
        
        # Fallback to OpenAI
        self._generate_openai_tts(text, filepath)

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
            voice="onyx",
            input=text
        )
        response.stream_to_file(filepath)
        return filepath
