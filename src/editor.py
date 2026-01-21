import os
import random
import whisper
from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
from .config import VIDEO_WIDTH, VIDEO_HEIGHT

class VideoEditor:
    def __init__(self):
        self.model = whisper.load_model("base")
        self.resolution = (VIDEO_WIDTH, VIDEO_HEIGHT)

    def assemble_video(self, image_paths: list, audio_path: str, output_path: str, 
                      music_mood: str, caption_style: dict, script_data: dict = None, audio_metadata: list = None):
        print(f"[*] Editor: Assembling video with mood '{music_mood}'...")
        
        # 1. Voice
        voice_clip = AudioFileClip(audio_path)
        duration = voice_clip.duration
        
        # 2. Visuals (Ken Burns)
        print("[*] Editor: Applying Ken Burns effect...")
        per_img_duration = duration / len(image_paths)
        video_clips = [self._ken_burns(img, per_img_duration) for img in image_paths]
        final_video = concatenate_videoclips(video_clips, method="compose")
        final_video = final_video.set_audio(voice_clip)

        # 3. Music (Ducking)
        music_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "music", music_mood)
        # Use default if not found
        if not os.path.exists(music_folder) or not os.listdir(music_folder):
             music_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "music", "analog_drone")

        if os.path.exists(music_folder) and os.listdir(music_folder):
            music_file = random.choice(os.listdir(music_folder))
            music_path = os.path.join(music_folder, music_file)
            print(f"[*] Editor: Adding music '{music_file}'...")
            
            music_clip = AudioFileClip(music_path)
            # Loop if short
            if music_clip.duration < duration:
                music_clip = afx.audio_loop(music_clip, duration=duration)
            else:
                music_clip = music_clip.subclip(0, duration)
            
            # Ducking (Volume 0.1)
            music_clip = music_clip.volumex(0.1)
            final_audio = CompositeAudioClip([voice_clip, music_clip])
            final_video = final_video.set_audio(final_audio)
        else:
            print("[!] Editor: No music found for mood. Skipping.")

        # 4. Captions (Kinetic or Whisper)
        print("[*] Editor: Generating captions...")
        try:
            captions = self._generate_captions(audio_path, caption_style, script_data, duration, audio_metadata)
            final_video = CompositeVideoClip([final_video] + captions)
        except Exception as e:
            print(f"[!] Editor: Caption generation failed (ImageMagick missing?). Proceeding without captions.")

        # 5. Export
        print(f"[*] Editor: Rendering to {output_path} (High Quality 5000k)...")
        final_video.write_videofile(
            output_path, 
            fps=24, 
            codec="libx264", 
            audio_codec="aac",
            bitrate="5000k",  # PATCH 10: High Bitrate
            threads=1,        # PATCH 10: Memory Safety
            preset='ultrafast'
        )

    def _ken_burns(self, img_path: str, duration: float):
        # Randomize movement: sometimes zoom IN, sometimes zoom OUT, sometimes PAN
        direction = random.choice(['in', 'out', 'pan_left', 'pan_right'])
        clip = ImageClip(img_path).set_duration(duration)
        
        # Resize to cover screen
        clip = clip.resize(height=VIDEO_HEIGHT * 1.2) # Make it 20% larger than screen to allow movement
        w, h = clip.size
        
        if direction == 'in':
            # Zoom Center
            return clip.resize(lambda t: 1 + 0.04 * t).set_position(('center', 'center'))
        elif direction == 'out':
            # Zoom Out
            return clip.resize(lambda t: 1.08 - 0.04 * t).set_position(('center', 'center'))
        elif direction == 'pan_left':
            # Pan Right to Left
            return clip.set_position(lambda t: (int(-50 * t), 'center'))
        else:
            return clip.set_position(('center', 'center'))

    def _generate_captions(self, audio_path: str, style: dict, script_data: dict, duration: float, audio_metadata: list = None):
        method = style.get("method", "whisper")
        
        # Styles
        font = style.get("font", "Arial-Bold")
        fontsize = style.get("fontsize", 70)
        color = style.get("color", "white")
        stroke_color = style.get("stroke_color", "black")
        stroke_width = style.get("stroke_width", 3)
        uppercase = style.get("uppercase", True)
        
        # PATCH 7: PRECISE SYNC WITH METADATA
        if audio_metadata:
            print("[*] Editor: Using PRECISE AUDIO METADATA for captions.")
            clips = []
            
            for segment in audio_metadata:
                if segment["type"] != "speech": continue
                
                seg_text = segment["text"]
                start_t = segment["start"]
                end_t = segment["end"]
                dur = end_t - start_t
                
                # Split words
                words = seg_text.split()
                if not words: continue
                
                per_word_time = dur / len(words)
                
                for i, word in enumerate(words):
                    txt = word.upper() if uppercase else word
                    w_start = start_t + (i * per_word_time)
                    
                    # PATCH 12: Use Pillow Renderer
                    from .text_renderer import create_text_clip
                    txt_clip = create_text_clip(
                        txt, 
                        fontsize=fontsize, 
                        font="Arial", # Force Arial for Windows stability
                        color=color, 
                        stroke_color=stroke_color, 
                        stroke_width=stroke_width,
                        size=(VIDEO_WIDTH-100, None),
                        duration=per_word_time
                    ).set_position('center').set_start(w_start)
                    
                     # Animation: Pop
                    txt_clip = txt_clip.resize(lambda t: 1 + (0.2 * t))
                    if per_word_time > 0.15: # Fade in only if enough time
                        txt_clip = txt_clip.crossfadein(0.05)
                        
                    clips.append(txt_clip)
            return clips

        # A) CENTER WORDBEATS (Legacy Naive Fallback)
        if method == "center_wordbeats" and script_data and "beat_words" in script_data:
            print("[*] Editor: Using CENTER WORDBEATS (Naive Distribution - FALLBACK)...")
            beat_words = script_data.get("beat_words", [])
            # Handle string vs list
            if isinstance(beat_words, str): 
                beat_words = beat_words.split() 
            
            if not beat_words: return []

            count = len(beat_words)
            per_word_time = duration / count
            
            clips = []

            for i, word in enumerate(beat_words):
                txt = word.upper() if uppercase else word
                start_t = i * per_word_time
                
                # PATCH 12: Use Pillow Renderer (Fallback)
                from .text_renderer import create_text_clip
                txt_clip = create_text_clip(
                    txt, 
                    fontsize=fontsize, 
                    font="Arial", 
                    color=color, 
                    stroke_color=stroke_color, 
                    stroke_width=stroke_width,
                    size=(VIDEO_WIDTH-100, None),
                    duration=per_word_time
                ).set_position('center').set_start(start_t)
                
                # Animation: Fade In + Scale Up (Pop effect)
                txt_clip = txt_clip.resize(lambda t: 1 + (0.3 * t)) # Zoom in
                if per_word_time > 0.2:
                    txt_clip = txt_clip.crossfadein(0.1)
                
                clips.append(txt_clip)
            
            return clips

        # B) WHISPER (Fallback)
        from .config import CAPTION_BACKEND
        if CAPTION_BACKEND == "whisper":
            print("[*] Editor: Using LOCAL Whisper for captions...")
            from .local_whisper import transcribe_to_srt
            srt_path = audio_path.replace(".mp3", ".srt")
            transcribe_to_srt(audio_path, srt_path)
        else:
            print("[!] Editor: Remote caption backend not implemented. Skipping.")
            return []

        # PATCH 12: Use Pillow Renderer (Generator)
        from .text_renderer import create_text_clip
        generator = lambda txt: create_text_clip(
            txt, 
            font="Arial", 
            fontsize=style.get("size", 54), 
            color=style.get("color", "white"),
            stroke_color=style.get("stroke_color", "black"), 
            stroke_width=style.get("stroke", 2),
            size=(VIDEO_WIDTH-100, None)
        )
        subtitles = SubtitlesClip(srt_path, generator)
        subtitles = subtitles.set_position(('center', 'center'))
        return [subtitles]