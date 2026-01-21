import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

files = [
    r"c:\Users\DOVY\Desktop\REELS AUTOMATION\desired outcome\snaptik_7562875135926078742_v2.mp4",
    r"c:\Users\DOVY\Desktop\REELS AUTOMATION\desired outcome\snaptik_7562994351874542850_v2.mp4",
    r"c:\Users\DOVY\Desktop\REELS AUTOMATION\desired outcome\snaptik_7529262479646395670_v2.mp4",
    r"c:\Users\DOVY\Desktop\REELS AUTOMATION\desired outcome\snaptik_7530328275013373206_v2.mp4"
]

print("-" * 50)
print("🎙️ TRANSCRIBING REFERENCE VIDEOS 🎙️")
print("-" * 50)

for fpath in files:
    print(f"\n📂 File: {os.path.basename(fpath)}")
    try:
        with open(fpath, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file
            )
            print("📝 Transcript:")
            print(transcript.text)
            print("-" * 20)
    except Exception as e:
        print(f"❌ Error: {e}")
