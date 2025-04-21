import os
import sys
import pickle
import pandas as pd
import pytest
from unittest import mock

# --- Step 1: Mock external modules ---
mock_config = mock.Mock()
mock_config.GCP_CREDENTIALS_PATH = "/dummy/path/to/creds.json"
mock_config.BUCKET_NAME = "mock-bucket"
mock_config.FILE_NAME = "mock.csv"
sys.modules["config"] = mock_config

mock_logging_setup = mock.Mock()
mock_logging_setup.log_event = mock.Mock()
sys.modules["logging_setup"] = mock_logging_setup

# --- Step 2: Import the DAG module (after patching sys.modules) ---
from Data_pipeline.dags import upload_to_bigquery_code

# --- Step 3: Fixtures & Tests ---
@pytest.fixture
def dummy_pickle_file(tmp_path):
    df = pd.DataFrame({
        'parent_asin': ['B01N1SE4EP', 'B00ZV9PXP2'],
        'verified': [1, 0],
        'review_sentiment': [0.8, 0.5]
    })
    path = tmp_path / "verified_vs_nonverified.pkl"
    with open(path, "wb") as f:
        pickle.dump(df, f)
    return path

@mock.patch("Data_pipeline.dags.upload_to_bigquery_code.bigquery.Client")
def test_upload_to_bigquery(mock_bq_client, dummy_pickle_file):
    mock_instance = mock.Mock()
    mock_bq_client.return_value = mock_instance
    mock_job = mock.Mock()
    mock_instance.load_table_from_dataframe.return_value = mock_job
    mock_job.result.return_value = None

    output = upload_to_bigquery_code.upload_to_bigquery(str(dummy_pickle_file))

    # Assertions
    mock_bq_client.assert_called_once()
    mock_instance.load_table_from_dataframe.assert_called_once()
    mock_logging_setup.log_event.assert_called_once_with(" Data Successfully Processed and Loaded into BigQuery!")