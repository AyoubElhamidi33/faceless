import os
import sys
import time
import json
import uuid
import random
import traceback
from src.config import OUTPUT_DIR
from src.writer import ScriptGenerator
from src.topic_engine import TopicEngine
from src.storyboard_engine import build_storyboard
from src.artist import VisualEngine
from src.narrator import AudioEngine
from src.editor import VideoEditor
from src.validator import validate_api_keys
import src.preflight

# PREFLIGHT CHECK (Runs on Import/Start)
src.preflight.validate()

# CONFIG LOAD
def load_config(path):
    with open(path, 'r') as f:
        return json.load(f)

# STUDIO CONFIG
# STUDIO CONFIG
CHANNEL_CONF = load_config("channels/comic_documentary_horror.json")

# PATCH 0: CONFIG DRIFT FIX
STYLE_NAME = CHANNEL_CONF.get("style", CHANNEL_CONF.get("default_style", "consistent_comic"))
CAPTION_NAME = CHANNEL_CONF.get("caption_style", CHANNEL_CONF.get("default_caption_style", "center_wordbeats"))
MOOD = CHANNEL_CONF.get("music_mood", "dark_ambient")

STYLE_CONF = load_config(f"styles/{STYLE_NAME}.json")
CAPTION_CONF = load_config(f"caption_styles/{CAPTION_NAME}.json")

print(f"[*] Studio Config: Style='{STYLE_NAME}' | Caption='{CAPTION_NAME}' | Mood='{MOOD}'")


# STUDIO SETTINGS
SLEEP_SEC = int(os.getenv("SLEEP_BETWEEN_RUNS_SEC", "120"))
STATS_FILE = os.path.join(OUTPUT_DIR, "studio_stats.json")

def load_stats():
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, 'r') as f: return json.load(f)
    return {"jobs_run": 0, "failures": 0, "last_run": 0}

def save_stats(stats):
    with open(STATS_FILE, 'w') as f: json.dump(stats, f, indent=2)

def run_job(job_id: str, topic_engine: TopicEngine):
    job_dir = os.path.join(OUTPUT_DIR, "outputs", job_id)
    os.makedirs(job_dir, exist_ok=True)
    
    print(f"\n==================================================")
    print(f"🎬 STUDIO JOB: {job_id}")
    print(f"==================================================")

    # 1. Topic
    topic = topic_engine.get_fresh_topic()
    print(f"[*] Topic: {topic}")

    # 2. Script (v3)
    writer = ScriptGenerator()
    script_data = writer.generate_script(topic, STYLE_CONF)
    
    # PATCH 5: STORYBOARD ENGINE REFINEMENT
    print("[*] Storyboard Engine: Refining scenes with continuity & lighting...")
    refined_scenes = build_storyboard(script_data, STYLE_CONF)
    script_data["scenes"] = refined_scenes
    
    with open(os.path.join(job_dir, "script.json"), 'w') as f:
        json.dump(script_data, f, indent=2)

    # 3. Images (Common)
    artist = VisualEngine()
    current_style = STYLE_CONF.copy()
    current_style["base_seed"] = random.randint(100000, 999999999) 
    
    scenes = script_data.get("scenes", [])
    image_paths = artist.generate_images(scenes, current_style, job_dir)
    
    # 3.5 Thumbnails (Lock 27)
    artist.generate_thumbnails(topic, current_style, job_dir)

    # 4. A/B Testing Loops (Render Variants)
    narrator = AudioEngine()
    editor = VideoEditor()
    voice_style = CHANNEL_CONF.get("voice_style", "investigation_doc")
    music_mood = script_data.get("music_mood")
    
    # Variant A: Base
    print("[*] Rendering Variant A (Base)...")
    _render_variant(job_dir, "A", script_data["script_text"], image_paths, narrator, editor, voice_style, music_mood, CAPTION_CONF, script_data)
    
    # Variant B: Alt Hook
    variants = script_data.get("variants", {})
    if "hook_b" in variants:
        print("[*] Rendering Variant B (Alt Hook)...")
        base_hook = script_data["hook_text"]
        alt_hook = variants["hook_b"]
        
        # Simple replace (might be risky if hook repeats, but okay for v1)
        text_b = script_data["script_text"].replace(base_hook, alt_hook, 1)
        
        _render_variant(job_dir, "B", text_b, image_paths, narrator, editor, voice_style, music_mood, CAPTION_CONF, script_data)

    print(f"✅ JOB COMPLETE: {job_id}")

def _render_variant(job_dir, suffix, text, image_paths, narrator, editor, voice_style, music_mood, caption_conf, script_data):
    try:
        audio_name = f"voice_{suffix}.mp3"
        # PATCH 7: Unpack metadata
        audio_path, audio_metadata = narrator.generate_voice(text, job_dir, voice_style) 
        
        final_mp4 = os.path.join(job_dir, f"video_{suffix}.mp4")
        
        # Pass metadata to editor
        editor.assemble_video(image_paths, audio_path, final_mp4, music_mood, caption_conf, script_data, audio_metadata)
        print(f"   -> Generated {final_mp4}")
    except Exception as e:
        print(f"   [!] Variant {suffix} Error: {e}")

def main():
    if not validate_api_keys():
        print("🛑 STOPPING: Fix API keys.")
        return

    print("[*] Initializing Topic Engine v2...")
    topic_engine = TopicEngine(CHANNEL_CONF)
    
    stats = load_stats()
    print(f"[*] Studio Stats: {stats['jobs_run']} runs, {stats['failures']} failures.")
    print(f"[*] Studio Stats: {stats['jobs_run']} runs, {stats['failures']} failures.")
    print(f"[*] 🎥 STUDIO PRODUCTION MODE: Continuous Execution")
    
    while True:
        try:
            job_id = f"job_{int(time.time())}_{random.randint(10,99)}"
            run_job(job_id, topic_engine)
            
            stats["jobs_run"] += 1
            stats["last_run"] = time.time()
            save_stats(stats)
            
            print("[*] Job Complete. Cooling down 10s...")
            time.sleep(10)

        except KeyboardInterrupt:
            print("\n🛑 STOPPING STUDIO.")
            break
        except Exception as e:
            print(f"🔥 CRITICAL FAILURE: {e}")
            stats["failures"] += 1
            save_stats(stats)
            time.sleep(30)

if __name__ == "__main__":
    main()