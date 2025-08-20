from transformers import pipeline, BartTokenizer

# load model + tokenizer
model_name = "facebook/bart-large-cnn"
summarizer = pipeline("summarization", model=model_name)
tokenizer = BartTokenizer.from_pretrained(model_name)

def chunk_text(text, max_tokens=900):
    """Split text into chunks within model token limit using tokenizer."""
    words = text.split()
    chunk, chunk_tokens = [], 0

    for word in words:
        tokenized = tokenizer.encode(word, add_special_tokens=False)
        if chunk_tokens + len(tokenized) > max_tokens:
            yield " ".join(chunk)
            chunk, chunk_tokens = [], 0
        chunk.append(word)
        chunk_tokens += len(tokenized)

    if chunk:
        yield " ".join(chunk)

def build_script(raw_text: str, max_points: int = 5):
    # 1) Break long text into safe chunks
    chunks = list(chunk_text(raw_text, max_tokens=900))

    # 2) Summarize each chunk
    summaries = []
    for i, chunk in enumerate(chunks, 1):
        out = summarizer(
            chunk,
            max_length=150,
            min_length=50,
            do_sample=False,
            truncation=True
        )
        summaries.append(out[0]["summary_text"])

    # 3) Merge summaries into final script
    combined = " ".join(summaries)

    # 4) Re-summarize combined summary
    final_out = summarizer(
        combined,
        max_length=200,
        min_length=80,
        do_sample=False,
        truncation=True
    )[0]["summary_text"]

    # 5) Extract key points (scenes)
    key_points = [point.strip() for point in final_out.split('.') if point.strip()][:max_points]

    return {
        "summary": final_out,
        "scenes": key_points
    }

