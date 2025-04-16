import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pandas as pd
from google.cloud import bigquery
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()
from config.config import logger, HF_TOKEN, OPENAI_API_KEY,DEEPSEEK_API_KEY,GROQ_API_KEY,LANGFUSE_PUBLIC_KEY,LANGFUSE_SECRET_KEY,LANGFUSE_HOST,GOOGLE_APPLICATION_CREDENTIALS

import json

# Write the secret to a file to be used by the GCP client libraries
if GOOGLE_APPLICATION_CREDENTIALS and GOOGLE_APPLICATION_CREDENTIALS.startswith("{"):
    with open("/app/service_account.json", "w") as f:
        f.write(GOOGLE_APPLICATION_CREDENTIALS)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/app/service_account.json"

def fetch_reviews(asin: str) -> pd.DataFrame:
    """
    Fetches product review data for a given ASIN from BigQuery.
    Adjust the query and table names to match your BigQuery dataset.
    """
    client = bigquery.Client()
    query = f"""
    SELECT *
    FROM `spheric-engine-451615-a8.Amazon_Reviews_original_dataset_v3.Amazon_dataset_V3`
    WHERE parent_asin = '{asin}'
    """
    try:
        review_df = client.query(query).to_dataframe()
        logger.info(f"Fetched {len(review_df)} review records for ASIN: {asin}")
    except Exception as e:
        logger.exception(f"Error fetching reviews for ASIN {asin}: {e}")
        review_df = pd.DataFrame()
    return review_df
