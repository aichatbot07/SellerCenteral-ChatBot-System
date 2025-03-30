import pytest
import pandas as pd
from Data.fetch_reviews import fetch_reviews
from Data.meta_data import fetch_metadata
from src.retriever import create_retriever_from_df

@pytest.fixture
def mock_review_data():
    return {
        "parent_asin": ["B07LFV749P", "B07LFV749P", "B07LFV749P", "B07LFV749P", "B07LFV749P"],
        "title": ["You get what you pay for", "Not for the natural look.", "Neutral lashes","Everyday use","Fabulous lashes"]
    }

@pytest.fixture
def mock_metadata():
    return {
        "parent_asin": ["B07LFV749P"],
        "seller_id": ["2471521"]
    }

def test_fetch_reviews(mock_review_data):
    asin = "B07LFV749P"
    review_df = fetch_reviews(asin)
    assert isinstance(review_df, pd.DataFrame)
    assert "parent_asin" in review_df.columns

def test_fetch_metadata(mock_metadata):
    asin = "B001234"
    meta_df = fetch_metadata(asin)
    assert isinstance(meta_df, pd.DataFrame)
    assert "product_name" in meta_df.columns

def test_create_retriever(mock_review_data):
    review_df = pd.DataFrame(mock_review_data)
    retriever = create_retriever_from_df(review_df)
    assert retriever is not None
