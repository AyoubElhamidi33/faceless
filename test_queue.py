import urllib.request
import json
import random

SERVER_ADDRESS = "127.0.0.1:8188"
CLIENT_ID = "test_client"

def build_workflow():
    workflow = {}
    workflow["3"] = {
        "inputs": {
            "seed": 123456789, "steps": 20, "cfg": 8, "sampler_name": "euler", "scheduler": "normal",
            "denoise": 1,
            "model": ["4", 0],
            "positive": ["6", 0],
            "negative": ["7", 0],
            "latent_image": ["5", 0]
        },
        "class_type": "KSampler"
    }
    workflow["4"] = {
        "inputs": {"ckpt_name": "dreamshaper_8.safetensors"},
        "class_type": "CheckpointLoaderSimple"
    }
    workflow["5"] = {
        "inputs": {"width": 512, "height": 512, "batch_size": 1},
        "class_type": "EmptyLatentImage"
    }
    workflow["6"] = {
        "inputs": {"text": "test image", "clip": ["4", 1]},
        "class_type": "CLIPTextEncode"
    }
    workflow["7"] = {
        "inputs": {"text": "bad quality", "clip": ["4", 1]},
        "class_type": "CLIPTextEncode"
    }
    workflow["8"] = {
        "inputs": {"samples": ["3", 0], "vae": ["4", 2]},
        "class_type": "VAEDecode"
    }
    workflow["9"] = {
        "inputs": {"filename_prefix": "TEST_API", "images": ["8", 0]},
        "class_type": "SaveImage"
    }
    return workflow

def queue_prompt(prompt_workflow):
    p = {"prompt": prompt_workflow, "client_id": CLIENT_ID}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request(f"http://{SERVER_ADDRESS}/prompt", data=data)
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read())
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    wf = build_workflow()
    print("Sending workflow...")
    res = queue_prompt(wf)
    print("Response:", res)
