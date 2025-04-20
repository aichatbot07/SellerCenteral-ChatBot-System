import pandas as pd
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import torch
from typing import Dict

# Constants for sparse data phrases and thresholds
SPARSE_DATA_PHRASES = ["sparse data", "limited reviews", "insufficient information"]
NEGATIVE_SENTIMENT_THRESHOLD = 0.7
SIMILARITY_THRESHOLD = 0.6

def analyze_sentiments(reviews: pd.DataFrame) -> Dict:
    """
    Analyzes the sentiment of reviews.
    """
    sentiment_counts = {"positive": 0, "neutral": 0, "negative": 0}
    # Use a sentiment model to classify each review
    # For simplicity, assume sentiment_label is already available
    for index, row in reviews.iterrows():
        if row['sentiment_label'] == 'positive':
            sentiment_counts['positive'] += 1
        elif row['sentiment_label'] == 'negative':
            sentiment_counts['negative'] += 1
        elif row['sentiment_label'] == 'neutral':
            sentiment_counts['neutral'] += 1
    return sentiment_counts

def sparse_data_acknowledged(response: str) -> bool:
    """
    Checks if a response acknowledges sparse data by comparing its embedding with predefined sparse data phrases.
    """
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    response_embedding = embeddings.embed_query(response)
    phrase_embeddings = [embeddings.embed_query(phrase) for phrase in SPARSE_DATA_PHRASES]
    similarities = torch.tensor([torch.cosine_similarity(torch.tensor(response_embedding), torch.tensor(embeddings), dim=0) for embeddings in phrase_embeddings])
    max_similarity = torch.max(similarities).item()
    return max_similarity > SIMILARITY_THRESHOLD

def detect_bias(response: str, review_sentiments: Dict, num_reviews: int) -> Dict:
    """
    Detects bias in a response based on review sentiments and sparse data acknowledgment.
    """
    bias_flags = {"bias_detected": False, "bias_types": []}
    
    # Example logic for detecting bias
    if num_reviews < 4 and not sparse_data_acknowledged(response):
        bias_flags["bias_detected"] = True
        bias_flags["bias_types"].append("missing_data_acknowledgment")
    
    # Additional logic can be added based on review sentiments and response content
    return bias_flags
