import os
import pickle
import pandas as pd
import numpy as np
import pytest

from Data_pipeline.dags.optimal_price_range_4 import (
    clean_price,
    maximum_profitability_strategy,
    merge_with_previous_model_output
)

# ---------- Fixtures ----------

@pytest.fixture
def sample_data():
    return pd.DataFrame({
        'main_category': ['Electronics', 'Electronics', 'Books'],
        'price': ['$20.99', '$25.00', '15.75'],
        'rating_number': [100, 50, 200],
        'parent_asin': ['A1', 'A2', 'B1']
    })

@pytest.fixture
def sample_previous_bundle(tmp_path):
    df = pd.DataFrame({
        'parent_asin': ['A1', 'A2', 'B1'],
        'bought_together': ['A2 | B1', 'A1 | B1', 'A1 | A2'],
        'most_liked_features': ['Battery', 'Performance', 'Affordable']
    })
    path = tmp_path / "best_bundled_together.pkl"
    with open(path, "wb") as f:
        pickle.dump(df, f)
    return path

# ---------- Unit Tests ----------

def test_clean_price_valid():
    assert clean_price("$12.99") == 12.99
    assert clean_price("30.00") == 30.0
    assert clean_price("USD 45") == 45.0

def test_clean_price_invalid():
    assert np.isnan(clean_price(None))
    assert np.isnan(clean_price("Free"))
    assert np.isnan(clean_price(""))

def test_maximum_profitability_strategy_valid(tmp_path, sample_data):
    input_path = tmp_path / "meta_data.pkl"
    output_path = tmp_path / "result.pkl"
    sample_data.to_pickle(input_path)

    result = maximum_profitability_strategy(
        input_file_path=str(input_path),
        unprocessed_pickle_path=tmp_path / "dummy_unprocessed.pkl",
        output_pickle_path=str(output_path)
    )

    assert isinstance(result, pd.DataFrame)
    assert "optimal_price_min" in result.columns
    assert "optimal_price_max" in result.columns

def test_merge_with_previous_model_output(tmp_path, sample_data, sample_previous_bundle):
    input_path = tmp_path / "meta_data.pkl"
    output_path = tmp_path / "merged_output.pkl"
    sample_data.to_pickle(input_path)

    result_path = merge_with_previous_model_output(
        input_file_path=str(input_path),
        previous_output_path=str(sample_previous_bundle),
        output_pickle_path=str(output_path)
    )

    assert os.path.exists(result_path)
    with open(result_path, "rb") as f:
        final_df = pickle.load(f)

    assert "optimal_price_min" in final_df.columns
    assert "optimal_price_max" in final_df.columns
    assert "bought_together" in final_df.columns