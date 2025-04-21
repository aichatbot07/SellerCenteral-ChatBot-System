import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config')))
from config.config import logger, HF_TOKEN, OPENAI_API_KEY,DEEPSEEK_API_KEY,GROQ_API_KEY,LANGFUSE_PUBLIC_KEY,LANGFUSE_SECRET_KEY,LANGFUSE_HOST,GOOGLE_APPLICATION_CREDENTIALS

import json
import re
from sentence_transformers import SentenceTransformer, util as st_util
from typing import List

# Initialize sentence transformer model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

class TestSetEvaluator:
    def __init__(self):
        pass

    # Function to normalize the answers (remove punctuation, lowercase)
    def normalize_answer(self, answer: str) -> str:
        answer = answer.strip().lower()
        answer = re.sub(r'[^\w\s]', '', answer)
        return answer

    # Function to calculate word-level matches
    def word_match(self, gt: str, pred: str) -> float:
        gt_words = set(self.normalize_answer(gt).split())
        pred_words = set(self.normalize_answer(pred).split())
        
        match = len(gt_words.intersection(pred_words))
        total_words = len(gt_words.union(pred_words))
        return match / total_words if total_words > 0 else 0

    # Function to evaluate the test set
    def evaluate_test_set(self, test_set: List[dict]) -> dict:
        word_matches = []
        semantic_similarities = []

        for entry in test_set:
            gt = entry["ground_truth_answer"].strip().lower()
            pred = entry["generated_answer"].strip().lower()

            # Word Match
            word_match_score = self.word_match(gt, pred)
            word_matches.append(word_match_score)

            # Semantic similarity (cosine similarity between embeddings)
            gt_embedding = embedding_model.encode(gt, convert_to_tensor=True)
            pred_embedding = embedding_model.encode(pred, convert_to_tensor=True)
            similarity = st_util.cos_sim(gt_embedding, pred_embedding).item()
            semantic_similarities.append(similarity)

        word_match_score = sum(word_matches) / len(word_matches)
        average_similarity = sum(semantic_similarities) / len(semantic_similarities)

        return {
            "Average Word Match": round(word_match_score, 4),
            "Average Semantic Similarity": round(average_similarity, 4)
        }

    # Function to load the test set from a JSON file
    def load_test_set(self, filename: str) -> List[dict]:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
        
    def save_results(self, results: dict, filename: str):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4)

# Example usage:
# evaluator = TestSetEvaluator()
# test_data = evaluator.load_test_set("your_file.json")
# results = evaluator.evaluate_test_set(test_data)
# print(results)
