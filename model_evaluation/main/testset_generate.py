import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.config import logger, HF_TOKEN, OPENAI_API_KEY,DEEPSEEK_API_KEY,GROQ_API_KEY,LANGFUSE_PUBLIC_KEY,LANGFUSE_SECRET_KEY,LANGFUSE_HOST,GOOGLE_APPLICATION_CREDENTIALS
import pandas as pd
from google.cloud import bigquery
from dotenv import load_dotenv
import logging
import json
from typing import List

from openai import OpenAI
from sentence_transformers import SentenceTransformer, util

import json

# Write the secret to a file to be used by the GCP client libraries
if GOOGLE_APPLICATION_CREDENTIALS and GOOGLE_APPLICATION_CREDENTIALS.startswith("{"):
    with open("/app/service_account.json", "w") as f:
        f.write(GOOGLE_APPLICATION_CREDENTIALS)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/app/service_account.json"
    
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
client = OpenAI()

# ----------- BigQuery Data Fetching Functions -----------

class Tata:
    def fetch_product_data(self, asin: str) -> tuple[pd.DataFrame, pd.DataFrame]:
        client = bigquery.Client()
        results = []
        
        queries = {
            'reviews': f"""
                SELECT * 
                FROM `spheric-engine-451615-a8.Amazon_Reviews_original_dataset_v3.Amazon_dataset_V3`
                WHERE parent_asin = '{asin}'
            """,
            'metadata': f"""
                SELECT * 
                FROM `spheric-engine-451615-a8.Amazon_Reviews_original_dataset_v4.meta_data`
                WHERE parent_asin = '{asin}'
            """
        }

        for name, query in queries.items():
            try:
                df = client.query(query).to_dataframe()
                logger.info(f"Fetched {len(df)} {name} records for ASIN: {asin}")
                results.append(df)
            except Exception as e:
                logger.exception(f"Error fetching {name} for ASIN {asin}: {e}")
                results.append(pd.DataFrame())

        return tuple(results)

    def retrieve_context(self, question: str, review_df, corpus_embeddings) -> str:
        question_embedding = embedding_model.encode(question, convert_to_tensor=True)
        similarities = util.cos_sim(question_embedding, corpus_embeddings)[0]
        top_index = similarities.argmax().item()
        return review_df.iloc[top_index]['text']

    def generate_qa_from_doc(self, doc_text: str) -> List[dict]:
        prompt = f"""
        You are a helpful assistant. Based on the following product metadata or customer review:
        
        "{doc_text}"
        
        Generate a list of 3 QA pairs. Each question should be relevant, answerable from the text, and fact-based.
        
        Format:
        [
        {{
            "question": "...",
            "answer": "..."
        }},
        ...
        ]
        """
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        qa_pairs = json.loads(response.choices[0].message.content)
        return qa_pairs

    def generate_answer(self, question: str, context: str) -> str:
        prompt = f"""
        You are a question-answering assistant. Answer the following question using the provided context only.
        
        Context:
        {context}
        
        Question: {question}
        Answer:
        """
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content.strip()

    def build_test_set(self, asin: str, review_df: pd.DataFrame, corpus_embeddings) -> List[dict]:
        test_set = []
        for _, row in review_df.iterrows():
            qa_pairs = self.generate_qa_from_doc(row['text'])
            for qa in qa_pairs:
                context = self.retrieve_context(qa["question"], review_df, corpus_embeddings)
                generated = self.generate_answer(qa["question"], context)
                test_set.append({
                    "asin": asin,
                    "question": qa["question"],
                    "ground_truth_answer": qa["answer"],
                    "retrieved_context": context,
                    "generated_answer": generated
                })
        return test_set

    def save_test_set(self, test_set: List[dict], filename: str):
    # Always overwrite and create a new JSON file with the current test set
        with open(filename, "w") as f:
            json.dump(test_set, f, indent=4)

    def save_test_set_parquet(self, json_file, filename: str):
        df = pd.read_json(json_file)
        df.to_parquet(filename, engine='pyarrow')
        print(f"Converted JSON to Parquet and saved at: {filename}")

        
