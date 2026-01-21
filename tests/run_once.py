import sys
import os
import time
import uuid

# Ensure we are running from project root
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from main import run_job, load_config
from src.topic_engine import TopicEngine
from src.validator import validate_api_keys

if __name__ == "__main__":
    print("[*] Validating Environment...")
    if not validate_api_keys():
        print("🛑 STOPPING: Fix API keys in .env or environment.")
        sys.exit(1)

    print("[*] Loading Configuration...")
    # Load config manually to ensure we have it
    try:
        channel_conf = load_config("channels/comic_documentary_horror.json")
    except Exception as e:
        print(f"[!] Config Load Failed: {e}")
        sys.exit(1)
        
    print("[*] Initializing Topic Engine...")
    topic_engine = TopicEngine(channel_conf)
    
    job_id = f"v4_manual_{int(time.time())}"
    print(f"[*] Starting Single Job: {job_id}")
    
    try:
        run_job(job_id, topic_engine)
        print(f"\n✅ MANUAL RUN COMPLETE: {job_id}")
    except Exception as e:
        print(f"\n❌ RUN FAILED: {e}")
        import traceback
        traceback.print_exc()
