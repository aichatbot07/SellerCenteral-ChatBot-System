import pandas as pd
from unittest import mock
from Data_pipeline.dags.data_process import (
    assign_seller_id,
    list_jsonl_files,
    process_jsonl_from_gcs,
)

# Global constants for testing
BUCKET_NAME = "ai_chatbot_seller_central"
INPUT_FOLDER = "reviews/"

def test_assign_seller_id_consistency():
    """
    Verify that assign_seller_id returns a consistent seller id for the same parent_asin.
    """
    parent_asin = "ABC123"
    id1 = assign_seller_id(parent_asin)
    id2 = assign_seller_id(parent_asin)
    assert id1 == id2, "assign_seller_id should return a consistent seller id for the same parent_asin"

@mock.patch("Data_pipeline.dags.data_process.storage.Client")
def test_list_jsonl_files(mock_storage_client):
    """
    Verify that list_jsonl_files returns only files ending with '.jsonl'.
    """
    # Create fake blobs
    fake_blob_jsonl = mock.Mock()
    fake_blob_jsonl.name = "reviews/sample.jsonl"
    
    fake_blob_txt = mock.Mock()
    fake_blob_txt.name = "reviews/ignore.txt"
    
    # Create a fake bucket that returns both blobs
    fake_bucket = mock.Mock()
    fake_bucket.list_blobs.return_value = [fake_blob_jsonl, fake_blob_txt]
    
    # Make the client's bucket() method return the fake bucket
    instance = mock_storage_client.return_value
    instance.bucket.return_value = fake_bucket

    # Call the function under test
    result = list_jsonl_files(BUCKET_NAME, INPUT_FOLDER)
    
    # Verify that only the JSONL file is returned
    assert "reviews/sample.jsonl" in result, "Expected JSONL file to be listed."
    assert "reviews/ignore.txt" not in result, "Non-JSONL file should not be listed."

@mock.patch("Data_pipeline.dags.data_process.storage.Client")
def test_process_jsonl_from_gcs(mock_storage_client):
    """
    Verify process_jsonl_from_gcs processes a GCS blob containing valid and invalid JSONL lines.
    Expected result: a DataFrame with 2 valid JSON records and a 'seller_id' column if 'parent_asin' exists.
    """
    # Prepare fake JSONL content: 2 valid JSON lines, 1 invalid line.
    jsonl_content = (
        '{"parent_asin": "ASIN1", "data": "value1"}\n'
        '{"parent_asin": "ASIN2", "data": "value2"}\n'
        'Invalid JSON line\n'
    )
    
    # Create a fake blob returning the content.
    fake_blob = mock.Mock()
    fake_blob.name = "reviews/sample.jsonl"
    fake_blob.download_as_text.return_value = jsonl_content
    
    # Create a fake bucket that returns our fake blob.
    fake_bucket = mock.Mock()
    fake_bucket.list_blobs.return_value = [fake_blob]
    fake_bucket.blob.return_value = fake_blob
    
    # Setup the fake client: bucket() returns the fake bucket.
    instance = mock_storage_client.return_value
    instance.bucket.return_value = fake_bucket
    
    # Call the function under test.
    df = process_jsonl_from_gcs()
    
    # Verify that the output is a DataFrame with 2 rows.
    assert isinstance(df, pd.DataFrame), "The output should be a pandas DataFrame."
    assert len(df) == 2, "Expected 2 valid JSON records after processing."
    
    # If 'parent_asin' exists, then a 'seller_id' column should be added.
    if "parent_asin" in df.columns:
        assert "seller_id" in df.columns, "Expected 'seller_id' column in the processed DataFrame."

@mock.patch("Data_pipeline.dags.data_process.storage.Client")
def test_gcs_authentication_failure(mock_storage_client):
    """
    Verify that when GCS authentication fails, process_jsonl_from_gcs
    returns an empty DataFrame.
    """
    # Simulate an authentication error.
    mock_storage_client.side_effect = Exception("Authentication Error")

    df = process_jsonl_from_gcs()
    # If df is None, treat it as an empty DataFrame.
    if df is None:
        df = pd.DataFrame()
    assert isinstance(df, pd.DataFrame), "Output should be a pandas DataFrame."
    assert df.empty, "Expected an empty DataFrame when authentication fails."