import sys
import os
import time

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.local_comfyui import generate_images

def test_single_smoke():
    print("\n💨 COMFYUI SMOKE TEST (Single Image) 💨")
    
    out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../assets/temp"))
    os.makedirs(out_dir, exist_ok=True)
    
    job_id = f"smoke_{int(time.time())}"
    prompts = ["Comic panel, close up of a glowing red eye, dramatic lighting, high contrast"]
    negative = "blurry, text, watermark"
    
    cfg = {
        "model": "revAnimated_v122EOL.safetensors",
        "width": 512,
        "height": 896,
        "steps": 20,
        "cfg": 6,
        "events": ["NORMAL"]
    }
    
    print(f"[*] Prompt: {prompts[0]}")
    paths = generate_images(job_id, prompts, negative, out_dir, cfg)
    
    if paths and os.path.exists(paths[0]):
        size = os.path.getsize(paths[0])
        print(f"[*] Generated: {paths[0]} ({size} bytes)")
        if size > 100000:
            print("✅ SMOKE TEST PASSED")
            return
    
    print("❌ SMOKE TEST FAILED")
    sys.exit(1)

if __name__ == "__main__":
    test_single_smoke()
