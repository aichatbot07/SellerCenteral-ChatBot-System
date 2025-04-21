import os
import sys
import pickle
import pytest
import pandas as pd
from unittest import mock
from textblob import TextBlob

# Fix path for module import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from Data_pipeline.dags.product_features import (
    safe_load_pickle,
    extract_features
)

# Fixtures
@pytest.fixture
def sample_dataframe():
    return pd.DataFrame({
        'parent_asin': ['ASIN1', 'ASIN1', 'ASIN2'],
        'text': ['This is a great product. Love the battery life.',
                 'Battery lasts long and quality is amazing.',
                 'Affordable and efficient.']
    })

@pytest.fixture
def missing_columns_dataframe():
    return pd.DataFrame({
        'asin': ['ASIN1', 'ASIN2'],
        'review': ['Text 1', 'Text 2']
    })

# Tests
def test_safe_load_pickle_success_pickle(tmp_path, sample_dataframe):
    path = tmp_path / "test.pkl"
    sample_dataframe.to_pickle(path)
    df = safe_load_pickle(str(path))
    assert isinstance(df, pd.DataFrame)
    assert "parent_asin" in df.columns

def test_safe_load_pickle_fallback_to_csv(tmp_path, sample_dataframe):
    pickle_path = tmp_path / "broken.pkl"
    csv_path = tmp_path / "broken.csv"

    # Simulate corrupted pickle file
    with open(pickle_path, "wb") as f:
        f.write(b"corrupted content")

    # Save valid sample data as CSV
    sample_dataframe.to_csv(csv_path, index=False)

    df = safe_load_pickle(str(pickle_path))
    assert isinstance(df, pd.DataFrame)
    assert "parent_asin" in df.columns
    assert len(df) == 3

def test_extract_features_success(tmp_path, sample_dataframe):
    input_path = tmp_path / "input.pkl"
    output_path = tmp_path / "output.pkl"
    sample_dataframe.to_pickle(input_path)

    extract_features(str(input_path), str(output_path))
    assert output_path.exists()
    with open(output_path, "rb") as f:
        result = pickle.load(f)
    assert "most_liked_features" in result.columns

def test_extract_features_missing_column(tmp_path, missing_columns_dataframe):
    input_path = tmp_path / "input.pkl"
    output_path = tmp_path / "output.pkl"
    missing_columns_dataframe.to_pickle(input_path)
    with pytest.raises(ValueError):
        extract_features(str(input_path), str(output_path))

def test_extract_features_no_text(tmp_path):
    df = pd.DataFrame({'parent_asin': ['A'], 'text': [None]})
    input_path = tmp_path / "input.pkl"
    output_path = tmp_path / "output.pkl"
    df.to_pickle(input_path)

    extract_features(str(input_path), str(output_path))
    with open(output_path, "rb") as f:
        result = pickle.load(f)
    assert "No features identified" in result["most_liked_features"].values

def test_extract_features_textblob_error(tmp_path):
    df = pd.DataFrame({'parent_asin': ['A'], 'text': ['This might crash']})
    input_path = tmp_path / "input.pkl"
    output_path = tmp_path / "output.pkl"
    df.to_pickle(input_path)

    # Mock noun_phrases to raise error
    with mock.patch("textblob.TextBlob.noun_phrases", new_callable=mock.PropertyMock) as mock_noun_phrases:
        mock_noun_phrases.side_effect = Exception("fail")
        extract_features(str(input_path), str(output_path))

    with open(output_path, "rb") as f:
        result = pickle.load(f)
    assert "Error processing text" in result["most_liked_features"].values

def test_extract_features_skips_if_exists(tmp_path, sample_dataframe):
    input_path = tmp_path / "input.pkl"
    output_path = tmp_path / "output.pkl"
    sample_dataframe.to_pickle(input_path)

    dummy_result = pd.DataFrame({'parent_asin': ['A'], 'most_liked_features': ['Dummy']})
    with open(output_path, "wb") as f:
        pickle.dump(dummy_result, f)

    result = extract_features(str(input_path), str(output_path))
    with open(result, "rb") as f:
        loaded = pickle.load(f)
    assert loaded.equals(dummy_result)