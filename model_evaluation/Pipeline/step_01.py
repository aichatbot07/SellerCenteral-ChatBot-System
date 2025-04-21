import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'main')))
from config.config import logger, HF_TOKEN, OPENAI_API_KEY,DEEPSEEK_API_KEY,GROQ_API_KEY,LANGFUSE_PUBLIC_KEY,LANGFUSE_SECRET_KEY,LANGFUSE_HOST,GOOGLE_APPLICATION_CREDENTIALS

from sentence_transformers import SentenceTransformer, util
from testset_generate import Tata  # Import the Tata class from Code 1

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

def main():
    generator = Tata()  # Create an instance of the Tata class

    asin_list = ["B071J212M1", "B09DCNT9W8", "B008OCOJIA"]  # Example list of ASINs
    all_test_sets = []  # Collect all test set data here

    for asin in asin_list:
        review_df, meta_df = generator.fetch_product_data(asin)

        if review_df.empty or meta_df.empty:
            print(f"Data for ASIN {asin} is empty. Skipping.")
            continue

        print(f"Processing ASIN: {asin}")

        corpus_embeddings = embedding_model.encode(review_df['text'].tolist(), convert_to_tensor=True)

        # Build the test set and add to list
        test_set = generator.build_test_set(asin, review_df, corpus_embeddings)
        all_test_sets.extend(test_set)

    # Save all test sets at once
    generator.save_test_set(all_test_sets, "rag_test_set.json")
    generator.save_test_set_parquet("rag_test_set.json", "rag_test_set.parquet")
    print(f"Final test set saved/updated in 'rag_test_set.json'.")

if __name__ == "__main__":
    main()
