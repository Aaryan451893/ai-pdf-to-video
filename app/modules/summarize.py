import nltk
import heapq
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

nltk.download("punkt", quiet=True)

def summarize_text(text, num_sentences=5):
    # Split into sentences
    sentences = nltk.sent_tokenize(text)
    
    if len(sentences) <= num_sentences:
        return text  # If text is short, return as is

    # Convert sentences into vectors using TF-IDF
    vectorizer = TfidfVectorizer().fit_transform(sentences)
    similarity_matrix = cosine_similarity(vectorizer, vectorizer)

    # Score sentences by sum of similarities
    sentence_scores = similarity_matrix.sum(axis=1)

    # Pick top N sentences
    top_sentence_indices = heapq.nlargest(num_sentences, range(len(sentence_scores)), sentence_scores.take)
    top_sentence_indices.sort()

    summary = " ".join([sentences[i] for i in top_sentence_indices])
    return summary
