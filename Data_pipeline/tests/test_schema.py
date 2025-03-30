from google.cloud import bigquery

def test_bigquery_schema_amazon_dataset_v4():
    """
    Verify that the 'Amazon_dataset_V4' table in the 
    'Amazon_Reviews_original_dataset_v4' dataset has the expected schema.
    """
    # Create a BigQuery client (ensure GOOGLE_APPLICATION_CREDENTIALS is set externally)
    client = bigquery.Client()
    
    # Define fully qualified dataset and table name.
    dataset_id = "spheric-engine-451615-a8.Amazon_Reviews_original_dataset_v4"
    table_id = f"{dataset_id}.Amazon_dataset_V4"
    
    # Retrieve the table and extract its schema (list of field names).
    table = client.get_table(table_id)
    schema = [field.name for field in table.schema]
    
    # Expected columns for the Amazon_dataset_V4 table.
    expected_columns = [
        "parent_asin",
        "most_liked_features"
    ]
    
    for col in expected_columns:
        assert col in schema, f"Expected column '{col}' not found in schema for table {table_id}"

def test_bigquery_schema_meta_data():
    """
    Verify that the 'meta_data' table in the 
    'Amazon_Reviews_original_dataset_v4' dataset has the expected schema.
    """
    client = bigquery.Client()
    
    dataset_id = "spheric-engine-451615-a8.Amazon_Reviews_original_dataset_v4"
    table_id = f"{dataset_id}.meta_data"
    
    table = client.get_table(table_id)
    schema = [field.name for field in table.schema]
    
    # Expected columns for the meta_data table.
    expected_columns = [
        "average_rating",
        "bought_together",
        "categories",
        "description",
        "details",
        "features",
        "images",
        "main_category",
        "parent_asin",
        "price",
        "rating_number",
        "store",
        "title",
        "videos",
        "seller_id"
    ]
    
    for col in expected_columns:
        assert col in schema, f"Expected column '{col}' not found in schema for table {table_id}"

if __name__ == "__main__":
    test_bigquery_schema_amazon_dataset_v4()
    test_bigquery_schema_meta_data()
    print("All BigQuery schema tests passed.")