import sys
import os
import unittest
import shutil
from unittest.mock import MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.topic_engine import TopicEngine

class TestTopicDedupe(unittest.TestCase):
    def setUp(self):
        # Create temp output dir for state
        self.test_dir = "tests_output"
        os.makedirs(self.test_dir, exist_ok=True)
        # Mock config
        self.conf = {"niche": "test_horror"}
        
        # We need to patch OUTPUT_DIR in topic_engine or pass state file?
        # TopicEngine uses src.config.OUTPUT_DIR import. 
        # We can't easily patch the import on the fly without stubbing.
        # But we can patch self.state_file in the instance.
    
    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_dedupe_logic(self):
        engine = TopicEngine(self.conf)
        engine.state_file = os.path.join(self.test_dir, "topic_state.json")
        engine._load_state() 
        
        # Seed state with "Old Topic"
        engine.state["used_topics"] = ["Old Topic"]
        
        # Mock generate batch to return [Old Topic, New Topic]
        engine._generate_batch = MagicMock(return_value=["Old Topic", "New Topic"])
        
        topic = engine.get_fresh_topic()
        
        self.assertEqual(topic, "New Topic")
        self.assertIn("New Topic", engine.state["used_topics"])
        print("✅ Dedupe Logic Verified: 'Old Topic' skipped, 'New Topic' selected.")

if __name__ == '__main__':
    unittest.main()
