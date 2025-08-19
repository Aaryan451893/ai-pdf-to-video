# modules/compositor.py
from moviepy import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip

def assemble(segments, keylines, output_file, fps=24):
    clips = [VideoFileClip(seg["path"]).set_start(seg["start"]) for seg in segments]
    video = concatenate_videoclips(clips, method="compose")
    # add minimal keylines as overlays if needed
    video.write_videofile(output_file, fps=fps, codec="libx264", audio_codec="aac")
