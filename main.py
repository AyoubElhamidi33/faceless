import os
import json
from src.config import OUTPUT_DIR
from src.writer import ScriptGenerator
from src.artist import VisualEngine
from src.narrator import AudioEngine
from src.editor import VideoEditor

def main():
    print("=========================================")
    print("   PROMETHEUS - Faceless Video Studio    ")
    print("=========================================")

    # 1. Input
    topic = input("Enter video topic: ").strip()
    if not topic:
        print("[!] Topic cannot be empty.")
        return

    # 2. Script
    print("\n--- PHASE 1: SCRIPT ---")
    writer = ScriptGenerator()
    script_data = writer.generate_script(topic)
    
    script_text = script_data.get("script_text")
    scenes = script_data.get("scenes")
    
    if not script_text or not scenes:
        print("[!] Failed to generate valid script.")
        return
        
    print(f"\n[Script Quote]: \"{script_text[:50]}...\"")

    # 3. Voice
    print("\n--- PHASE 2: VOICE ---")
    narrator = AudioEngine()
    audio_path = narrator.generate_voice(script_text)

    # 4. Visuals
    print("\n--- PHASE 3: VISUALS ---")
    artist = VisualEngine()
    # Use keywords or just generic consistent character?
    # Let's extract a character trait if possible, or use default.
    image_paths = artist.generate_images(scenes)

    # 5. Editor
    print("\n--- PHASE 4: EDITING ---")
    output_path = os.path.join(OUTPUT_DIR, "output_video.mp4")
    editor = VideoEditor()
    editor.assemble_video(image_paths, audio_path, output_path)

    print("\n=========================================")
    print(f"DONE! Video saved to: {output_path}")
    print("=========================================")

if __name__ == "__main__":
    main()
