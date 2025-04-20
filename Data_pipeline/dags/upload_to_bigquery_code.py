import os
from google.cloud import bigquery
import pandas as pd
import config
from logging_setup import log_event
import pickle
import logging

# Set GCP credentials dynamically from config.py
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config.GCP_CREDENTIALS_PATH

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_PICKLE_PATH = os.path.join(PROJECT_DIR, 'data',
                                 'processed','verified_vs_nonverified.pkl')

def upload_to_bigquery(input_pickle_path=INPUT_PICKLE_PATH):
    """Uploads a Pandas DataFrame to a BigQuery table."""
    if os.path.exists(input_pickle_path):
        with open(input_pickle_path, "rb") as file:
            df = pickle.load(file)
            logging.info(f"Merged DataFrame shape: {df.shape}")
            logging.info(f"Merged DataFrame columns: {df.columns.tolist()}")
            logging.info(f"Merged DataFrame sample:\n{df.head()}")
    else:
        raise FileNotFoundError(f"No data found at the specified path: {input_pickle_path}")
    project_id = "spheric-engine-451615-a8"
    dataset_id = "Amazon_Reviews_original_dataset_v3"
    table_id = "Amazon_dataset_V3"
    client = bigquery.Client()
    # create_bigquery_dataset(client, project_id, dataset_id)

    table_ref = f"{project_id}.{dataset_id}.{table_id}"
    job_config = bigquery.LoadJobConfig(
        autodetect=True,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )
    job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
    job.result()
    print(f" Uploaded {len(df)} rows to {table_ref}")
    log_event(" Data Successfully Processed and Loaded into BigQuery!")