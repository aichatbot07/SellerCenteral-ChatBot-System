import os
import pandas as pd
import numpy as np
from textblob import TextBlob
import nltk
nltk.download('brown')
nltk.download('punkt')
import pickle
import logging
from google.cloud import bigquery

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Define project directory and file paths
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_PICKLE_PATH = os.path.join(PROJECT_DIR, 'data', 'processed', 'raw_data.pkl')
PREVIOUS_MODEL_OUTPUT_PATH = os.path.join(PROJECT_DIR, 'data', 'processed', 'optimal_price_range.pkl')  # Updated path
OUTPUT_PICKLE_PATH = os.path.join(PROJECT_DIR, 'data', 'processed', 'verified_vs_nonverified.pkl')
UNPROCESSED_PICKEL_PATH = os.path.join(PROJECT_DIR, 'data', 'unprocessed_pkl', 'verified_vs_nonverified.pkl')

def grouped_reviews_fn(df):
    df.columns = df.columns.str.strip()

# Confirm column names
    print("Cleaned Columns:", df.columns.tolist())

    # Group and aggregate review text by product (parent_asin)
    grouped_reviews = df.groupby('parent_asin')['text'].apply(lambda texts: ' '.join(str(t) for t in texts)).reset_index()

    # Save the result to a new CSV
    grouped_reviews.to_csv("grouped_reviews_by_product.csv", index=False)
    print(grouped_reviews.head())

    logging.info("Aggregation complete!")
    return grouped_reviews

def verified_vs_nonverified_6(raw_data_pickle_path=RAW_DATA_PICKLE_PATH,
                                    previous_model_output_path=PREVIOUS_MODEL_OUTPUT_PATH,
                                    output_pickle_path=OUTPUT_PICKLE_PATH):
    
    df_sentiment = pd.DataFrame()
    grouped_reviews = pd.DataFrame()
    
    logging.info(f"checking for unprocessed pkl file")
    if os.path.exists(UNPROCESSED_PICKEL_PATH):
        logging.info(f"Output file {UNPROCESSED_PICKEL_PATH} already exists. Skipping processing.")
        df_sentiment = pd.read_pickle(UNPROCESSED_PICKEL_PATH)
       
    else:
        """
        Loads raw data and computes verified sentiment analysis, 
        loads an existing product features pickle file, and merges both 
        DataFrames on 'parent_asin'. The merged DataFrame is saved as a new pickle file.
        """
        logging.info("Starting verified vs non-verified analysis and merging with previous model output.")
        
        # Load raw data (for sentiment analysis)
        if os.path.exists(raw_data_pickle_path):
            try:
                df_raw = pd.read_pickle(raw_data_pickle_path)
                grouped_reviews = grouped_reviews_fn(df_raw)
                logging.info(f"Loaded raw data. Shape: {df_raw.shape}")
            except Exception as e:
                raise RuntimeError(f"Error reading raw data pickle file: {e}")
        else:
            raise FileNotFoundError(f"No raw data found at: {raw_data_pickle_path}")
        
        # Compute sentiment if not present (assuming raw data has 'text' and 'verified_purchase')
        if 'sentiment' not in df_raw.columns:
            logging.info("Computing sentiment from 'text' column using TextBlob.")
            df_raw['sentiment'] = df_raw['text'].apply(lambda x: TextBlob(x).sentiment.polarity if pd.notnull(x) else 0)
        else:
            logging.info("'sentiment' column already exists.")
        
        # Build verified vs non-verified sentiment results
        sentiment_results = []
        for asin, group in df_raw.groupby('parent_asin'):
            # Ensure parent_asin is a string
            asin = str(asin)
            
            # Check if verified_purchase column exists
            if 'verified_purchase' not in group.columns:
                logging.warning("'verified_purchase' column not found, assuming all purchases are verified")
                verified = group
                non_verified = pd.DataFrame()
            else:
                verified = group[group['verified_purchase']]
                non_verified = group[~group['verified_purchase']]
            
            verified_sentiment = verified['sentiment'].sum()
            non_verified_sentiment = non_verified['sentiment'].sum()
            total_sentiment = abs(verified_sentiment) + abs(non_verified_sentiment)
            
            if total_sentiment == 0:
                happier_group = "Sentiment is neutral for both"
            else:
                if verified_sentiment >= non_verified_sentiment:
                    pct = int((abs(verified_sentiment) / total_sentiment) * 100)
                    happier_group = f"{pct}% verified are happier"
                else:
                    pct = int((abs(non_verified_sentiment) / total_sentiment) * 100)
                    happier_group = f"{pct}% non-verified are happier"
            
            sentiment_results.append({'parent_asin': asin, 'happier_group': happier_group})
        
        df_sentiment = pd.DataFrame(sentiment_results)
        logging.info(f"Sentiment analysis complete. Verified vs Non-verified DataFrame shape: {df_sentiment.shape}")

    # Load previous model output file
    if os.path.exists(previous_model_output_path):
        try:
            previous_df = pd.read_pickle(previous_model_output_path)
            logging.info(f"Loaded previous model output. Shape: {previous_df.shape}")
            logging.info(f"Previous model columns: {previous_df.columns.tolist()}")
        except Exception as e:
            raise RuntimeError(f"Error reading previous model output file: {e}")
    else:
        raise FileNotFoundError(f"No previous model output file found at: {previous_model_output_path}")
    
    # Ensure parent_asin is a string in both DataFrames
    df_sentiment['parent_asin'] = df_sentiment['parent_asin'].astype(str)
    previous_df['parent_asin'] = previous_df['parent_asin'].astype(str)
    grouped_reviews['parent_asin'] = grouped_reviews['parent_asin'].astype(str)

    
    # Merge previous model output with new verified vs non-verified sentiment results
    df_merged = pd.merge(
        previous_df,
        df_sentiment,
        on='parent_asin',
        how='outer'
    )

    final_merge = pd.merge(
        df_merged,
        grouped_reviews,
        on='parent_asin',
        how='outer'
    )
    
    logging.info(f"Merged DataFrame shape: {final_merge.shape}")
    logging.info(f"Merged DataFrame columns: {final_merge.columns.tolist()}")
    logging.info(f"Merged DataFrame sample:\n{final_merge.head()}")
    
    # Save the merged DataFrame to pickle using protocol 4 for compatibility
    try:
        with open(output_pickle_path, "wb") as file:
            pickle.dump(final_merge, file, protocol=4)
        logging.info(f"Merged data saved to {output_pickle_path}.")
    except Exception as e:
        raise RuntimeError(f"Error saving merged pickle file: {e}")
    
    logging.info("Verified vs Non-Verified analysis with merged previous model output complete!")
    return output_pickle_path


