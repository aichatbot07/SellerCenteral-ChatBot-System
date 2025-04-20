import pandas as pd
import numpy as np
from textblob import TextBlob
import nltk
import pickle
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Try to download NLTK data with SSL verification disabled
try:
    import ssl
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context
    
    nltk.download('brown')
    nltk.download('punkt')
except Exception as e:
    logging.warning(f"NLTK download error: {e}. Continuing anyway...")

# Define file paths
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_PICKLE_PATH = os.path.join(PROJECT_DIR, 'data', 'processed', 'raw_data.pkl')
OUTPUT_PICKLE_PATH = os.path.join(PROJECT_DIR, 'data', 'processed', 'with_feature1.pkl')

def safe_load_pickle(file_path):
    """Load pickle file safely handling version compatibility issues"""
    try:
        # First try loading with pandas (if it's a DataFrame)
        try:
            df = pd.read_pickle(file_path)
            logging.info(f"Successfully loaded DataFrame with pandas.read_pickle")
            return df
        except:
            # If that fails, try with standard pickle
            with open(file_path, 'rb') as f:
                try:
                    data = pickle.load(f)
                    logging.info(f"Successfully loaded with standard pickle")
                    return data
                except:
                    # If that fails too, try loading as CSV if available
                    csv_path = file_path.replace('.pkl', '.csv')
                    if os.path.exists(csv_path):
                        logging.info(f"Attempting to load CSV from {csv_path}")
                        return pd.read_csv(csv_path)
                    else:
                        raise
    except Exception as e:
        logging.error(f"Error loading pickle file {file_path}: {e}")
        raise

def extract_features(input_pickle_path=INPUT_PICKLE_PATH, output_pickle_path=OUTPUT_PICKLE_PATH):
    """Extract most liked features from reviews and save as pickle"""
    logging.info("Starting feature extraction")
    
    # Check if the output file already exists
    if os.path.exists(output_pickle_path):
        logging.info(f"Output file {output_pickle_path} already exists. Skipping processing.")
        return output_pickle_path
    
    try:
        # Load the input data
        df = safe_load_pickle(input_pickle_path)
        logging.info(f"Original dataset shape: {df.shape}")
        
        # Check if required columns exist
        if 'parent_asin' not in df.columns or 'text' not in df.columns:
            missing_cols = []
            if 'parent_asin' not in df.columns:
                missing_cols.append('parent_asin')
            if 'text' not in df.columns:
                missing_cols.append('text')
            logging.error(f"Missing required columns: {missing_cols}")
            raise ValueError(f"Required columns missing: {missing_cols}")
        
        # Ensure parent_asin is a string for consistent merging
        df['parent_asin'] = df['parent_asin'].astype(str)
        
        # Extract features
        feature_results = []
        for asin, group in df.groupby('parent_asin'):
            all_text = ' '.join(group['text'].dropna())
            
            try:
                blob = TextBlob(all_text)
                noun_phrases = blob.noun_phrases
                if noun_phrases:
                    feature_freq = pd.Series(noun_phrases).value_counts(normalize=True) * 100
                    top_features = ', '.join([f"{feature.upper()}({int(freq)}%)" 
                                              for feature, freq in feature_freq.head(5).items()])
                else:
                    top_features = "No features identified"
            except Exception as e:
                logging.warning(f"Error processing text for asin {asin}: {e}")
                top_features = "Error processing text"
            
            feature_results.append({'parent_asin': asin, 'most_liked_features': top_features})
        
        # Create DataFrame and save
        features_df = pd.DataFrame(feature_results)
        logging.info(f"Extracted features for {len(features_df)} products")
        
        # Ensure parent_asin is a string before saving
        features_df['parent_asin'] = features_df['parent_asin'].astype(str)
        
        # Save as pickle file with protocol 4 for better compatibility
        with open(output_pickle_path, "wb") as file:
            pickle.dump(features_df, file, protocol=4)
        logging.info(f"Data saved to {output_pickle_path}")
        
        return output_pickle_path
        
    except Exception as e:
        logging.error(f"Error in extract_features: {e}")
        raise

if __name__ == "__main__":
    extract_features()