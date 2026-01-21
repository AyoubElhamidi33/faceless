import clip
import torch

try:
    model, preprocess = clip.load("ViT-B/32", device="cpu")
    print("CLIP OK: True")
except Exception as e:
    print(f"CLIP OK: False ({e})")
