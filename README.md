# 📖 AI PDF to Video Lecture

Convert PDFs (like textbooks, notes) into AI-generated video lectures with voiceover.

## 🚀 Features
- Extract text from PDF
- Summarize into lecture script (via OpenAI GPT, fallback included)
- Convert script to audio (gTTS)
- Render animated text video (MoviePy)

## 🛠 Setup
```bash
git clone https://github.com/Aaryan/ai-pdf-to-video.git
cd ai-pdf-to-video
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
