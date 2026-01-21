import sys
import os
import unittest
from unittest.mock import MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.writer import ScriptGenerator

class TestHookVariation(unittest.TestCase):
    def test_hook_banned_phrases(self):
        writer = ScriptGenerator()
        writer.client = MagicMock()
        
        # Mock response from OpenAI to test validation logic/prompt construction
        # Actually validation is inside prompt instructions now.
        # We can inspect the prompt sent to _generate_hook logic (internal call).
        
        # Just verifying the code path runs without error and prompt contains "BANNED PHRASES"
        # Since we can't easily mock the internal random choice or private method without more stubbing,
        # we will check if the method exists and runs.
        
        writer.client.chat.completions.create.return_value.choices = [
            MagicMock(message=MagicMock(content='{"hook_type": "test", "hook_text": "Impossible event at 3AM."}'))
        ]
        
        res = writer._generate_hook("Test Topic")
        self.assertIn("hook_text", res)
        # We assume the prompt sent enforced the ban.
        # To truly verify, we'd inspect call_args on the mock.
        
        start_prompt = writer.client.chat.completions.create.call_args[1]['messages'][0]['content']
        self.assertIn("BANNED PHRASES", start_prompt)
        print("✅ Hook Prompt contains BANNED PHRASES instruction.")

if __name__ == '__main__':
    unittest.main()
