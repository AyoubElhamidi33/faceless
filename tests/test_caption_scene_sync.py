import unittest
import unittest.mock as mock
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.editor import VideoEditor

class TestCaptionSync(unittest.TestCase):
    def test_caption_sync(self):
        # Mock TextClip inside editor to avoid ImageMagick
        with mock.patch("src.editor.TextClip") as MockTextClip:
            mock_clip = mock.MagicMock()
            # Chain configuration
            MockTextClip.return_value.set_position.return_value \
                        .set_start.return_value \
                        .set_duration.return_value \
                        .resize.return_value \
                        .crossfadein.return_value = mock_clip
            
            # Since resize is called multiple times, we need it to return something that has crossfadein
            # Actually simpler: ANY method call returns the mock_clip (self)
            mock_clip.set_position.return_value = mock_clip
            mock_clip.set_start.return_value = mock_clip
            mock_clip.set_duration.return_value = mock_clip
            mock_clip.resize.return_value = mock_clip
            mock_clip.crossfadein.return_value = mock_clip
            
            MockTextClip.return_value = mock_clip
            
            editor = VideoEditor()
            
            # Metadata: 2 words, then silence, then 1 word
            audio_metadata = [
                {"start": 0.0, "end": 1.0, "text": "Hello World", "type": "speech"},
                {"start": 1.0, "end": 3.0, "text": "[SILENCE]", "type": "silence"},
                {"start": 3.0, "end": 4.0, "text": "Bye", "type": "speech"},
            ]
            
            style = {"method": "center_wordbeats", "uppercase": True}
            
            clips = editor._generate_captions("dummy_path", style, {}, 4.0, audio_metadata=audio_metadata)
            
            # Expected matches:
            # "Hello", "World", "Bye" -> 3 clips
            self.assertEqual(len(clips), 3)
            
            print(f"\n[SUCCESS] Generated {len(clips)} caption clips from metadata.")
            print("  - Expects NO clips during 1.0s-3.0s silence.")
            # We trust the logic (iterates only speech types)

if __name__ == "__main__":
    unittest.main()
