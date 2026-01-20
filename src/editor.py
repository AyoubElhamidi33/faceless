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
                      music_mood: str, caption_style: dict):
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

        # 4. Captions (Kinetic)
        print("[*] Editor: Generating captions...")
        try:
            captions = self._generate_captions(audio_path, caption_style)
            final_video = CompositeVideoClip([final_video] + captions)
        except Exception as e:
            print(f"[!] Editor: Caption generation failed: {e}")

        # 5. Export
        print(f"[*] Editor: Rendering to {output_path}...")
        final_video.write_videofile(
            output_path, 
            fps=30, 
            codec='libx264', 
            audio_codec='aac',
            threads=4,
            preset='medium'
        )

    def _ken_burns(self, img_path: str, duration: float):
        clip = ImageClip(img_path).set_duration(duration)
        # Center crop to fill 9:16
        clip = clip.resize(height=VIDEO_HEIGHT)
        if clip.w < VIDEO_WIDTH:
            clip = clip.resize(width=VIDEO_WIDTH)
        clip = clip.crop(x1=clip.w/2 - VIDEO_WIDTH/2, width=VIDEO_WIDTH, height=VIDEO_HEIGHT)
        
        # Slow zoom 1.0 -> 1.05
        return clip.resize(lambda t : 1 + (0.05 * t)).set_position('center')

    def _generate_captions(self, audio_path: str, style: dict):
        from .config import CAPTION_BACKEND
        
        # 1. Transcribe (SRT)
        if CAPTION_BACKEND == "whisper":
            print("[*] Editor: Using LOCAL Whisper for captions...")
            from .local_whisper import transcribe_to_srt
            # We save srt in the same dir as audio
            srt_path = audio_path.replace(".mp3", ".srt")
            transcribe_to_srt(audio_path, srt_path)
        else:
            # Fallback (e.g. valid OpenAI API if implemented)
            print("[!] Editor: Remote caption backend not implemented. Skipping.")
            return []

        # 2. Convert SRT to SubtitlesClip (using MoviePy)
        # Note: MoviePy's SubtitlesClip requires ImageMagick.
        # If user doesn't have ImageMagick, this will fail.
        # But for 'Kinetic Captions' we usually parse words manually if we want word-level animation.
        # However, the previous code used whisper timestamps directly from 'result'.
        # Since we now use local_whisper which saves SRT, we might want to read the SRT or output similar 'segments' struct.
        # For simplicity in this 'Trial', let's stick to reading the SRT or just parsing the segments from local_whisper if we modified it to return object.
        # But local_whisper returns srt_path.
        
        # Let's verify if we can use SubtitlesClip or if we should parse SRT manually to match previous logic.
        # Previous logic: 'result = self.model.transcribe'.
        
        # Let's use SubtitlesClip from moviepy which is standard for SRT.
        generator = lambda txt: TextClip(
            txt, 
            font=style.get("font", "Arial"), 
            fontsize=style.get("size", 54), 
            color=style.get("color", "white"),
            stroke_color=style.get("stroke_color", "black"), 
            stroke_width=style.get("stroke", 2),
            method='caption', size=(VIDEO_WIDTH-100, None)
        )
        
        # Adjust position
        pos = style.get("position", "center")
        if pos == "bottom_left":
             pos_arg = (50, VIDEO_HEIGHT - 350)
        else:
             pos_arg = ('center', 'center')

        subtitles = SubtitlesClip(srt_path, generator)
        subtitles = subtitles.set_position(pos_arg)
        
        # SubtitlesClip is a single clip, not a list. But assemble_video expects a list to concat? 
        # No, assemble_video did: `final_video = CompositeVideoClip([final_video] + captions)`
        # If captions is a list of TextClips, OK. If it's one SubtitlesClip, we wrap in list.
        return [subtitles]