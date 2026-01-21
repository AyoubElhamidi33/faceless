import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.validator import validate_false_calm

class TestFalseCalm(unittest.TestCase):
    def test_false_calm_fail(self):
        # Missing the "Calm -> Warning -> Calm -> Doom" sequence
        # Just Calm -> Doom
        text = "It was quiet. Then it exploded."
        valid, problems = validate_false_calm(text)
        self.assertFalse(valid)
        self.assertIn("False Calm Pattern", problems[0])
        print(f"\n[SUCCESS] test_false_calm_fail: Detected '{text}' as INVALID.")

    def test_false_calm_pass(self):
        # Valid: Calm -> Warning -> Calm -> Doom
        # Calm: "quiet"
        # Warning: "rumble"
        # Calm: "stopped"
        # Doom: "exploded"
        text = "It was quiet and peaceful. Suddenly I heard a rumble. Then it stopped and was normal. Finally it exploded."
        valid, problems = validate_false_calm(text)
        self.assertTrue(valid)
        print(f"\n[SUCCESS] test_false_calm_pass: Detected Valid Sequence.")

if __name__ == "__main__":
    unittest.main()
