import sys
import os
import time
import json
import uuid

# Ensure we are running from project root
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from main import run_job, load_config
from src.topic_engine import TopicEngine
from src.writer import ScriptGenerator
from src.artist import VisualEngine
from src.validator import validate_api_keys

from src.validator import validate_pov_realism, validate_false_calm, validate_escalation_curve

# MOCK WRITER TO RETURN A VALID SCRIPT
def mock_generate_script(self, topic, style_profile):
    print("[*] INJECTING VALID MOCK SCRIPT FOR AUDIT...")
    vals = {
        "script_text": "I saw the dark water rising. I heard a scream. I felt cold. I decided to run. I was scared. [SILENCE:2.0] Then I saw the dam break. It was quiet. Then a rumble. Then silence again. Then the wave hit.",
        "fact_confidence": "high",
        "beat_words": ["I", "saw", "dark", "water"] * 15, # Dummy beats
        "scenes": [{"location": f"Loc {i}", "main_subject": "Dam"} for i in range(16)],
        "narrative_pov": "I saw",
        "iconic_scene_index": 5,
        "sticky_ending_line": "It was over.",
        "hook_text": "Did you know the dam failed?",
        "metadata": {},
        "variants": {"hook_b": "Hook B text."}
    }
    
    # EXPLICITLY RUN VALIDATORS FOR AUDIT LOGS
    print("\n--- [AUDIT START] VALIDATOR LOGS ---")
    validate_pov_realism(vals["script_text"], "I")
    validate_false_calm(vals["script_text"])
    validate_escalation_curve(vals["script_text"])
    print("--- [AUDIT END] VALIDATOR LOGS ---\n")
    
    return vals

# MOCK ARTIST TO BYPASS COMFYUI (OFFLINE)
def mock_generate_images(self, scenes, style, job_dir):
    print("[*] (Mock) VisualEngine: generating dummy images to allow pipeline continuation...")
    dummy_path = os.path.join(job_dir, "dummy_scene.jpg")
    # visual engine might need real files
    from PIL import Image
    img = Image.new('RGB', (1080, 1920), color='black')
    img.save(dummy_path)
    return [dummy_path] * len(scenes)

if __name__ == "__main__":
    print("[*] Validating Environment...")
    if not validate_api_keys():
        print("🛑 STOPPING: Fix API keys in .env or environment.")
        sys.exit(1)

    print("[*] Loading Configuration...")
    try:
        channel_conf = load_config("channels/comic_documentary_horror.json")
    except Exception as e:
        print(f"[!] Config Load Failed: {e}")
        sys.exit(1)
        
    print("[*] Initializing Topic Engine...")
    topic_engine = TopicEngine(channel_conf)
    
    # PATCH WRITER
    ScriptGenerator.generate_script = mock_generate_script
    
    # PATCH ARTIST - RESTORE REAL ENGINE FOR AUDIT
    # VisualEngine.generate_images = mock_generate_images
    
    job_id = f"v4_visual_audit_{int(time.time())}"
    print(f"[*] Starting Single Job with INJECTED SCRIPT + REAL IMAGES: {job_id}")
    
    try:
        run_job(job_id, topic_engine)
        print(f"\n✅ MANUAL RUN COMPLETE: {job_id}")
    except Exception as e:
        print(f"\n❌ RUN FAILED: {e}")
        import traceback
        traceback.print_exc()
