import urllib.request
import json

SERVER_ADDRESS = "127.0.0.1:8188"
CLIENT_ID = "test_minimal"

def build_workflow():
    workflow = {}
    # EmptyLatent -> SaveLatent
    workflow["5"] = {
        "inputs": {"width": 512, "height": 512, "batch_size": 1},
        "class_type": "EmptyLatentImage"
    }
    workflow["10"] = {
        "inputs": {"samples": ["5", 0], "filename_prefix": "MINIMAL_TEST"},
        "class_type": "SaveLatent"
    }
    return workflow

def queue_prompt(prompt_workflow):
    p = {"prompt": prompt_workflow, "client_id": CLIENT_ID}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request(f"http://{SERVER_ADDRESS}/prompt", data=data)
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read())
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode()}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    wf = build_workflow()
    print("Sending minimal workflow...")
    res = queue_prompt(wf)
    print("Response:", res)
