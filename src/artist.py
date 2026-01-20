import os
import requests
from openai import OpenAI
from .config import OPENAI_API_KEY

class VisualEngine:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def generate_images(self, scenes: list, style_profile: dict, job_dir: str) -> list:
        from .config import IMAGE_BACKEND
        
        # Strict Local Mode
        if IMAGE_BACKEND == "comfyui":
            print("[*] VisualEngine: Using LOCAL ComfyUI (Strict Mode - No Fallback)...")
            return self._generate_comfyui(scenes, style_profile, job_dir)
        
        # Default to OpenAI
        print("[*] VisualEngine: Using OpenAI DALL-E 3...")
        return self._generate_openai(scenes, style_profile, job_dir)

    def _generate_openai(self, scenes: list, style_profile: dict, job_dir: str) -> list:
        image_paths = []
        # Style Construction
        # prefix + char + camera + scene
        prefix = style_profile.get("prompt_prefix", "")
        char = style_profile.get("character_bible", "")
        camera = style_profile.get("camera_bible", "")
        
        print(f"[*] Generating {len(scenes)} images based on style: {style_profile.get('name')}")

        for i, scene_prompt in enumerate(scenes):
            full_prompt = f"{prefix}. {char}. {camera}. SCENE: {scene_prompt}"
            if len(full_prompt) > 3000: full_prompt = full_prompt[:3000]

            print(f"[*] Generating image {i+1}...")
            try:
                response = self.client.images.generate(
                    model="dall-e-3", prompt=full_prompt, size="1024x1792", quality="hd", n=1,
                )
                image_url = response.data[0].url
                image_path = self._save_image(image_url, i, job_dir)
                image_paths.append(image_path)
            except Exception as e:
                print(f"[!] Error generating image {i+1}: {e}")
        return image_paths

    def _generate_comfyui(self, scenes: list, style_profile: dict, job_dir: str) -> list:
        from .local_comfyui import generate_images
        
        job_id = os.path.basename(job_dir)
        
        # Construct exact prompts
        prefix = style_profile.get("prompt_prefix", "")
        char = style_profile.get("character_bible", "")
        cam = style_profile.get("camera_bible", "")
        negative = style_profile.get("negative_prompt", "")
        
        final_prompts = []
        for scene in scenes:
            p = f"{prefix}, {char}, {cam}, {scene}"
            final_prompts.append(p)
            
        return generate_images(
            job_id=job_id,
            prompts=final_prompts,
            negative=negative,
            out_dir=job_dir,
            cfg=style_profile # Pass entire style profile as cfg (contains width/height/etc)
        )

    def _save_image(self, url: str, index: int, job_dir: str) -> str:
        response = requests.get(url)
        if response.status_code == 200:
            filename = f"scene_{index:03d}.png"
            filepath = os.path.join(job_dir, filename)
            with open(filepath, 'wb') as f:
                f.write(response.content)
            return filepath
        return None
