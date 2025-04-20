import os
import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from torch.utils.data import DataLoader
from datasets import Dataset, load_from_disk
import nltk
import pickle
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Try to download NLTK data with SSL verification disabled
# try:
#     import ssl
#     try:
#         _create_unverified_https_context = ssl._create_unverified_context
#     except AttributeError:
#         pass
#     else:
#         ssl._create_default_https_context = _create_unverified_https_context

#     nltk.download('brown')
#     nltk.download('punkt')
# except Exception as e:
#     logging.warning(f"NLTK download error: {e}. Continuing anyway...")

# Define project directory and file paths
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_PICKLE_PATH = os.path.join(PROJECT_DIR, 'data', 'processed', 'raw_data.pkl')
PREVIOUS_MODEL_OUTPUT_PATH = os.path.join(PROJECT_DIR, 'data', 'processed', 'optimal_price_range.pkl')
OUTPUT_PICKLE_PATH = os.path.join(PROJECT_DIR, 'data', 'processed', 'new_data_sentiment.pkl')
UNPROCESSED_PICKEL_PATH = os.path.join(PROJECT_DIR, 'data', 'unprocessed_pkl', 'new_data_sentiment.pkl')

def sentiment_analysis():
    """
    Performs sentiment analysis using a pretrained model,
    aggregates sentiment by 'parent_asin', and saves the results to a pickle file.
    """
    logging.info("Starting sentiment analysis")
    
    if os.path.exists(UNPROCESSED_PICKEL_PATH):
        logging.info(f"Output file {UNPROCESSED_PICKEL_PATH} already exists. Skipping processing.")
        aggregated = pd.read_pickle(UNPROCESSED_PICKEL_PATH)
        return aggregated
    else:
        logging.info("path doestn't exist so training the model")
       
    
        try:
            # Load raw data using Pandas' pickle loader
            logging.info(f"Loading raw data from {INPUT_PICKLE_PATH}")
            try:
                data = pd.read_pickle(INPUT_PICKLE_PATH)
                logging.info(f"Loaded raw data with shape: {data.shape}")
            except Exception as e:
                logging.error(f"Error loading pickle file with pd.read_pickle: {e}")
                raise FileNotFoundError(f"Could not load data from {INPUT_PICKLE_PATH}")

            # Preprocess data
            logging.info("Preprocessing data")
            data = data[data["text"].notna()]
            data = data[data["text"].str.strip() != ""]
            data = data[['text', 'parent_asin']].copy()
            logging.info(f"Preprocessed data shape: {data.shape}")
            
            # Ensure parent_asin is a string
            data['parent_asin'] = data['parent_asin'].astype(str)
            
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logging.info(f"Using device: {device}")
            
            # Load transformer model
            logging.info("Loading sentiment analysis model")
            try:
                tokenizer = AutoTokenizer.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment")
                model = AutoModelForSequenceClassification.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment").to(device)
            except Exception as e:
                logging.error(f"Error loading sentiment model: {e}")
                logging.info("Falling back to simple sentiment analysis using TextBlob")
                from textblob import TextBlob
                
                def simple_sentiment(text):
                    try:
                        return TextBlob(text).sentiment.polarity
                    except Exception:
                        return 0
                
                data["sentiment_numeric"] = data["text"].apply(simple_sentiment)
                data["sentiment_label"] = data["sentiment_numeric"].apply(
                    lambda x: "positive" if x > 0.1 else ("negative" if x < -0.1 else "neutral")
                )
                data["sentiment_score"] = data["sentiment_numeric"].abs()
                use_transformer = False
            else:
                use_transformer = True
            
            if use_transformer:
                logging.info("Creating Hugging Face dataset")
                hf_dataset = Dataset.from_pandas(data)
                dataset_disk_path = os.path.join(PROJECT_DIR, 'data', 'processed', 'hf_dataset')
                hf_dataset.save_to_disk(dataset_disk_path)
                hf_dataset = load_from_disk(dataset_disk_path)
                
                logging.info("Tokenizing dataset")
                def tokenize_function(examples):
                    return tokenizer(examples["text"], padding="max_length", truncation=True, max_length=512)
                
                tokenized_dataset = hf_dataset.map(tokenize_function, batched=True, writer_batch_size=100)
                
                def collate_fn(batch):
                    return {
                        "input_ids": torch.tensor([item["input_ids"] for item in batch]).to(device),
                        "attention_mask": torch.tensor([item["attention_mask"] for item in batch]).to(device)
                    }
                
                dataloader = DataLoader(tokenized_dataset, batch_size=32, collate_fn=collate_fn)
                
                logging.info("Running sentiment analysis")
                model.eval()
                sentiment_labels = []
                sentiment_scores = []
                
                with torch.no_grad():
                    for batch in dataloader:
                        outputs = model(input_ids=batch["input_ids"], attention_mask=batch["attention_mask"])
                        predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
                        labels = torch.argmax(predictions, dim=1).cpu().numpy()
                        scores = predictions.max(dim=1).values.cpu().numpy()
                        
                        sentiment_labels.extend(labels)
                        sentiment_scores.extend(scores)
                
                label_map = {0: "negative", 1: "neutral", 2: "positive"}
                data["sentiment_label"] = [label_map[label] for label in sentiment_labels]
                data["sentiment_score"] = sentiment_scores
                
                sentiment_map = {"negative": -1, "neutral": 0, "positive": 1}
                data["sentiment_numeric"] = data["sentiment_label"].map(sentiment_map).fillna(0)
            
            logging.info("Aggregating sentiment by product")
            grouped = data.groupby("parent_asin")
            aggregated = grouped.agg(
                overall_sentiment_score=("sentiment_numeric", "mean"),
                total_reviews=("sentiment_numeric", "size"),
                positive_count=("sentiment_numeric", lambda x: (x > 0).sum()),
                neutral_count=("sentiment_numeric", lambda x: (x == 0).sum()),
                negative_count=("sentiment_numeric", lambda x: (x < 0).sum())
            ).reset_index()
            
            # Calculate percentages
            aggregated["positive_pct"] = (aggregated["positive_count"] / aggregated["total_reviews"]) * 100
            aggregated["neutral_pct"] = (aggregated["neutral_count"] / aggregated["total_reviews"]) * 100
            aggregated["negative_pct"] = (aggregated["negative_count"] / aggregated["total_reviews"]) * 100
            
            # rename columns to avoid merge conflicts
            aggregated = aggregated.rename(columns={
                "positive_pct": "percent_positive",
                "neutral_pct": "percent_neutral",
                "negative_pct": "percent_negative"
            })
            
            logging.info(f"Final aggregated data shape: {aggregated.shape}")
            
            return aggregated
            
            return OUTPUT_PICKLE_PATH
            
        except Exception as e:
            logging.error(f"Error in sentiment_analysis: {e}")
            raise

