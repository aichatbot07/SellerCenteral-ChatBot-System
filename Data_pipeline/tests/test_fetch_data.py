import io
import gzip
import pytest
import logging
from unittest import mock
import importlib.util
import os

# Load the DAG module dynamically
DAG_PATH = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "dags", "fetch_data.py"
))

def load_fetch_data_module():
    spec = importlib.util.spec_from_file_location("fetch_data", DAG_PATH)
    fetch_data = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fetch_data)
    return fetch_data

@pytest.fixture
def mock_gzip_response():
    sample_data = b'{"review": "Great product!"}\n{"review": "Bad product!"}'
    gzipped = io.BytesIO()
    with gzip.GzipFile(fileobj=gzipped, mode='wb') as f:
        f.write(sample_data)
    gzipped.seek(0)
    return gzipped

def test_upload_to_gcs_from_url(monkeypatch, mock_gzip_response, caplog):
    caplog.set_level(logging.INFO)

    # Load the real module
    fetch_data = load_fetch_data_module()

    # Mock retry session with our fake response
    mock_session = mock.Mock()
    fake_response = mock.Mock()
    fake_response.raw = mock_gzip_response
    fake_response.headers = {"Content-Length": "1234"}
    fake_response.raise_for_status = mock.Mock()
    mock_session.get.return_value = fake_response

    monkeypatch.setattr(fetch_data, "create_retry_session", lambda: mock_session)

    # Mock GCS client and bucket/blob
    mock_blob = mock.Mock()
    mock_bucket = mock.Mock()
    mock_bucket.blob.return_value = mock_blob
    mock_client = mock.Mock()
    mock_client.bucket.return_value = mock_bucket

    monkeypatch.setattr(fetch_data.storage, "Client", lambda: mock_client)

    # Run the function
    fetch_data.upload_to_gcs_from_url()

    # Assert the function made expected number of calls
    assert mock_session.get.call_count == len(fetch_data.DATASET_URLS)
    assert mock_blob.upload_from_file.called
    assert "Uploaded" in caplog.text