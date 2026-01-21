import sys
import os
import unittest
from unittest.mock import MagicMock

# Ensure we can import from src (assuming running from valid root)
# If running from faceless_studio root:
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir) # faceless_studio
sys.path.insert(0, parent_dir)

from src.artist import VisualEngine

class TestScenePrompt(unittest.TestCase):
    def test_prompt_includes_fields(self):
        engine = VisualEngine()
        # Mock comfyui retry to just return prompts for inspection
        engine._generate_comfyui_with_retry = MagicMock(return_value=[])
        
        scenes = [{
            "main_subject": "A Cat",
            "action": "Jumping",
            "location": "Roof",
            "time": "Night",
            "lighting": "Moonlight",
            "atmosphere": "Spooky",
            "camera": "Wide Shot",
            "visible_objects": ["Moon", "Chimney"]
        }]
        
        style = {
            "prompt_prefix": "StylePrefix",
            "character_bible": "DocuStyle",
            "camera_bible": "35mm",
            "palette_bible": "Blue"
        }
        
        # We need to capture the prompts sent to _generate_comfyui_with_retry
        engine.generate_images(scenes, style, "tmp_dir")
        
        call_args = engine._generate_comfyui_with_retry.call_args
        prompts = call_args[0][0] # First arg is prompts list
        
        p = prompts[0]
        print(f"Generated Prompt: {p}")
        
        self.assertIn("Subject: A Cat", p)
        self.assertIn("Location: Roof", p)
        self.assertIn("Time/Light: Night", p)
        self.assertIn("Atmosphere: Spooky", p)
        self.assertIn("Camera: Wide Shot", p)
        self.assertIn("MUST SHOW: Moon, Chimney", p)
        
        print("✅ Scene Prompt includes all key fields.")

if __name__ == '__main__':
    from unittest.mock import MagicMock
    unittest.main()
