import os
import sys

# --- Ensure the repository root is in PYTHONPATH ---
repo_root = os.path.abspath(os.path.join(os.getcwd()))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

# --- Add the 'Data_pipeline/dags' directory to PYTHONPATH ---
dags_folder_path = os.path.abspath(os.path.join(os.getcwd(), "Data_pipeline", "dags"))
if dags_folder_path not in sys.path:
    sys.path.insert(0, dags_folder_path)

# Import the config module from Data_pipeline/dags
import Data_pipeline.dags.config as config

if not hasattr(config, "GCP_CREDENTIALS_PATH"):
    config.GCP_CREDENTIALS_PATH = os.getenv("GCP_CREDENTIALS_PATH", "/opt/airflow/dags/gcp-credentials.json")
if not hasattr(config, "BUCKET_NAME"):
    config.BUCKET_NAME = os.getenv("BUCKET_NAME", "ai_chatbot_seller_central")
if not hasattr(config, "FILE_NAME"):
    config.FILE_NAME = os.getenv("FILE_NAME", "new_data_sentiment.csv")
