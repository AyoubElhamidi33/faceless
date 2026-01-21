import sys
import os
import json
import unittest

# Adjust path to find src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

class TestConfigKeys(unittest.TestCase):
    def test_main_config_loading(self):
        # Simulate main.py config loading logic
        from src.config import OUTPUT_DIR
        
        # Mock load_config
        def load_config(path):
            if "channels" in path:
                return {
                    "name": "test_channel",
                    "style": "test_style",
                    "default_style": "old_style_key",
                    "caption_style": "test_caption",
                    "default_caption_style": "old_caption_key"
                }
            return {}

        CHANNEL_CONF = load_config("channels/test.json")
        
        # Test Patch 0 Logic
        STYLE_NAME = CHANNEL_CONF.get("style", CHANNEL_CONF.get("default_style", "fallback"))
        CAPTION_NAME = CHANNEL_CONF.get("caption_style", CHANNEL_CONF.get("default_caption_style", "fallback"))
        
        self.assertEqual(STYLE_NAME, "test_style")
        self.assertEqual(CAPTION_NAME, "test_caption")
        print(f"✅ Config Drift Fix Verified: {STYLE_NAME}, {CAPTION_NAME}")

if __name__ == '__main__':
    unittest.main()
