import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config')))
from config import logger, HF_TOKEN, OPENAI_API_KEY,DEEPSEEK_API_KEY,GROQ_API_KEY,LANGFUSE_PUBLIC_KEY,LANGFUSE_SECRET_KEY,LANGFUSE_HOST,GOOGLE_APPLICATION_CREDENTIALS
import json
import torch
import pandas as pd
from pathlib import Path
import logging
from collections import Counter
from transformers import pipeline
from typing import List, Dict
from langchain_deepseek import ChatDeepSeek
from langchain_core.output_parsers import StrOutputParser
# from utils.common import save_json, make_serializable
# from utils.database import connect_with_db
from langchain.prompts import ChatPromptTemplate

from google.cloud import bigquery
import json


class BiasDetection:
    def __init__(self):
        self.results = {}
        self.evaluation_results = self.read_parquet("rag_test_set.parquet")

        # self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    def read_parquet(self, path):
            df = pd.read_parquet(path)
            return df
    
    def fetch_product_data(self, asin: str):
        client = bigquery.Client()
        results = []
        
        queries = {
            'reviews': f"""
                SELECT * 
                FROM `spheric-engine-451615-a8.Amazon_Reviews_original_dataset_v3.Amazon_dataset_V3`
                WHERE parent_asin = '{asin}'
            """
        }

        for name, query in queries.items():
            try:
                df = client.query(query).to_dataframe()
                logger.info(f"Fetched {len(df)} {name} records for ASIN: {asin}")
            except Exception as e:
                logger.exception(f"Error fetching {name} for ASIN {asin}: {e}")
                results.append(pd.DataFrame())

        return df
    
    def analyze_sentiments_model(self):
        # sentiment_counts = Counter({"positive": 0, "neutral": 0, "negative": 0})

        llm = ChatDeepSeek(model_name="deepseek-chat", temperature=0.5)
    
        system_prompt = ''' Classify the sentiment of the following text as positive, neutral, or negative, taking into account nuances such as sarcasm, mixed sentiments, or implicit tone. 
                            Provide a clear and concise classification. 
                            Here are some examples to guide your response:

                            Examples:
                            1.	Text: “I absolutely love this product! It works perfectly every time.”
                                Output: Positive
                            2.	Text: “It’s okay, does the job, but nothing extraordinary.”
                                Output: Neutral
                            3.	Text: “Terrible experience. It broke the first day I used it.”
                                Output: Negative

                            Text: {review}
                            Output: (Positive/Neutral/Negative)
                            '''
        sentiment_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
        ]
    )
        parser = StrOutputParser()
        model_chain = sentiment_prompt | llm | parser

        return model_chain

    def analyze_sentiments(self, texts: List[str]) -> Counter:
        sentiment_counts = Counter({"positive": 0, "neutral": 0, "negative": 0})
    
        for review in texts:
            try:
                # Send each review to the LLM for classification
                analyze_sentiments_model = self.analyze_sentiments_model()
                sentiment_response = analyze_sentiments_model.invoke({"review": review})

                sentiment = sentiment_response.lower()
                if 'positive' in sentiment:
                    sentiment_counts['positive'] += 1
                elif 'negative' in sentiment:
                    sentiment_counts['negative'] += 1
                elif 'neutral' in sentiment:
                    sentiment_counts['neutral'] += 1
                else:
                    print(f"Unexpected sentiment response: {sentiment_response}")

            except Exception as e:
                print(f"Error analyzing sentiment for review: {review}. Error: {e}")
        
        return sentiment_counts
    
    def analyze_sentiments_prob_model(self):
        # sentiment_counts = Counter({"positive": 0, "neutral": 0, "negative": 0})

        llm = ChatDeepSeek(model_name="deepseek-chat", temperature=0.5)
    
        system_prompt = ''' Analyze the sentiment of the following text and provide the likelihoods for positive, neutral, and negative sentiments. 
                            Output the result as a JSON object with keys 'positive', 'neutral', and 'negative', where the values are probabilities as decimals (e.g., 0.7).

                            Examples:
                            1.	Text: “This product is fantastic and exceeded my expectations.”
                                Output:
                                {{
                                    "positive": 0.9,
                                    "neutral": 0.1,
                                    "negative": 0.0
                                }}

                            2.	Text: “It’s fine, nothing special but not bad either.”
                                Output:
                                {{
                                    "positive": 0.2,
                                    "neutral": 0.7,
                                    "negative": 0.1
                                }}

                            3.	Text: “Absolutely terrible, a complete waste of money.”
                                Output:
                                {{
                                    "positive": 0.0,
                                    "neutral": 0.1,
                                    "negative": 0.9
                                }}

                            Text: "{response}"
                            Output: (Provide a output in JSON format like the examples above in text format. And dont add extra characters)
                            And also please remove json and ``` from the output
                            '''
        sentiment_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
        ]
    )
        parser = StrOutputParser()
        model_chain = sentiment_prompt | llm | parser

        return model_chain
    
    def analyze_sentiments_probs(self, response: str) -> Dict[str, float]:
        analyze_sentiments_prob_model = self.analyze_sentiments_prob_model()
        response = analyze_sentiments_prob_model.invoke({'response': response})
        cleaned_response = response.strip('json').strip('').strip()
        print(cleaned_response)

        try:
            # Parse the cleaned response string as JSON
            sentiment_probs = json.loads(cleaned_response)
            return sentiment_probs
        except json.JSONDecodeError as e:
            print(f"Error parsing sentiment probabilities: {e}")
            return {"positive": 0.0, "neutral": 0.0, "negative": 0.0}
        
    def bias_detection(self, response: str, review_sentiments: Counter, num_reviews: int) -> Dict:
        response_probs = self.analyze_sentiments_probs(response)
        response_prob_neg = response_probs.get("negative", 0.0)

        review_pos = review_sentiments.get("positive", 0)
        review_neg = review_sentiments.get("negative", 0)

        bias_flags = {"bias_detected": False, "bias_types": []}

        if response_prob_neg > 0.7 and review_neg > review_pos:
            bias_flags["bias_detected"] = True
            bias_flags["bias_types"].append("over_reliance_on_negative")

        # if num_reviews < 4 and not self.sparse_data_acknowledged(response):

        #     bias_flags["bias_detected"] = True
        #     bias_flags["bias_types"].append("missing_data_acknowledgment")

        return bias_flags
    
    def save_json(self, path: Path, data: dict):
        """save json data

        Args:
            path (Path): path to json file
            data (dict): data to be saved in json file
        """
        with open(path, "w") as f:
            json.dump(data, f, indent=4)

        logger.info(f"json file saved at: {path}")

    def make_serializable(self, data):
        """Recursively convert sets to lists and handle other non-serializable types."""
        if isinstance(data, set):
            return list(data)  # Convert set to list
        elif isinstance(data, dict):
            return {key: self.make_serializable(value) for key, value in data.items()}  # Recursively process dicts
        elif isinstance(data, list):
            return [self.make_serializable(item) for item in data]  # Recursively process lists
        else:
            return data

    def save_score(self):
            self.save_json(path=Path(f"bias-scores.json"), data=self.make_serializable(self.results))
        
    def detect(self):
        for index, row in self.evaluation_results.iterrows():
            response = row["generated_answer"]
            asin = row["asin"]
            logger.info(f"Detecting Bias for asin: {asin}")

            reviews = self.fetch_product_data(asin)
            review_sentiments = self.analyze_sentiments(reviews['text'].to_list())

            bias_data = self.bias_detection(
                response=response,
                review_sentiments=review_sentiments,
                num_reviews=len(reviews),
            )
            
            if asin not in self.results:
                self.results[asin] = {
                    "bias_detected_count": 0,
                    "bias_types": set(),
                    "num_reviews": len(reviews),
                    "review_sentiments": review_sentiments,
                }

            if bias_data["bias_detected"]:
                self.results[asin]["bias_detected_count"] += 1
                self.results[asin]["bias_types"].update(bias_data["bias_types"])

        self.save_score()