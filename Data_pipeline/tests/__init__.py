import os
import sys

# Add the repository root to the Python path so that the Data_pipeline package is discoverable.
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, repo_root)

# Import the config module from Data_pipeline/dags
import Data_pipeline.dags.config as config

if not hasattr(config, "GCP_CREDENTIALS_PATH"):
    config.GCP_CREDENTIALS_PATH = os.getenv("GCP_CREDENTIALS_PATH", "/opt/airflow/dags/gcp-credentials.json")
if not hasattr(config, "BUCKET_NAME"):
    config.BUCKET_NAME = os.getenv("BUCKET_NAME", "ai_chatbot_seller_central")
if not hasattr(config, "FILE_NAME"):
    config.FILE_NAME = os.getenv("FILE_NAME", "new_data_sentiment.csv")
