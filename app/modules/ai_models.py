from transformers import pipeline

def load_summarizer():
    return pipeline("summarization", model="facebook/bart-large-cnn")

def summarize_text(text: str):
    summarizer = load_summarizer()
    summary = summarizer(text, max_length=150, min_length=40, do_sample=False)
    return summary[0]['summary_text']
