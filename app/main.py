# app/main.py
import os
import subprocess
import urllib.request
from modules import pdf_utils, story_engine, tts, video_gen
import torch
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Device set to use {device}")

def download_wav2lip_checkpoint(checkpoint_path: str):
    os.makedirs(os.path.dirname(checkpoint_path), exist_ok=True)
    url = "https://github.com/justinjohn0306/Wav2Lip/releases/download/models/wav2lip.pth"
    print(f"Downloading Wav2Lip checkpoint from {url}...")
    urllib.request.urlretrieve(url, checkpoint_path)
    print(f"✅ Downloaded checkpoint to {checkpoint_path}")


def run_pipeline(pdf_path: str, out_path: str):
    print("[1/4] Extracting text from PDF...")
    raw_text = pdf_utils.extract_text_from_pdf(pdf_path)

    print("[2/4] Building lesson script (summary + examples + dialog)...")
    lesson = story_engine.build_script(raw_text)

    # Use "scenes" instead of "points"
    narration_text = " ".join(lesson["scenes"])  

    print("[3/4] Generating narration audio (offline TTS where possible)...")
    audio_path = tts.synthesize(narration_text, output_path="narration.wav")

    print("[4/4] Generating video with slides + narration...")
    checkpoints_path = os.path.join("checkpoints", "wav2lip.pth")
    face_path = os.path.join("assets", "face.jpg")
    output_path = "lecture.mp4"


    if not os.path.exists(checkpoints_path):
        download_wav2lip_checkpoint(checkpoints_path)


    if not os.path.exists(face_path):
        raise FileNotFoundError("Missing assets/face.jpg. Please place a portrait image in assets/face.jpg")


    # Run Wav2Lip inference
    print(f"Generating video for audio file: {audio_path}")
    subprocess.run([
    "python", "Wav2Lip/inference.py",
    "--checkpoint_path", checkpoints_path,
    "--face", face_path,
    "--audio", audio_path,
    "--outfile", output_path
    ], check=True)


    print(f"✅ Done! Video saved at {output_path}")

if __name__ == "__main__":
    # Change these if you need
    run_pipeline("sample.pdf", "lecture.mp4")
