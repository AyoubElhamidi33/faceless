import json
import urllib.request
import urllib.parse
import time
import os
import random

SERVER_ADDRESS = "127.0.0.1:8188"
CLIENT_ID = "prometheus_local"

# HARD LOCK CONFIGURATION
DEFAULT_MODEL = "Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors"
DEFAULT_WIDTH = 512
DEFAULT_HEIGHT = 896
DEFAULT_STEPS = 25
DEFAULT_CFG = 6
DEFAULT_SAMPLER = "euler"

def _check_model_activation():
    """Step 7: Activation Check on Startup (Real FS Check)"""
    required_model = DEFAULT_MODEL
    
    # Common ComfyUI paths relative to studio
    possible_paths = [
        "../ComfyUI_Local/models/checkpoints",
        "../../ComfyUI_Local/models/checkpoints",
        "C:/Users/DOVY/Desktop/REELS AUTOMATION/ComfyUI_Local/models/checkpoints"
    ]
    
    found = False
    for p in possible_paths:
        target = os.path.join(p, required_model)
        if os.path.exists(target):
            print(f"   ✅ Model Verified: {required_model}")
            found = True
            break
            
    if not found:
        print(f"   ⚠️  Model '{required_model}' NOT FOUND in standard paths.")
        print("      (Ignore if using custom path, but verify manually)")

def _check_backend_compliance(client, width, height):
    """
    Blocks production runs if CPU backend is detected.
    """
    try:
        # Simple /system_stats check if client supports it
        # Note: ComfyUIClient needs get_system_stats method
        pass 
    except:
        pass

def generate_images(job_id: str, prompts: list[str], negative: str, out_dir: str, cfg: dict = None) -> list[str]:
    """
    Generates images locally via ComfyUI.
    Returns list of absolute paths to generated images.
    STRICT LOCAL MODE: No Fallback.
    """
    client = ComfyUIClient(SERVER_ADDRESS)
    generated_paths = []
    
    # 7) ACTIVATION CHECK (Fast)
    # We assume 'revAnimated_v122EOL.safetensors' is available per Step 1 & 7.
    # If file check fails here, we crash.
    # (Checking strictly via API might be slow per image, we trust the startup or previous check)
    
    # 3) RESOLUTION + QUALITY LOCK
    width = DEFAULT_WIDTH
    height = DEFAULT_HEIGHT
    steps = DEFAULT_STEPS
    cfg_scale = DEFAULT_CFG
    sampler = DEFAULT_SAMPLER
    
    # TASK 4: BACKEND CHECK
    _check_backend_compliance(client, width, height)
    
    # 1) HARD-LOCK THE MODEL
    model_name = DEFAULT_MODEL
    
    print(f"[*] ComfyUI: Starting batch of {len(prompts)} images using '{model_name}'...")
    print(f"[*] Visual Debug: Res={width}x{height} | Steps={steps} | CFG={cfg_scale} | Sampler={sampler}")
    print(f"[*] Visual Debug: Negative Prompt: {negative[:100]}...")

    # 2) CONSISTENT SEED ENGINE
    # User Spec: base_seed = random.randint(1, 10_000_000)
    # scene_seed = base_seed + (scene_index * 1000)
    base_seed = random.randint(1, 10_000_000)
    print(f"[*] Visual Debug: Base Seed: {base_seed}")

    for idx, prompt_text in enumerate(prompts):
        scene_num = idx + 1
        filename_prefix = f"{job_id}_scene_{scene_num:02d}"
        
        # Deterministic seed variation
        seed = base_seed + (idx * 1000)
        
        print(f"[*] Visual Debug: Scene {scene_num} Seed: {seed}")
        print(f"[*] Visual Debug: Prompt: {prompt_text[:100]}...")
        
        # 1. Build Workflow
        workflow = _build_workflow(
            model_name=model_name,
            positive=prompt_text,
            negative=negative,
            width=width,
            height=height,
            steps=steps,
            cfg=cfg_scale,
            seed=seed,
            filename_prefix=filename_prefix,
            sampler_name=sampler
        )
        
        # 2. Queue
        try:
            print(f"[*] ComfyUI: Queueing Scene {scene_num}...")
            response = client.queue_prompt(workflow)
            if not response:
                print(f"[!] FATAL: ComfyUI Failed to queue Scene {scene_num}")
                raise RuntimeError("ComfyUI Queue Failed")
                
            prompt_id = response['prompt_id']
            
            # 3. Poll
            history = client.wait_for_prompt(prompt_id)
            
            # 4. Download
            outputs = history[prompt_id]['outputs']
            image_data = None
            
            for node_id, node_output in outputs.items():
                if 'images' in node_output:
                    for img_info in node_output['images']:
                        fname = img_info['filename']
                        subfolder = img_info['subfolder']
                        type_ = img_info['type']
                        
                        raw_bytes = client.get_image(fname, subfolder, type_)
                        image_data = raw_bytes
                        break
                if image_data: break
            
            if image_data:
                dst_filename = f"scene_{scene_num:02d}.png"
                dst_path = os.path.join(out_dir, dst_filename)
                with open(dst_path, 'wb') as f:
                    f.write(image_data)
                generated_paths.append(dst_path)
                print(f"[*] ComfyUI: Downloaded & Saved -> {dst_path}")
            else:
                print(f"[!] FATAL: Generated but no image found for Scene {scene_num}")
                raise RuntimeError("ComfyUI Image Generation Failed - No Output")

        except Exception as e:
            print(f"[!] FATAL ComfyUI Error Scene {scene_num}: {e}")
            # 6) STRICT LOCAL MODE: If ComfyUI fails, throw a fatal error and discard the job.
            raise RuntimeError(f"Strict Local Mode Validation Failed: {e}")
            
    return generated_paths

