import os
import sys
import importlib

# Step 1: Ensure the repository root is in the Python path.
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, repo_root)

# Step 2: Import and monkey-patch the config module before any module that uses it is imported.
import Data_pipeline.dags.config as config
if not hasattr(config, "GCP_CREDENTIALS_PATH"):
    config.GCP_CREDENTIALS_PATH = os.getenv("GCP_CREDENTIALS_PATH", "/opt/airflow/dags/gcp-credentials.json")
if not hasattr(config, "BUCKET_NAME"):
    config.BUCKET_NAME = os.getenv("BUCKET_NAME", "ai_chatbot_seller_central")
if not hasattr(config, "FILE_NAME"):
    config.FILE_NAME = os.getenv("FILE_NAME", "new_data_sentiment.csv")
importlib.reload(config)

# Step 3: Remove fetch_data from sys.modules (if already imported) to force re-import with patched config.
if "Data_pipeline.dags.fetch_data" in sys.modules:
    del sys.modules["Data_pipeline.dags.fetch_data"]

# Step 4: Now import fetch_data (which uses config)
from Data_pipeline.dags import fetch_data

import io
import gzip
import pytest
from unittest import mock

BUCKET_NAME = "ai_chatbot_seller_central"
FILE_NAME = "new_data_sentiment.csv"

@mock.patch("Data_pipeline.dags.fetch_data.create_retry_session")
@mock.patch("Data_pipeline.dags.fetch_data.storage.Client")
def test_upload_to_gcs_from_url_success(mock_storage_client, mock_create_retry_session):
    """
    Test the upload_to_gcs_from_url function when download and upload succeed.
    This test mocks the requests session and the GCS client so that:
      - A fake gzipped response is returned from the dataset URL.
      - The GCS blob's upload_from_file method is called.
    """
    # Create a fake requests session.
    mock_session = mock.Mock()
    # Create sample data and compress it into a gzipped stream.
    sample_data = b'{"key": "value"}\n'
    gzipped_stream = io.BytesIO()
    with gzip.GzipFile(fileobj=gzipped_stream, mode="wb") as gz:
        gz.write(sample_data)
    gzipped_stream.seek(0)

    # Prepare a fake response that simulates a successful HTTP GET.
    fake_response = mock.Mock()
    fake_response.raw = gzipped_stream
    fake_response.headers = {'Content-Length': '1000'}
    fake_response.raise_for_status = mock.Mock()
    mock_session.get.return_value = fake_response
    mock_create_retry_session.return_value = mock_session

    # Setup a fake GCS client, bucket, and blob.
    mock_client = mock_storage_client.return_value
    mock_bucket = mock.Mock()
    mock_client.bucket.return_value = mock_bucket
    mock_blob = mock.Mock()
    # Ensure that bucket.blob() returns our fake blob.
    mock_bucket.blob.return_value = mock_blob

    # Call the function under test; it will iterate over DATASET_URLS.
    fetch_data.upload_to_gcs_from_url()

    # Assert that the session's get() was called (i.e. a download was attempted).
    assert mock_session.get.called, "The session.get() method should be called to download the file."
    # Assert that the GCS blob's upload_from_file() method was called to upload the file.
    assert mock_blob.upload_from_file.called, "The blob.upload_from_file() method should be called to upload the file to GCS."

@mock.patch("Data_pipeline.dags.fetch_data.create_retry_session")
@mock.patch("Data_pipeline.dags.fetch_data.storage.Client")
def test_upload_to_gcs_from_url_download_failure(mock_storage_client, mock_create_retry_session):
    """
    Test the upload_to_gcs_from_url function when a download error occurs.
    This test simulates a failure in the requests session (e.g., network error) and
    verifies that the error is re-raised.
    """
    # Simulate a download error by having session.get() raise an Exception.
    mock_session = mock.Mock()
    mock_session.get.side_effect = Exception("Download failed")
    mock_create_retry_session.return_value = mock_session

    # Setup a fake GCS client (won't be used because download fails).
    mock_storage_client.return_value = mock.Mock()

    # Expect that the function re-raises the exception.
    with pytest.raises(Exception, match="Download failed"):
        fetch_data.upload_to_gcs_from_url()