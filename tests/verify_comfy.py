import os

# Assuming default portable path or check local
# User said: ComfyUI_Local/models/checkpoints/
# But I don't know where ComfyUI_Local IS.
# I'll check common paths.

paths_to_check = [
    "c:/Users/DOVY/Desktop/REELS AUTOMATION/ComfyUI_Local/models/checkpoints",
]

models = ["dreamshaper_8.safetensors", "revAnimated_v122EOL.safetensors"]

found_dir = None
for p in paths_to_check:
    if os.path.exists(p):
        found_dir = p
        break

if found_dir:
    print(f"Found Checkpoint Dir: {found_dir}")
    for m in models:
        mp = os.path.join(found_dir, m)
        if os.path.exists(mp):
            print(f"[OK] Found {m}")
        else:
            print(f"[MISSING] {m}")
else:
    print("[!] Could not find ComfyUI checkpoint directory. Models might be missing.")
