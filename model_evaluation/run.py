from utils import load_evaluation_dataset
from evaluate_retrieval import evaluate_retrieval
from evaluate_responses import evaluate_responses
from src.chain import create_qa_chain
from src.retriever import create_retriever_from_df
from Data.meta_data import fetch_metadata
from Data.fetch_reviews import fetch_reviews

# Prompt the user to enter the ASIN number
asin = input("Enter the product's ASIN number: ")

# Load the evaluation dataset
dataset = load_evaluation_dataset("evaluation_framework/evaluation_dataset.json")

# Fetch reviews and metadata for the given ASIN
review_df = fetch_reviews(asin)
meta_df = fetch_metadata(asin)

# Create a retriever from the reviews DataFrame
retriever = create_retriever_from_df(review_df)

# Create a QA chain using the retriever
qa_chain = create_qa_chain(retriever)

# Evaluate retrieval performance
retriever_results = evaluate_retrieval(dataset, retriever)
print("Retrieval Performance:", retriever_results)

# Evaluate response quality
response_results = evaluate_responses(dataset, qa_chain)
print("Response Quality:", response_results)
