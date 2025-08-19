# app/main.py
from modules import pdf_utils, story_engine, tts, video_gen

def run_pipeline(pdf_path: str, output_video: str):
    print("[1/4] Extracting text from PDF...")
    raw_text = pdf_utils.extract_text(pdf_path)

    print("[2/4] Building lesson script (summary + examples + dialog)...")
    lesson = story_engine.build_script(raw_text, max_points=5)
    scenes = lesson["scenes"]
    narration_text = " ".join(lesson["points"])  # concise narration

    print("[3/4] Generating narration audio (offline TTS where possible)...")
    audio_path = tts.synthesize(narration_text, out_path="narration.wav")  # returns path

    print("[4/4] Rendering animated video...")
    video_gen.generate_video(
        audio_file=audio_path,
        scenes=scenes,
        output_file=output_video,
        fps=24,
        W=1280,
        H=720,
    )
    print(f"Done. Video saved to: {output_video}")

if __name__ == "__main__":
    # Change these if you need
    run_pipeline("sample.pdf", "lecture.mp4")
