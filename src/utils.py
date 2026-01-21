import hashlib
import os

def check_images_unique(folder_path: str) -> bool:
    """
    Checks if all images in a folder are unique by hash.
    Returns True if all unique, False if duplicates found.
    """
    hashes = set()
    files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if not files:
        print(f"[!] No images found in {folder_path} to check uniqueness.")
        return False
        
    for filename in files:
        path = os.path.join(folder_path, filename)
        with open(path, "rb") as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
            
        if file_hash in hashes:
            print(f"[!] Duplicate image found: {filename}")
            return False
        hashes.add(file_hash)
        
    print(f"[*] Verified {len(files)} unique images in {folder_path}.")
    return True
