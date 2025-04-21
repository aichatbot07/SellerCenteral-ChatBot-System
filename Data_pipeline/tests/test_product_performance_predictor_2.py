import os
import pickle
import pandas as pd
import numpy as np
import pytest
import tempfile

# Import the functions from the actual module
from Data_pipeline.dags.product_performance_predictor_2 import (
    safe_pickle_load,
    merge_performance_and_features
)

@pytest.fixture
def dummy_pickle_file(tmp_path):
    """Create a dummy pickle file with a sample DataFrame."""
    df = pd.DataFrame({
        "parent_asin": ["A1", "A2"],
        "price": [10.0, 20.0]
    })
    file_path = tmp_path / "sample.pkl"
    with open(file_path, "wb") as f:
        pickle.dump(df, f)
    return str(file_path)

@pytest.fixture
def corrupted_pickle_file(tmp_path):
    """Create a corrupted pickle file for testing failure path."""
    file_path = tmp_path / "corrupted.pkl"
    with open(file_path, "wb") as f:
        f.write(b"not a pickle")
    return str(file_path)

def test_safe_pickle_load_valid(dummy_pickle_file):
    df = safe_pickle_load(dummy_pickle_file)
    assert isinstance(df, pd.DataFrame)
    assert "parent_asin" in df.columns
    assert len(df) == 2

def test_safe_pickle_load_invalid(corrupted_pickle_file):
    with pytest.raises(Exception):
        safe_pickle_load(corrupted_pickle_file)

def test_merge_performance_and_features(tmp_path, monkeypatch):
    # Mock file paths
    dummy_meta_path = tmp_path / "meta_data.pkl"
    dummy_feat_path = tmp_path / "with_feature1.pkl"
    dummy_output_path = tmp_path / "product_metadata_with_ml_performance_2.pkl"
    dummy_unprocessed_path = tmp_path / "product_metadata_with_ml_performance.pkl"

    # Dummy metadata for training
    meta_df = pd.DataFrame({
        'parent_asin': ['A1', 'A2'],
        'main_category': ['Electronics', 'Books'],
        'title': ['Item 1', 'Item 2'],
        'average_rating': [4.5, 4.0],
        'rating_number': [100, 50],
        'price': [20.0, 15.0]
    })
    meta_df.to_pickle(dummy_meta_path)

    # Dummy features for merging
    feat_df = pd.DataFrame({
        'parent_asin': ['A1', 'A2'],
        'most_liked_features': ['Good battery', 'Affordable']
    })
    feat_df.to_pickle(dummy_feat_path)

    # Patch paths
    monkeypatch.setattr("Data_pipeline.dags.product_performance_predictor_2.INPUT_FILE_PATH", str(dummy_meta_path))
    monkeypatch.setattr("Data_pipeline.dags.product_performance_predictor_2.PREVIOUS_MODEL_OUTPUT_PATH", str(dummy_feat_path))
    monkeypatch.setattr("Data_pipeline.dags.product_performance_predictor_2.OUTPUT_PICKLE_PATH", str(dummy_output_path))
    monkeypatch.setattr("Data_pipeline.dags.product_performance_predictor_2.UNPROCESSED_PICKEL_PATH", str(dummy_unprocessed_path))

    output_path = merge_performance_and_features()

    assert os.path.exists(output_path)

    with open(output_path, "rb") as f:
        df = pickle.load(f)

    assert isinstance(df, pd.DataFrame)
    assert "parent_asin" in df.columns
    assert "predicted_performance_score" in df.columns
    assert "most_liked_features" in df.columns