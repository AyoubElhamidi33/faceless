import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.storyboard_engine import build_storyboard

class TestStoryboardContinuity(unittest.TestCase):
    def test_continuity_and_events(self):
        mock_script = {
            "script_text": "One. Two. Three. Four. Five. Six. Seven. Eight. Nine. Ten. Eleven. Twelve. Thirteen. Fourteen. Fifteen. Sixteen.",
            "scenes": [
                {"location": "Kitchen", "visible_objects": ["Knife"]}, # Scene 1
                {"location": "Kitchen"}, # Scene 2
                {"location": "Garden", "visible_objects": ["Shovel"]}, # Scene 3 (Move)
            ]
        }
        style = {}
        
        scenes = build_storyboard(mock_script, style)
        
        # 16 Scenes
        self.assertEqual(len(scenes), 16)
        
        # Check Event Types
        self.assertEqual(scenes[0]["event_type"], "NORMAL")
        self.assertEqual(scenes[5]["event_type"], "WARNING") # 4-6
        self.assertEqual(scenes[8]["event_type"], "ESCALATION") # 7-10
        self.assertEqual(scenes[12]["event_type"], "DANGER") # 11-14
        self.assertEqual(scenes[15]["event_type"], "AFTERMATH") # 15
        
        # Check Lighting Map (Patch 6)
        self.assertIn("Natural", scenes[0]["lighting"])
        self.assertIn("Dim", scenes[5]["lighting"])
        
        # Check Continuity
        # Scene 1: Kitchen, Knife
        self.assertEqual(scenes[0]["location"], "Kitchen")
        self.assertIn("Knife", scenes[0]["visible_objects"])
        
        # Scene 2: Kitchen (Persistence), Knife (Persistence)
        self.assertEqual(scenes[1]["location"], "Kitchen") 
        self.assertIn("Knife", scenes[1]["visible_objects"])
        
        # Scene 3: Garden (Change), Knife + Shovel (Accumulation?)
        # Logic says: objects accumulate.
        self.assertEqual(scenes[2]["location"], "Garden")
        self.assertIn("Knife", scenes[2]["visible_objects"])
        self.assertIn("Shovel", scenes[2]["visible_objects"])
        
        # Scene 4: Garden (Persistence)
        self.assertEqual(scenes[3]["location"], "Garden")
        
        print("\n[SUCCESS] Storyboard Continuity & Events Verified.")
        print(f"  Sc 1: {scenes[0]['location']} | {scenes[0]['event_type']}")
        print(f"  Sc 3: {scenes[2]['location']} | {scenes[2]['visible_objects']}")

if __name__ == "__main__":
    unittest.main()
