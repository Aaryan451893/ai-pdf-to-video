import pyttsx3

def synthesize(text: str, output_path: str = "narration.wav"):
    """Offline lightweight TTS using pyttsx3 (for free users)."""
    engine = pyttsx3.init()
    engine.save_to_file(text, output_path)
    engine.runAndWait()
    return output_path
