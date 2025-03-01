import os
from google.cloud import storage, bigquery
import pandas as pd
from io import BytesIO
import config  # Importing the config file for credentials and bucket details

# Set GCP credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config.GCP_CREDENTIALS_PATH

def read_csv_from_gcp(bucket_name, file_name):
    """Reads a CSV file from GCS and returns it as a Pandas DataFrame."""
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(file_name)
    content = blob.download_as_string()
    df = pd.read_csv(BytesIO(content))
    return df




def create_bigquery_dataset(client, project_id, dataset_id):
    """Creates a dataset in BigQuery if it doesn't exist."""
    dataset_ref = client.dataset(dataset_id)

    try:
        client.get_dataset(dataset_ref)  # Check if dataset exists
        print(f"Dataset {dataset_id} already exists.")
    except Exception:
        dataset = bigquery.Dataset(f"{project_id}.{dataset_id}")
        dataset.location = "US"  # Set location as needed
        client.create_dataset(dataset, exists_ok=True)
        print(f"Created dataset {dataset_id}.")

# Modify upload_to_bigquery function
def upload_to_bigquery(df, project_id, dataset_id, table_id):
    """Uploads a Pandas DataFrame to a BigQuery table."""
    client = bigquery.Client()

    # Ensure dataset exists
    create_bigquery_dataset(client, project_id, dataset_id)

    table_ref = f"{project_id}.{dataset_id}.{table_id}"
    job_config = bigquery.LoadJobConfig(
        autodetect=True,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
    )

    job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
    job.result()
    print(f"Uploaded {len(df)} rows to {table_ref}")


# Configuration
bucket_name = config.BUCKET_NAME
file_name = config.FILE_NAME
project_id = "spheric-engine-451615-a8"  # Replace with your GCP project ID
dataset_id = "Amazon_Reviews_original_dataset_by_Kavi"  # Replace with your BigQuery dataset name
table_id = "Amazon_dataset_by_Kavi"  # Replace with your BigQuery table name

# Process
df = read_csv_from_gcp(bucket_name, file_name)
print(df.head(5))
upload_to_bigquery(df, project_id, dataset_id, table_id)
