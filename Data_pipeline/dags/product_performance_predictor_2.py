import os
import pickle
import pandas as pd
import numpy as np
import pytest

from Data_pipeline.dags.product_performance_predictor_2 import (
    safe_pickle_load,
    merge_performance_and_features
)

@pytest.fixture
def dummy_metadata_pickle(tmp_path):
    data = pd.DataFrame({
        'parent_asin': ['A1', 'A2', 'A3'],
        'main_category': ['Electronics', 'Books', 'Toys'],
        'title': ['Product A', 'Product B', 'Product C'],
        'average_rating': [4.5, 4.0, 3.0],
        'rating_number': [100, 200, 50],
        'price': [29.99, 15.00, 12.50]
    })
    path = tmp_path / "meta_data.pkl"
    data.to_pickle(path)
    return path

@pytest.fixture
def dummy_feature_pickle(tmp_path):
    features = pd.DataFrame({
        'parent_asin': ['A1', 'A2', 'A3'],
        'most_liked_features': ['Battery(40%)', 'Design(30%)', 'Durability(25%)']
    })
    path = tmp_path / "with_feature1.pkl"
    with open(path, "wb") as f:
        pickle.dump(features, f)
    return path

def test_safe_pickle_load_success(tmp_path):
    test_df = pd.DataFrame({'col': [1, 2, 3]})
    pkl_path = tmp_path / "test.pkl"
    test_df.to_pickle(pkl_path)
    loaded = safe_pickle_load(str(pkl_path))
    assert isinstance(loaded, pd.DataFrame)
    assert list(loaded['col']) == [1, 2, 3]

def test_merge_performance_and_features(tmp_path, dummy_metadata_pickle, dummy_feature_pickle, monkeypatch):
    # Patch the file paths
    monkeypatch.setattr("Data_pipeline.dags.product_performance_predictor_2.INPUT_FILE_PATH", str(dummy_metadata_pickle))
    monkeypatch.setattr("Data_pipeline.dags.product_performance_predictor_2.PREVIOUS_MODEL_OUTPUT_PATH", str(dummy_feature_pickle))
    monkeypatch.setattr("Data_pipeline.dags.product_performance_predictor_2.OUTPUT_PICKLE_PATH", str(tmp_path / "output.pkl"))
    monkeypatch.setattr("Data_pipeline.dags.product_performance_predictor_2.UNPROCESSED_PICKEL_PATH", str(tmp_path / "unprocessed.pkl"))

    output_path = merge_performance_and_features()
    assert os.path.exists(output_path)

    with open(output_path, "rb") as f:
        result = pickle.load(f)

    assert "parent_asin" in result.columns
    assert "predicted_performance_score" in result.columns
    assert "most_liked_features" in result.columns
    assert len(result) >= 3  # At least the 3 dummy rows