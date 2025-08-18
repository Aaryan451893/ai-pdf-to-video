import numpy as np
import moviepy as mp
from moviepy.video.VideoClip import VideoClip


def generate_video(audio_file="narration.mp3", output_file="lecture.mp4"):
    width, height = 800, 600

    # === Load audio ===
    try:
        audio = mp.AudioFileClip(audio_file)
    except Exception as e:
        raise FileNotFoundError(f"Could not load audio file '{audio_file}': {e}")
    total_duration = audio.duration

    # === Frame generator (automatic animation) ===
    def make_frame(t):
        frame = np.zeros((height, width, 3), dtype=np.uint8)

        # Background: change color slowly with time
        r = int(100 + 50 * np.sin(t))
        g = int(100 + 50 * np.sin(t / 2))
        b = int(150 + 50 * np.cos(t / 3))
        frame[:, :] = [r, g, b]

        # "Character": bouncing circle
        radius = 50
        cx = int(width // 2 + 200 * np.sin(t))  # horizontal movement
        cy = int(height // 2 + 100 * np.cos(t / 2))  # vertical movement

        y, x = np.ogrid[:height, :width]
        mask = (x - cx) ** 2 + (y - cy) ** 2 <= radius ** 2
        frame[mask] = [255, 255, 255]  # white circle

        # "Talking effect": circle color changes with audio rhythm
        if int(t * 2) % 2 == 0:  # quick toggle
            frame[mask] = [255, 200, 0]  # yellow when talking

        return frame

     # === Build video ===
    base_clip = VideoClip(make_frame, duration=total_duration)

    # Use CompositeVideoClip from mp
    video = mp.CompositeVideoClip([base_clip])
    video = video.with_audio(audio)

    # Export video
    video.write_videofile(output_file, fps=24, codec="mpeg4")