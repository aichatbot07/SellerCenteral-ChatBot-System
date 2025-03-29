# File: Data_pipeline/tests/test_schema.py

import pytest
from google.cloud import bigquery

def test_bigquery_schema():
    """
    Test that the BigQuery table has the expected schema.
    Adjust dataset_id and table_id as needed.
    """
    client = bigquery.Client()
    # Replace with your actual dataset and table names
    dataset_id = "your_project_id.your_dataset"  
    table_id = f"{dataset_id}.your_table_name"

    table = client.get_table(table_id)
    schema = [field.name for field in table.schema]

    # Define expected columns (adjust as necessary)
    expected_columns = ["seller_id", "product_name", "price", "other_expected_column"]
    for col in expected_columns:
        assert col in schema, f"Expected column '{col}' not found in schema."