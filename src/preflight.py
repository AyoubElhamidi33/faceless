import os
import sys
import shutil
import requests
import importlib

def check_comfy_ready():
    print("[*] Checking ComfyUI (127.0.0.1:8188)...")
    try:
        resp = requests.get("http://127.0.0.1:8188/system_stats", timeout=2)
        if resp.status_code == 200:
            print("   ✅ ComfyUI Online")
            return True
    except:
        print("   ❌ ComfyUI Offline or Unreachable")
    return False

def check_model_exists():
    path = "c:/Users/DOVY/Desktop/REELS AUTOMATION/ComfyUI_Local/models/checkpoints/Juggernaut_XL_v9_RunDiffusionPhoto_v2.safetensors"
    print(f"[*] Checking Model: {os.path.basename(path)}...")
    if os.path.exists(path):
        print("   ✅ Model Found")
        return True
    print("   ❌ Model Missing")
    return False

def check_deps():
    print("[*] Checking Dependencies...")
    required = ["moviepy", "requests", "PIL"]
    missing = []
    for pkg in required:
        try:
            importlib.import_module(pkg)
            if pkg == "PIL": importlib.import_module("PIL.Image")
        except ImportError:
            missing.append(pkg)
    
    if not missing:
        print("   ✅ All Deps Found")
        return True
    print(f"   ❌ Missing: {missing}")
    return False

def check_disk_space(min_gb=2):
    try:
        total, used, free = shutil.disk_usage(".")
        free_gb = free // (2**30)
        if free_gb < min_gb:
            print(f"[*] Checking Disk Space...\n   ❌ Low Disk Space ({free_gb}GB < {min_gb}GB)")
            return False
        print(f"[*] Checking Disk Space...\n   ✅ Disk Space OK ({free_gb}GB Free)")
        return True
    except:
        return True

def check_write_perms():
    print("[*] Checking Write Permissions...")
    dirs = ["outputs", "assets/temp"]
    for d in dirs:
        if not os.path.exists(d):
            try:
                os.makedirs(d)
            except:
                print(f"   ❌ Cannot create {d}")
                return False
        
        if not os.access(d, os.W_OK):
             print(f"   ❌ No Write Access to {d}")
             return False
    print("   ✅ Write Access OK")
    return True

def validate():
    print("\n✈️  PROMETHEUS PREFLIGHT CHECK ✈️")
    print("-----------------------------------")
    checks = [
        check_comfy_ready(),
        check_model_exists(),
        check_deps(),
        check_disk_space(),
        check_write_perms()
    ]
    
    if all(checks):
        print("-----------------------------------")
        print("✅ PREFLIGHT PASSED. SYSTEM READY.")
        return True
    else:
        print("-----------------------------------")
        print("🛑 PREFLIGHT FAILED. ABORTING.")
        sys.exit(1)

if __name__ == "__main__":
    validate()
