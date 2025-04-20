import os
from google.cloud import bigquery
import config

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config.GCP_CREDENTIALS_PATH

def create_bigquery_dataset():
    project_id = "spheric-engine-451615-a8"
    dataset_id = "Amazon_Reviews_original_dataset_v4"
    client = bigquery.Client()
    """Creates a dataset in BigQuery if it doesn't exist."""
    dataset_ref = client.dataset(dataset_id)

    try:
        client.get_dataset(dataset_ref)  # Check if dataset exists
        print(f" Dataset {dataset_id} already exists.")
    except Exception:
        dataset = bigquery.Dataset(f"{project_id}.{dataset_id}")
        dataset.location = "US"
        client.create_dataset(dataset, exists_ok=True)
        print(f" Created dataset {dataset_id}.")
        print