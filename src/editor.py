from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip
import os
from .config import VIDEO_WIDTH, VIDEO_HEIGHT

class VideoEditor:
    def __init__(self):
        self.resolution = (VIDEO_WIDTH, VIDEO_HEIGHT)

    def apply_ken_burns(self, image_path: str, duration: float) -> ImageClip:
        """
        Applies a slow zoom effect (Ken Burns) to an image.
        Scales from 1.0 to 1.1 over the duration.
        """
        # Create an ImageClip
        clip = ImageClip(image_path).set_duration(duration)
        
        # Center the image (and resize to fill screen first if needed - usually DALL-E is close)
        # We enforce our target resolution
        clip = clip.resize(height=VIDEO_HEIGHT) 
        # If width is less, resize by width
        if clip.w < VIDEO_WIDTH:
             clip = clip.resize(width=VIDEO_WIDTH)
             
        # Center crop to target resolution before zooming to ensure clean edges
        clip = clip.crop(x1=clip.w/2 - VIDEO_WIDTH/2, y1=clip.h/2 - VIDEO_HEIGHT/2, width=VIDEO_WIDTH, height=VIDEO_HEIGHT)

        # Define the zoom function
        # t is time, returns logic for resize
        def zoom_in(t):
            return 1 + 0.04 * t  # Zoom in 4% per second - subtle

        # Apply the zoom
        # Note: 'resize' in moviepy with a function works, but can be slow. 
        # An alternative is: clip.resize(lambda t : 1 + 0.02*t)
        # However, simple resize changes the frame size, which we don't want for the final output.
        # We want to zoom IN to the center.
        
        # Better approach for stability:
        # Resize the clip to be slightly larger over time, then crop to center.
        
        return clip.resize(lambda t : 1 + (0.1 * (t / duration))) \
                   .set_position(('center', 'center')) \
                   .set_fps(30) \
                   .crop(x_center=VIDEO_WIDTH/2, y_center=VIDEO_HEIGHT/2, width=VIDEO_WIDTH, height=VIDEO_HEIGHT)

    def assemble_video(self, image_paths: list, audio_path: str, output_paths: str):
        """
        Assembles the final video from images and audio.
        """
        print("[*] Assembling video...")
        
        # 1. Load Audio
        audio_clip = AudioFileClip(audio_path)
        total_duration = audio_clip.duration
        
        # 2. Calculate duration per image
        if not image_paths:
            raise ValueError("No images provided for video assembly.")
            
        duration_per_image = total_duration / len(image_paths)
        print(f"[*] Total Duration: {total_duration:.2f}s | Per Image: {duration_per_image:.2f}s")

        # 3. Create clips with Ken Burns
        video_clips = []
        for img_path in image_paths:
            clip = self.apply_ken_burns(img_path, duration_per_image)
            video_clips.append(clip)
            
        # 4. Concatenate
        final_video = concatenate_videoclips(video_clips, method="compose")
        
        # 5. Set Audio
        final_video = final_video.set_audio(audio_clip)
        
        # 6. Write File
        # Use 'libx264' for good compatibility
        # threads=4 for speed
        final_video.write_videofile(
            output_paths, 
            fps=30, 
            codec='libx264', 
            audio_codec='aac', 
            temp_audiofile='temp-audio.m4a', 
            remove_temp=True
        )
        print(f"[*] Video saved to {output_paths}")

if __name__ == "__main__":
    # Test
    # editor = VideoEditor()
    pass