def merge_with_previous_model_output_5():
    sentiment_df = pd.DataFrame()
    """Merge sentiment analysis results with previous model output"""
    logging.info("Starting merge with previous model output")
    
    try:
        sentiment_df = sentiment_analysis()
    except Exception as e:
        logging.error(f"Error performing sentiment analysis: {e}")
        raise
    
    if not os.path.exists(PREVIOUS_MODEL_OUTPUT_PATH):
        logging.error(f"Previous model output file not found at {PREVIOUS_MODEL_OUTPUT_PATH}")
        raise FileNotFoundError(f"Previous model output file not found: {PREVIOUS_MODEL_OUTPUT_PATH}")
    
    try:
        
        with open(PREVIOUS_MODEL_OUTPUT_PATH, "rb") as file:
            previous_df = pickle.load(file)
        logging.info(f"Loaded previous model output with shape: {previous_df.shape}")
        logging.info(f"Previous model columns: {previous_df.columns.tolist()}")
        
        # First, clean up any duplicate columns in previous_df
        # Find duplicate column patterns (e.g., optimal_price_min_x, optimal_price_min_y)
        column_groups = {}
        for col in previous_df.columns:
            if col.endswith('_x') or col.endswith('_y'):
                base_name = col.rsplit('_', 1)[0]  # Get base name without _x or _y
                if base_name not in column_groups:
                    column_groups[base_name] = []
                column_groups[base_name].append(col)
        
        # Consolidate duplicate columns
        for base_name, cols in column_groups.items():
            if len(cols) > 1:
                logging.info(f"Consolidating duplicate columns for {base_name}: {cols}")
                # Create or update the base column
                if base_name not in previous_df.columns:
                    # Create the base column using the first non-null value from duplicates
                    previous_df[base_name] = pd.NA
                    for col in cols:
                        previous_df[base_name] = previous_df[base_name].fillna(previous_df[col])
                # Drop the duplicate columns
                previous_df = previous_df.drop(columns=cols)
                logging.info(f"Created consolidated column {base_name} and dropped duplicates")
        
        # Rename any columns in sentiment_df that might cause conflicts
        sentiment_columns = sentiment_df.columns.tolist()
        for col in sentiment_columns:
            if col in previous_df.columns and col != 'parent_asin':
                new_name = f"{col}_sentiment"
                sentiment_df = sentiment_df.rename(columns={col: new_name})
                logging.info(f"Renamed column {col} to {new_name} to avoid conflicts")
        
        # Convert parent_asin to string in both dataframes
        sentiment_df['parent_asin'] = sentiment_df['parent_asin'].astype(str)
        previous_df['parent_asin'] = previous_df['parent_asin'].astype(str)
        
        # Merge data using simple left join
        result_df = pd.merge(
            previous_df,
            sentiment_df,
            on='parent_asin',
            how='outer'  # Keep all rows from both dataframes
        )
        
        # Check merge results
        logging.info(f"Merged data shape: {result_df.shape}")
        logging.info(f"Final columns: {result_df.columns.tolist()}")
        
        # Verify key columns were preserved
        important_columns = ['parent_asin', 'most_liked_features', 'bought_together', 
                            'optimal_price_min', 'optimal_price_max']
        
        for col in important_columns:
            if col in previous_df.columns and col not in result_df.columns:
                logging.error(f"Important column '{col}' was lost during merge!")
            elif col in previous_df.columns:
                logging.info(f"Column '{col}' was preserved with {result_df[col].notna().sum()} non-null values")
        
        # Save the result to the output path
        with open(OUTPUT_PICKLE_PATH, "wb") as file:
            pickle.dump(result_df, file, protocol=4)
        logging.info(f"Saved merged data to {OUTPUT_PICKLE_PATH}")
        
        return OUTPUT_PICKLE_PATH
        
    except Exception as e:
        logging.error(f"Error in merge_with_previous_model_output: {e}")
        raise
