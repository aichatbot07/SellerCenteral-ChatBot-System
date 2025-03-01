import os
from google.cloud import storage, bigquery
import pandas as pd
from io import BytesIO
import config  # Import your config file

# Set GCP credentials globally before using any GCP service
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config.GCP_CREDENTIALS_PATH

def read_csv_from_gcp():
    """Reads a CSV file from GCS and returns it as a Pandas DataFrame."""
    bucket_name = config.BUCKET_NAME
    file_name = config.FILE_NAME
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    content = blob.download_as_string()
    df = pd.read_csv(BytesIO(content))
    return df

def create_bigquery_dataset():
    """Creates a dataset in BigQuery if it doesn't exist."""
    project_id = "spheric-engine-451615-a8"  # Your GCP project ID
    dataset_id = "Amazon_Reviews_original_dataset_by_Kavi"  # Your BigQuery dataset name
    client = bigquery.Client()
    dataset_ref = client.dataset(dataset_id)

    try:
        client.get_dataset(dataset_ref)  # Check if dataset exists
        print(f"Dataset {dataset_id} already exists.")
    except Exception:
        dataset = bigquery.Dataset(f"{project_id}.{dataset_id}")
        dataset.location = "US"
        client.create_dataset(dataset, exists_ok=True)
        print(f"Created dataset {dataset_id}.")

def upload_to_bigquery(df):
    """Uploads a Pandas DataFrame to a BigQuery table."""
    project_id = "spheric-engine-451615-a8"
    dataset_id = "Amazon_Reviews_original_dataset_by_Kavi"
    table_id = "Amazon_dataset_by_Kavi"
    client = bigquery.Client()

    table_ref = f"{project_id}.{dataset_id}.{table_id}"
    job_config = bigquery.LoadJobConfig(
        autodetect=True,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
    )
    job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
    job.result()
    print(f"Uploaded {len(df)} rows to {table_ref}")
