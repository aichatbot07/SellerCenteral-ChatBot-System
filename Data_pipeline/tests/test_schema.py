import pytest
import pandas as pd
from google.cloud import bigquery

PROJECT_ID = "spheric-engine-451615-a8"
DATASET = "Amazon_Reviews_original_dataset_v3"
TABLE = "Amazon_dataset_V3"
FULL_TABLE = f"{PROJECT_ID}.{DATASET}.{TABLE}"


@pytest.fixture(scope="module")
def sample_dataframe():
    """Fetch sample records from BigQuery for testing."""
    client = bigquery.Client(project=PROJECT_ID)
    query = f"SELECT * FROM `{FULL_TABLE}` LIMIT 50"
    df = client.query(query).to_dataframe()
    return df


def test_required_columns(sample_dataframe):
    expected_columns = {
        'parent_asin',
        'title',
        'average_rating',
        'rating_number',
        'price',
        'most_liked_features',
        'optimal_price_min',
        'optimal_price_max',
        'performance_target',
        'predicted_performance_score',
        'bought_together',
        'main_category',
        'happier_group'
    }
    assert expected_columns.issubset(set(sample_dataframe.columns)), "Missing expected columns"


def test_no_nulls_in_required_columns(sample_dataframe):
    for col in ['parent_asin']:
        assert sample_dataframe[col].notna().all(), f"{col} contains nulls"


def test_all_other_columns_can_be_null(sample_dataframe):
    optional_columns = set(sample_dataframe.columns) - {'parent_asin'}
    null_allowed = sample_dataframe[list(optional_columns)].isnull().sum()
    assert isinstance(null_allowed, pd.Series)  # Ensure result is a valid Series


def test_schema_column_types_are_valid(sample_dataframe):
    assert pd.api.types.is_string_dtype(sample_dataframe['parent_asin']), "parent_asin should be a string"
    if 'price' in sample_dataframe.columns:
        assert pd.api.types.is_numeric_dtype(sample_dataframe['price']), "price should be numeric"
    if 'average_rating' in sample_dataframe.columns:
        assert pd.api.types.is_numeric_dtype(sample_dataframe['average_rating']), "average_rating should be numeric"
    if 'rating_number' in sample_dataframe.columns:
        assert pd.api.types.is_numeric_dtype(sample_dataframe['rating_number']), "rating_number should be numeric"


def test_print_schema_fields(sample_dataframe):
    print("\nSample DataFrame Columns:")
    for col in sample_dataframe.columns:
        print(f" - {col} ({sample_dataframe[col].dtype})")