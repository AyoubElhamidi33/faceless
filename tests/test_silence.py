import unittest
import unittest.mock as mock
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.narrator import AudioEngine

class TestSilence(unittest.TestCase):
    def test_silence_markers(self):
        # Mock dependencies
        with mock.patch("src.narrator.OpenAI"), \
             mock.patch("src.narrator.ELEVENLABS_API_KEY", None), \
             mock.patch("src.narrator.AudioFileClip") as MockClip, \
             mock.patch("src.narrator.AudioClip") as MockAudioClip, \
             mock.patch("src.narrator.concatenate_audioclips"), \
             mock.patch("os.path.exists", return_value=True):
            
            # Setup Mocks
            mock_clip_inst = mock.MagicMock()
            mock_clip_inst.duration = 3.0
            MockClip.return_value = mock_clip_inst
            
            mock_audio_clip_inst = mock.MagicMock()
            MockAudioClip.return_value = mock_audio_clip_inst
            
            narrator = AudioEngine()
            narrator._generate_single_chunk = mock.MagicMock()
            
            text = "Hello.[SILENCE:2.5]World."
            
            # Run
            path, meta = narrator.generate_voice(text, "test_output")
            
            # Assertions
            # We expect 3 clips: Speech(Hello), Silence(2.5), Speech(World)
            # Metadata check
            self.assertEqual(len(meta), 3)
            
            # 1. Speech "Hello."
            self.assertEqual(meta[0]["type"], "speech")
            self.assertEqual(meta[0]["text"], "Hello.")
            
            # 2. Silence
            self.assertEqual(meta[1]["type"], "silence")
            self.assertEqual(meta[1]["text"], "[SILENCE]")
            self.assertAlmostEqual(meta[1]["end"] - meta[1]["start"], 2.5)
            
            # 3. Speech "World."
            self.assertEqual(meta[2]["type"], "speech")
            self.assertEqual(meta[2]["text"], "World.")
            
            print("\n[SUCCESS] test_silence_markers:")
            for m in meta:
                print(f"  {m['type'].upper()} ({m['end']-m['start']:.1f}s): {m['text']}")

if __name__ == "__main__":
    unittest.main()
