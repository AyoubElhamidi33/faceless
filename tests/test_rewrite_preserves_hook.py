import sys
import os
import unittest
from unittest.mock import MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.writer import ScriptGenerator

class TestRewriteIntegrity(unittest.TestCase):
    def test_rewrite_preserves_hook(self):
        writer = ScriptGenerator()
        writer.client = MagicMock()
        
        hook = "The shadow moved."
        
        # Mock LLM returning text WITHOUT hook to test the force-fix
        writer.client.chat.completions.create.return_value.choices = [
            MagicMock(message=MagicMock(content="It was a dark night and the thing shifted."))
        ]
        
        final = writer._rewrite_human_voice("Draft text", hook)
        
        self.assertTrue(final.startswith(hook))
        print(f"✅ Rewrite forced hook prefix: {final}")

if __name__ == '__main__':
    unittest.main()
