import sys
import os
import json
import unittest.mock as mock

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# MOCK HEAVY DEPENDENCIES BEFORE IMPORTING CLASSES
with mock.patch('whisper.load_model', return_value=mock.MagicMock()) as mock_whisper:
    from src.storyboard_engine import build_storyboard
    from src.validator import validate_script_logic
    from src.narrator import AudioEngine
    from src.editor import VideoEditor

# MOCK DATA
mock_script = {
    "script_text": "I heard a noise. I decided to run. I felt scared. [SILENCE:2.0] Then I saw it.",
    "fact_confidence": "high",
    "beat_words": ["I", "heard", "a", "noise", "I", "decided", "to", "run", "I", "felt", "scared", "Then", "I", "saw", "it"],
    "scenes": [{"location": "Bedroom", "visible_objects": ["Bed"]}], # partial
    "narrative_pov": "I",
    "iconic_scene_index": 5,
    "sticky_ending_line": "It was over.",
    "hook_text": "text",
    "metadata": {}
}

# 1. Test Validator (POV, etc)
print("\n--- TEST 1: VALIDATOR ---")
# Using a text that PASSES POV check (Sensory: heard, felt, saw; Decision: run; Emotion: scared)
# But let's check structure.
# We need 16 scenes for validation to pass structure check.
# Let's mock 16 scenes.
mock_script["scenes"] = [{"location": "Loc"} for _ in range(16)]

valid, probs = validate_script_logic(mock_script)
print(f"Validation Result: {valid}")
if not valid:
    print("Problems:", probs)
else:
    print("Validation PASSED (Expected).")

# Test FAILURE case (False Calm)
print("\n--- TEST 2: VALIDATOR FAIL CASE ---")
bad_text = "It was quiet. Then a boom. Then quiet again. Then everyone died."
# Heuristic expects: Calm -> Warn -> Calm -> Doom
# "quiet" (Calm) -> "boom" (Doom) -- Missing Warning and second Calm?
# Actually "boom" is catastrophe.
# "Then quiet again" (Calm).
# "Then everyone died" (Matches nothing? "died" not in list? "chaos" is.)
# validator_false_calm checks: Calm < Warning < Calm < Catastrophe
# "quiet" (0) -> "boom" (Doom, but checking Warn?)
# Let's try to construct a Valid Calm sequence:
# "It was quiet (Calm). I heard a rumble (Warn). Then it stopped (Calm). Then it exploded (Doom)."
ret, _ = validate_script_logic({**mock_script, "script_text": bad_text, "beat_words": bad_text.split()})
# Note: script logic also runs other checks. We just want to see if `validate_false_calm` complains differently.

# 2. Test Storyboard Engine (Lighting + Events)
print("\n--- TEST 3: STORYBOARD ENGINE ---")
style = {"palette_bible": "Dark", "camera_bible": "Wide"}
# We use a script with 16 sentences to see event curves?
# Or just simple script.
sb_scenes = build_storyboard(mock_script, style)
print(f"Generated {len(sb_scenes)} scenes.")
print(f"Scene 1 Event: {sb_scenes[0]['event_type']} | Lighting: {sb_scenes[0]['lighting']}")
print(f"Scene 8 Event: {sb_scenes[7]['event_type']} | Lighting: {sb_scenes[7]['lighting']}")
print(f"Scene 14 Event: {sb_scenes[13]['event_type']} | Lighting: {sb_scenes[13]['lighting']}")

# 3. Test Narrator Metadata Logic (Mocking the private method)
print("\n--- TEST 4: NARRATOR METADATA ---")
# Mock OpenAI in init
with mock.patch('src.narrator.OpenAI'), mock.patch('src.narrator.ELEVENLABS_API_KEY', None):
    narrator = AudioEngine()
    
    # Mock _generate_single_chunk to avoid API calls and write dummy files
    def mock_gen_chunk(text, path):
        with open(path, 'wb') as f: f.write(b'\x00'*100) # dummy mp3 content
    narrator._generate_single_chunk = mock_gen_chunk

    # Mock moviepy AudioFileClip
    # We need to mock AudioFileClip to return a dummy with duration
    with mock.patch('src.narrator.AudioFileClip') as MockClip:
        mock_clip_instance = mock.MagicMock()
        mock_clip_instance.duration = 1.0 # default dummy duration
        MockClip.return_value = mock_clip_instance
        
        # Also mock concatenate_audioclips
        with mock.patch('src.narrator.concatenate_audioclips') as mock_concat:
            mock_concat.return_value.write_audiofile = mock.MagicMock()
            
            # RUN TEST
            fpath, meta = narrator.generate_voice("Test part 1. [SILENCE:2.5] Test part 2.", "test_job")
            print(f"Meta Count: {len(meta)}")
            for m in meta:
                print(f"  - {m['type']} | Dur: {m['end']-m['start']:.1f}s | Text: {m['text']}")

# 4. Test Editor Metadata Logic
print("\n--- TEST 5: EDITOR CAPTION LOGIC ---")
# Mock whisper load in init (already handled by top level patch?) 
# Yes, top level patch mocks `whisper.load_model`.
editor = VideoEditor()

# Mock metadata
meta = [
    {"start": 0.0, "end": 2.0, "text": "Hello world", "type": "speech"},
    {"start": 2.0, "end": 4.0, "text": "[SILENCE]", "type": "silence"},
    {"start": 4.0, "end": 5.0, "text": "Run", "type": "speech"}
]
style = {"method": "center_wordbeats", "uppercase": True}
# Mock TextClip because it requires ImageMagick
with mock.patch('src.editor.TextClip') as MockTextClip:
    try:
        clips = editor._generate_captions("dummy.mp3", style, {}, 5.0, meta)
        print(f"Generated {len(clips)} caption clips.")
        print("Caption Count Correct" if len(clips) == 3 else f"Caption Count Wrong: {len(clips)}")
    except Exception as e:
        print(f"Caption Gen Error: {e}")

print("\n--- SIMULATION COMPLETE ---")