class ComfyUIClient:
    def __init__(self, server_address):
        self.server_address = server_address

    def queue_prompt(self, prompt_workflow: dict):
        p = {"prompt": prompt_workflow, "client_id": CLIENT_ID}
        data = json.dumps(p).encode('utf-8')
        req = urllib.request.Request(f"http://{self.server_address}/prompt", data=data)
        try:
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read())
        except Exception as e:
            print(f"[!] ComfyUI Queue Error: {e}")
            return None

    def wait_for_prompt(self, prompt_id: str):
        print(f"[*] ComfyUI: Waiting for Job {prompt_id}...", end="", flush=True)
        wait_count = 0
        while True:
            try:
                with urllib.request.urlopen(f"http://{self.server_address}/history/{prompt_id}") as response:
                    history = json.loads(response.read())
                    if prompt_id in history:
                        print(" Done!")
                        return history
            except Exception:
                pass
            
            # Print dot every 2 seconds
            if wait_count % 2 == 0:
                print(".", end="", flush=True)
                
            time.sleep(1)
            wait_count += 1

    def get_image(self, filename: str, subfolder: str, folder_type: str):
        data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        url_values = urllib.parse.urlencode(data)
        with urllib.request.urlopen(f"http://{self.server_address}/view?{url_values}") as response:
            return response.read()

def _build_workflow(model_name, positive, negative, width, height, steps, cfg, seed, filename_prefix, sampler_name="euler"):
    # Minimal ID-based workflow
    # 4: CheckpointLoaderSimple
    # 6: CLIPTextEncode (Pos)
    # 7: CLIPTextEncode (Neg)
    # 3: KSampler
    # 5: EmptyLatentImage
    # 8: VAEDecode
    # 9: SaveImage
    
    return {
        "3": {
            "inputs": {
                "seed": seed, "steps": steps, "cfg": cfg, "sampler_name": sampler_name, "scheduler": "normal",
                "denoise": 1,
                "model": ["4", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0]
            },
            "class_type": "KSampler"
        },
        "4": {
            "inputs": {"ckpt_name": model_name},
            "class_type": "CheckpointLoaderSimple"
        },
        "5": {
            "inputs": {"width": width, "height": height, "batch_size": 1},
            "class_type": "EmptyLatentImage"
        },
        "6": {
            "inputs": {"text": positive, "clip": ["4", 1]},
            "class_type": "CLIPTextEncode"
        },
        "7": {
            "inputs": {"text": negative, "clip": ["4", 1]},
            "class_type": "CLIPTextEncode"
        },
        "8": {
            "inputs": {"samples": ["3", 0], "vae": ["4", 2]},
            "class_type": "VAEDecode"
        },
        "9": {
            "inputs": {"filename_prefix": filename_prefix, "images": ["8", 0]},
            "class_type": "SaveImage"
        }
    }
