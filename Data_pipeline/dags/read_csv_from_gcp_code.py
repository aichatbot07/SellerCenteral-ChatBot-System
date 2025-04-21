import os
from google.cloud import storage
import pandas as pd
from io import BytesIO
import Data_pipeline.config as config
import pickle

# Set GCP credentials dynamically from config.py
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config.GCP_CREDENTIALS_PATH

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEFAULT_PICKLE_PATH = os.path.join(PROJECT_DIR, 'data',
                                   'processed', 'raw_data.pkl')
DEFAULT_EXCEL_PATH = os.path.join(PROJECT_DIR, 'data', 'Online Retail.xlsx')



def read_csv_from_gcp(pickle_path=DEFAULT_PICKLE_PATH, excel_path=DEFAULT_EXCEL_PATH):
    """Reads a CSV file from GCS and returns it as a Pandas DataFrame."""
    print(f"Attempting to access bucket: {config.BUCKET_NAME}")
    print(f"Attempting to access file: {config.FILE_NAME}")

    client = storage.Client()
    bucket = client.bucket(config.BUCKET_NAME)
    blob = bucket.blob(config.FILE_NAME)
    content = blob.download_as_string()
    df = pd.read_csv(BytesIO(content))
    
    
    

    os.makedirs(os.path.dirname(pickle_path), exist_ok=True)
    with open(pickle_path, "wb") as file:
        pickle.dump(df, file)
    print(f"Data saved to {pickle_path} for future use.")
    
    return   # Returning the file path (optional)
