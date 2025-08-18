from modules import pdf_utils, summarize, tts, video_gen

def run_pipeline(pdf_path, output_video):
    # 1. Extract text
    text = pdf_utils.extract_text_from_pdf(pdf_path)
    
    # 2. Summarize text
    summary = summarize.summarize_text(text)
    
    # 3. Convert summary to audio
    audio_path = "output_audio.mp3"
    tts.text_to_speech(summary, audio_path)
    
    # 4. Generate video
    video_gen.generate_video(audio_path, output_video)
    print(f" Video created at: {output_video}")

if __name__ == "__main__":
    run_pipeline("sample.pdf", "lecture.mp4")
