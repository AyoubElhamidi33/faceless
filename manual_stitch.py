import os
import json
from src.editor import VideoEditor

JOB_ID = "golden_1768975446"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JOB_DIR = os.path.join(BASE_DIR, "outputs", JOB_ID)

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def run():
    print(f"[*] Starting Manual Stitch for {JOB_ID}...")
    
    # 1. Load Data
    script_path = os.path.join(JOB_DIR, "script.json")
    if not os.path.exists(script_path):
        print(f"[!] Script missing: {script_path}")
        return
        
    script_data = load_json(script_path)
    
    # 2. Load Configs
    caption_style_path = os.path.join(BASE_DIR, "caption_styles", "center_wordbeats.json")
    caption_style = load_json(caption_style_path)
    
    # 3. Assets
    audio_path = os.path.join(JOB_DIR, "voiceover.mp3")
    image_paths = [os.path.join(JOB_DIR, f"scene_{i:02d}.png") for i in range(1, 17)]
    
    for img in image_paths:
        if not os.path.exists(img):
            print(f"[!] Missing image: {img}")
            # Try thumb override if still missing (though I copied them)
            # But script should fail if missing.
            return

    output_path = os.path.join(JOB_DIR, "final_video_manual.mp4")
    
    # 4. Assemble
    editor = VideoEditor()
    mood = script_data.get("music_mood", "dark_ambient")
    
    print(f"[*] Assembling to {output_path}...")
    editor.assemble_video(
        image_paths=image_paths,
        audio_path=audio_path,
        output_path=output_path,
        music_mood=mood,
        caption_style=caption_style,
        script_data=script_data
    )
    print(f"[*] DONE! Video saved to {output_path}")

if __name__ == "__main__":
    run()
