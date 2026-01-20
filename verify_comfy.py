import urllib.request
import json

try:
    print("Requesting object_info...")
    with urllib.request.urlopen('http://127.0.0.1:8188/object_info') as response:
        data = json.loads(response.read())
        
    outputs = [k for k,v in data.items() if v.get('output_node')]
    print("Found Output Nodes:", outputs)
    
    if "SaveImage" in outputs:
        print("SaveImage Details:", data["SaveImage"])
    else:
        print("SaveImage NOT FOUND in output nodes!")

except Exception as e:
    print(f"Error: {e}")
