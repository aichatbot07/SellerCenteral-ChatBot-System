import os
import sys
import importlib
import io
import gzip
import pytest
from unittest import mock
import config

# -- PYTHONPATH Setup --
# Ensure the repository root is in the Python path so that modules can be imported properly.
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

# -- Configuration Setup --
# Import the config module and ensure that it uses the environment variable if set,
# otherwise fallback to default values.
if not hasattr(config, "GCP_CREDENTIALS_PATH"):
    config.GCP_CREDENTIALS_PATH = os.getenv("GCP_CREDENTIALS_PATH")
if not hasattr(config, "BUCKET_NAME"):
    config.BUCKET_NAME = os.getenv("BUCKET_NAME", "ai_chatbot_seller_central")
if not hasattr(config, "FILE_NAME"):
    config.FILE_NAME = os.getenv("FILE_NAME", "new_data_sentiment.csv")
importlib.reload(config)

# -- Force Re-import of Dependent Modules --
# Remove fetch_data from sys.modules (if already imported) so that it picks up the patched config.
if "Data_pipeline.dags.fetch_data" in sys.modules:
    del sys.modules["Data_pipeline.dags.fetch_data"]

# Now import the module that uses the configuration.
from Data_pipeline.dags import fetch_data

# Global constants for testing
BUCKET_NAME = "ai_chatbot_seller_central"
FILE_NAME = "new_data_sentiment.csv"

@mock.patch("Data_pipeline.dags.fetch_data.create_retry_session")
@mock.patch("Data_pipeline.dags.fetch_data.storage.Client")
def test_upload_to_gcs_from_url_success(mock_storage_client, mock_create_retry_session):
    """
    Test the upload_to_gcs_from_url function under a successful download scenario.
    This simulates a fake HTTP response returning a gzipped stream of data and ensures
    that the file is attempted to be uploaded to GCS.
    """
    # Create a fake requests session.
    mock_session = mock.Mock()
    # Create sample data and compress it.
    sample_data = b'{"key": "value"}\n'
    gzipped_stream = io.BytesIO()
    with gzip.GzipFile(fileobj=gzipped_stream, mode="wb") as gz:
        gz.write(sample_data)
    gzipped_stream.seek(0)
    
    # Set up a fake response that simulates a successful HTTP GET.
    fake_response = mock.Mock()
    fake_response.raw = gzipped_stream
    fake_response.headers = {'Content-Length': '1000'}
    fake_response.raise_for_status = mock.Mock()
    mock_session.get.return_value = fake_response
    mock_create_retry_session.return_value = mock_session

    # Create a fake GCS client, bucket, and blob.
    mock_client = mock_storage_client.return_value
    mock_bucket = mock.Mock()
    mock_client.bucket.return_value = mock_bucket
    mock_blob = mock.Mock()
    mock_bucket.blob.return_value = mock_blob

    # Call the function under test.
    fetch_data.upload_to_gcs_from_url()

    # Verify that a download was attempted.
    assert mock_session.get.called, "Expected session.get() to be called to download the file."
    # Verify that an upload was attempted.
    assert mock_blob.upload_from_file.called, "Expected blob.upload_from_file() to be called to upload the file to GCS."

@mock.patch("Data_pipeline.dags.fetch_data.create_retry_session")
@mock.patch("Data_pipeline.dags.fetch_data.storage.Client")
def test_upload_to_gcs_from_url_download_failure(mock_storage_client, mock_create_retry_session):
    """
    Test the upload_to_gcs_from_url function when a download error occurs.
    This simulates a network error by having the session.get() method raise an Exception.
    The test expects that the function will propagate the exception.
    """
    # Simulate a download error.
    mock_session = mock.Mock()
    mock_session.get.side_effect = Exception("Download failed")
    mock_create_retry_session.return_value = mock_session

    # Setup a fake GCS client.
    mock_storage_client.return_value = mock.Mock()

    # Expect that the function raises an exception when download fails.
    with pytest.raises(Exception, match="Download failed"):
        fetch_data.upload_to_gcs_from_url()