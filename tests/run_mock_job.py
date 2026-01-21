import sys
import os
import unittest.mock as mock
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# MOCK EVERYTHING to simulate a job run
with mock.patch("whisper.load_model"), \
     mock.patch("src.narrator.OpenAI"), \
     mock.patch("src.narrator.ELEVENLABS_API_KEY", None), \
     mock.patch("src.narrator.AudioFileClip") as MockAudioClip, \
     mock.patch("src.narrator.concatenate_audioclips") as MockConcat, \
     mock.patch("src.editor.TextClip") as MockTextClip, \
     mock.patch("src.editor.ImageClip") as MockImageClip, \
     mock.patch("src.editor.CompositeVideoClip") as MockComposite, \
     mock.patch("src.editor.concatenate_videoclips") as MockConcatVideo, \
     mock.patch("src.editor.AudioFileClip") as MockEditorAudio, \
     mock.patch("src.artist.VisualEngine.generate_images") as MockGenImages, \
     mock.patch("src.artist.VisualEngine.generate_thumbnails") as MockGenThumb, \
     mock.patch("src.writer.ScriptGenerator.generate_script") as MockGenScript, \
     mock.patch("src.topic_engine.TopicEngine.get_fresh_topic", return_value="Simulation Topic"):

    # Setup Mocks
    # Narrator: Returns dummy path and metadata
    MockConcat.return_value.write_audiofile = mock.MagicMock()
    MockAudioClip.return_value.duration = 2.0
    
    # Editor Mocks
    MockEditorAudio.return_value.duration = 32.0 # 16 scenes * 2s
    # Mock text clip chain
    MockTextClip.return_value.set_position.return_value.set_start.return_value.set_duration.return_value.resize.return_value = "CAPTION_CLIP"
    MockImageClip.return_value.set_duration.return_value.resize.return_value.crop.return_value.resize.return_value.set_position.return_value = "VIDEO_CLIP"
    MockConcatVideo.return_value.set_audio.return_value = mock.MagicMock() # final video
    MockConcatVideo.return_value.set_audio.return_value.write_videofile = mock.MagicMock()
    
    # Script Mock
    mock_script = {
        "script_text": "Scene one. Scene two. Scene three. Scene four. Scene five. Scene six. Scene seven. Scene eight. Scene nine. Scene ten. Scene eleven. Scene twelve. Scene thirteen. Scene fourteen. Scene fifteen. Scene sixteen.",
        "beat_words": ["Scene", "one"] * 16,
        "scenes": [{"location": "Start Loc", "main_subject": "Test Subj"}] * 16,
        "fact_confidence": "high",
        "narrative_pov": "I saw",
        "iconic_scene_index": 0,
        "sticky_ending_line": "End.",
        "hook_text": "Hook",
        "music_mood": "dark",
        "variants": {"hook_b": "Hook B"}
    }
    MockGenScript.return_value = mock_script
    
    # Artist Mock
    MockGenImages.return_value = ["img.jpg"] * 16
    
    # RUN MAIN
    from main import run_job
    from src.topic_engine import TopicEngine
    
    print("\n--- RUNNING MOCK JOB ---")
    topic_engine = TopicEngine({}) # Config ignored due to mock? 
    # Actually TopicEngine needs config passed to init.
    # We can pass dummy dict.
    topic_engine = mock.MagicMock()
    topic_engine.get_fresh_topic.return_value = "Mock Topic"
    
    try:
        run_job("MOCK_JOB_ID", topic_engine)
        print("Mock Job Completed Successfully.")
    except Exception as e:
        print(f"Mock Job Failed: {e}")
        import traceback
        traceback.print_exc()
