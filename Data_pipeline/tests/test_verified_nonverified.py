import pytest
import pandas as pd
import pickle
import os
from textblob import TextBlob
from Data_pipeline.dags.verified_nonverified_6 import grouped_reviews_fn, verified_vs_nonverified_6

@pytest.fixture
def sample_raw_data(tmp_path):
    df = pd.DataFrame({
        'parent_asin': ['A1', 'A1', 'A2', 'A3', 'A3'],
        'text': [
            "Excellent quality and durable", 
            "Long-lasting battery", 
            "Affordable price and easy to use", 
            "Worst product ever", 
            "Bad experience overall"],
        'verified_purchase': [True, False, True, True, False]
    })
    path = tmp_path / "raw_data.pkl"
    df.to_pickle(path)
    return str(path), df

@pytest.fixture
def sample_previous_model_data(tmp_path):
    df = pd.DataFrame({
        'parent_asin': ['A1', 'A2', 'A3'],
        'price': [20.0, 10.0, 5.0],
        'score': [0.8, 0.9, 0.3]
    })
    path = tmp_path / "prev_model.pkl"
    df.to_pickle(path)
    return str(path), df

def test_grouped_reviews_output_format(sample_raw_data):
    _, df = sample_raw_data
    grouped = grouped_reviews_fn(df)
    assert isinstance(grouped, pd.DataFrame)
    assert 'parent_asin' in grouped.columns
    assert 'text' in grouped.columns
    assert grouped.shape[0] == df['parent_asin'].nunique()

def test_verified_vs_nonverified_success(sample_raw_data, sample_previous_model_data, tmp_path):
    raw_path, _ = sample_raw_data
    prev_path, _ = sample_previous_model_data
    output_path = tmp_path / "verified_output.pkl"

    result_path = verified_vs_nonverified_6(
        raw_data_pickle_path=raw_path,
        previous_model_output_path=prev_path,
        output_pickle_path=str(output_path)
    )

    assert os.path.exists(result_path)
    with open(result_path, "rb") as f:
        result_df = pickle.load(f)
    assert isinstance(result_df, pd.DataFrame)
    assert "happier_group" in result_df.columns
    assert "text" in result_df.columns
    assert "parent_asin" in result_df.columns

def test_missing_raw_data_file(sample_previous_model_data, tmp_path):
    prev_path, _ = sample_previous_model_data
    missing_raw_path = tmp_path / "nonexistent.pkl"
    with pytest.raises(FileNotFoundError):
        verified_vs_nonverified_6(
            raw_data_pickle_path=str(missing_raw_path),
            previous_model_output_path=prev_path,
            output_pickle_path=str(tmp_path / "output.pkl")
        )

def test_missing_prev_model_file(sample_raw_data, tmp_path):
    raw_path, _ = sample_raw_data
    missing_prev_path = tmp_path / "nonexistent_prev.pkl"
    with pytest.raises(FileNotFoundError):
        verified_vs_nonverified_6(
            raw_data_pickle_path=raw_path,
            previous_model_output_path=str(missing_prev_path),
            output_pickle_path=str(tmp_path / "output.pkl")
        )