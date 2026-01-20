from faster_whisper import WhisperModel
import os

model_size = os.getenv("WHISPER_MODEL", "small")
# Run on CPU by default for broad compatibility, or "cuda" if available
device = "cpu" 
compute_type = "int8"

def transcribe_to_srt(audio_path: str, srt_path: str):
    print(f"[*] LocalWhisper: Loading model '{model_size}' on {device}...")
    model = WhisperModel(model_size, device=device, compute_type=compute_type)

    print(f"[*] LocalWhisper: Transcribing {audio_path}...")
    segments, info = model.transcribe(audio_path, beam_size=5)

    print(f"[*] LocalWhisper: Detected language '{info.language}' with probability {info.language_probability}")

    with open(srt_path, "w", encoding="utf-8") as f:
        for i, segment in enumerate(segments, start=1):
            # Format timestamp: 00:00:00,000
            start = _format_timestamp(segment.start)
            end = _format_timestamp(segment.end)
            text = segment.text.strip()
            
            f.write(f"{i}\n")
            f.write(f"{start} --> {end}\n")
            f.write(f"{text}\n\n")
    
    print(f"[*] LocalWhisper: Saved captions to {srt_path}")
    return srt_path

def _format_timestamp(seconds: float):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
