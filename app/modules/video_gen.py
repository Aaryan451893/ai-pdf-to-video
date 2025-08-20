# app/modules/video_gen.py
import os
import subprocess
import logging

# Configure logging for better error reporting
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_video(audio_file: str, scenes: list, output_file: str):
    """
    Generate talking head using Wav2Lip (open source).
    """
    # For now, just join scenes into a text script (unused downstream yet)
    text_script = " ".join(scenes)
    logging.info(f"Generating video for audio file: {audio_file}")

    # Define the expected output file path from Wav2Lip
    wav2lip_output_dir = os.path.join("Wav2Lip", "results")
    gen_file = os.path.join(wav2lip_output_dir, "result_voice.mp4")

    # Generate talking head with Wav2Lip
    cmd = [
        "python", "inference.py",
        "--checkpoint_path", "checkpoints/wav2lip.pth",
        "--face", "avatar.png",
        "--audio", os.path.abspath(audio_file),
        "--outfile", gen_file
    ]

    try:
        logging.info("Running Wav2Lip subprocess...")
        # Run the subprocess with error checking
        result = subprocess.run(cmd, cwd="Wav2Lip", check=True, capture_output=True, text=True)
        logging.info("Wav2Lip stdout:\n" + result.stdout)
        logging.info("Wav2Lip stderr:\n" + result.stderr)
        logging.info("Wav2Lip process completed successfully.")

    except subprocess.CalledProcessError as e:
        logging.error(f"Wav2Lip subprocess failed with exit code {e.returncode}")
        logging.error(f"stdout: {e.stdout}")
        logging.error(f"stderr: {e.stderr}")
        return None  # Return None to signal failure

    # Check if the generated file exists before moving it
    if os.path.exists(gen_file):
        logging.info(f"Wav2Lip output file found: {gen_file}")
        try:
            # Move the result to the final output location
            os.rename(gen_file, output_file)
            logging.info(f"File successfully moved to {output_file}")
            return output_file
        except Exception as e:
            logging.error(f"Failed to move file: {e}")
            return None
    else:
        logging.error(f"Wav2Lip output file not found at expected path: {gen_file}")
        return None