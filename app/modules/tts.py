# app/modules/tts.py
"""
Offline-first TTS:
- Tries pyttsx3 (offline) to generate a WAV.
- If you prefer gTTS (online), set use_gtts=True.
Returns the path to the generated audio file.
"""
from typing import Optional
import os

def _tts_pyttsx3(text: str, out_path: str) -> str:
    import pyttsx3
    engine = pyttsx3.init()
    # You can tweak voice/rate if you want:
    # voices = engine.getProperty('voices')
    # engine.setProperty('voice', voices[0].id)
    # engine.setProperty('rate', 175)
    engine.save_to_file(text, out_path)  # WAV recommended
    engine.runAndWait()
    return out_path

def _tts_gtts(text: str, out_path: str) -> str:
    from gtts import gTTS
    tts = gTTS(text)
    tts.save(out_path)
    return out_path

def synthesize(text: str, out_path: str = "narration.wav", use_gtts: bool = False) -> str:
    """
    If out_path ends with .mp3 and you use pyttsx3, Windows may still write WAV.
    Prefer .wav for pyttsx3.
    """
    if not text.strip():
        # Avoid empty TTS
        text = "No content provided."
    if use_gtts:
        # ensure mp3 extension for gTTS
        if not out_path.lower().endswith(".mp3"):
            out_path = os.path.splitext(out_path)[0] + ".mp3"
        return _tts_gtts(text, out_path)
    # offline first
    if not out_path.lower().endswith(".wav"):
        out_path = os.path.splitext(out_path)[0] + ".wav"
    return _tts_pyttsx3(text, out_path)
