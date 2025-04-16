import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
from google.cloud import bigquery

from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

from config.config import logger, HF_TOKEN, OPENAI_API_KEY,DEEPSEEK_API_KEY,GROQ_API_KEY,LANGFUSE_PUBLIC_KEY,LANGFUSE_SECRET_KEY,LANGFUSE_HOST,GOOGLE_APPLICATION_CREDENTIALS

def fetch_metadata(asin: str) -> pd.DataFrame:
    """
    Fetches product metadata for a given ASIN from BigQuery.
    Adjust the query and table names as necessary.
    """
    client = bigquery.Client()
    query = f"""
    SELECT *
    FROM `spheric-engine-451615-a8.Amazon_Reviews_original_dataset_v4.meta_data`
    WHERE parent_asin = '{asin}'
    """
    try:
        meta_df = client.query(query).to_dataframe()
        logger.info(f"Fetched {len(meta_df)} metadata records for ASIN: {asin}")
    except Exception as e:
        logger.exception(f"Error fetching metadata for ASIN {asin}: {e}")
        meta_df = pd.DataFrame()
    return meta_df
