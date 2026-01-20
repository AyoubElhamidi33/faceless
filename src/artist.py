import os
import requests
from openai import OpenAI
from .config import OPENAI_API_KEY, TEMP_DIR

class VisualEngine:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.style_prompt = "Dark comic book style, cel-shaded, noir atmosphere, vintage coloration. High definition, cinematic composition."
        self.character_descriptor = "A mysterious figure in a trench coat" # Default fallback

    def generate_images(self, scenes: list, character_desc: str = None) -> list:
        """
        Generates images for the given list of scene prompts.
        Returns a list of local file paths to the saved images.
        """
        image_paths = []
        if character_desc:
            self.character_descriptor = character_desc

        print(f"[*] Generating {len(scenes)} images...")

        for i, scene_prompt in enumerate(scenes):
            full_prompt = (
                f"{self.style_prompt} "
                f"Character consistency: {self.character_descriptor}. "
                f"Scene: {scene_prompt}"
            )

            print(f"[*] Generatng image {i+1}/{len(scenes)}...")
            try:
                response = self.client.images.generate(
                    model="dall-e-3",
                    prompt=full_prompt,
                    size="1024x1792", # Vertical aspect ratio for DALL-E 3
                    quality="hd",
                    n=1,
                )
                
                image_url = response.data[0].url
                image_path = self._save_image(image_url, i)
                image_paths.append(image_path)
            except Exception as e:
                print(f"[!] Error generating image {i+1}: {e}")
                # Placeholder for error handling - maybe retry or skip
        
        return image_paths

    def _save_image(self, url: str, index: int) -> str:
        response = requests.get(url)
        if response.status_code == 200:
            filename = f"scene_{index:03d}.png"
            filepath = os.path.join(TEMP_DIR, filename)
            with open(filepath, 'wb') as f:
                f.write(response.content)
            return filepath
        else:
            raise Exception(f"Failed to download image from {url}")

if __name__ == "__main__":
    # Test
    artist = VisualEngine()
    # Mock call
    # artist.generate_images(["A detective standing in the rain looking at a neon sign."])
