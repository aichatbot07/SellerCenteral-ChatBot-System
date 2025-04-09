import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
from google.cloud import bigquery
import logging

from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

# Set up logging (optional; adjust format as needed)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set API keys and tokens from environment variables
# HF_TOKEN = os.getenv("HF_TOKEN")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

if not all([GOOGLE_APPLICATION_CREDENTIALS]):
    
    raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variables are missing.")


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
