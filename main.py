import os
import time
import json
import uuid
from src.config import OUTPUT_DIR
from src.writer import ScriptGenerator, TopicEngine
from src.artist import VisualEngine
from src.narrator import AudioEngine
from src.editor import VideoEditor
from src.validator import validate_api_keys

# CONFIG LOAD
def load_config(path):
    with open(path, 'r') as f:
        return json.load(f)

CHANNEL_CONF = load_config("channels/real_horror.json")
STYLE_NAME = CHANNEL_CONF.get("default_style", "polaroid_realism")
STYLE_CONF = load_config(f"styles/{STYLE_NAME}.json")
CAPTION_CONF = load_config("caption_styles/typewriter.json")

# RUN CONFIG
MODE = os.getenv("MODE", "batch") # batch or daemon
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "3"))
SLEEP_SEC = int(os.getenv("SLEEP_BETWEEN_RUNS_SEC", "1800"))

def run_job(job_id: str, topic_engine: TopicEngine):
    job_dir = os.path.join(OUTPUT_DIR, "outputs", job_id)
    os.makedirs(job_dir, exist_ok=True)
    
    print(f"\n==================================================")
    print(f"🚀 STARTING JOB: {job_id}")
    print(f"==================================================")

    # 1. Topic
    topic = topic_engine.get_fresh_topic()
    print(f"[*] Topic: {topic}")

    # 2. Script
    writer = ScriptGenerator()
    script_data = writer.generate_script(topic, STYLE_CONF)
    
    # Save Script
    with open(os.path.join(job_dir, "script.json"), 'w') as f:
        json.dump(script_data, f, indent=2)

    # 3. Images
    artist = VisualEngine()
    scenes = script_data.get("scenes", [])
    image_paths = artist.generate_images(scenes, STYLE_CONF, job_dir)

    # 4. Voice
    narrator = AudioEngine()
    script_text = script_data.get("script_text")
    audio_path = narrator.generate_voice(script_text, job_dir, CHANNEL_CONF.get("voice_style"))

    # 5. Assembly
    editor = VideoEditor()
    final_mp4 = os.path.join(job_dir, "final.mp4")
    
    music_mood = script_data.get("music_mood", CHANNEL_CONF.get("default_music_mood"))
    caption_style = CAPTION_CONF # could override from script_data if we wanted
    
    editor.assemble_video(image_paths, audio_path, final_mp4, music_mood, caption_style)
    
    print(f"✅ JOB COMPLETE: {final_mp4}")
    return final_mp4

def main():
    if not validate_api_keys():
        print("🛑 STOPPING: Fix API keys.")
        return

    # Init Engines
    topic_engine = TopicEngine(CHANNEL_CONF)
    
    if MODE == "batch":
        print(f"[*] Starting BATCH mode (Size: {BATCH_SIZE})...")
        for i in range(BATCH_SIZE):
            job_id = f"job_{int(time.time())}_{uuid.uuid4().hex[:4]}"
            try:
                run_job(job_id, topic_engine)
            except Exception as e:
                print(f"❌ JOB FAILED: {e}")
                import traceback
                traceback.print_exc()
            
    elif MODE == "daemon":
        print("[*] Starting DAEMON mode (Infinite Loop)...")
        while True:
            job_id = f"job_{int(time.time())}_{uuid.uuid4().hex[:4]}"
            try:
                run_job(job_id, topic_engine)
            except Exception as e:
                print(f"❌ JOB FAILED: {e}")
            
            print(f"[*] Sleeping for {SLEEP_SEC}s...")
            time.sleep(SLEEP_SEC)

if __name__ == "__main__":
    main()