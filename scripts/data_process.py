import pandas as pd
import random
from google.cloud import storage
from io import StringIO
import json

# Google Cloud Storage (GCS) Details
BUCKET_NAME = "ai_chatbot_seller_central"
INPUT_FOLDER = "reviews/"  # Folder containing JSONL files
OUTPUT_FILE = "processed/reviews_processed.csv"  # Merged CSV output path

SELLER_IDS = ["2471521", "2471522", "2471523", "2471524", "2471525"]

def list_jsonl_files(bucket_name, folder_name):
    """Lists all JSONL files in the specified GCS folder."""
    try:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blobs = list(bucket.list_blobs(prefix=folder_name))

        jsonl_files = [blob.name for blob in blobs if blob.name.endswith(".jsonl")]
        print(f"Found {len(jsonl_files)} JSONL files in {folder_name}.")
        return jsonl_files
    except Exception as e:
        print(f"Error listing files in GCS: {e}")
        return []

def process_jsonl_from_gcs(bucket_name, jsonl_files):
    """Reads and processes JSONL files from GCS, assigning seller IDs."""
    client = storage.Client()
    all_data = []

    for jsonl_file in jsonl_files:
        try:
            print(f"Processing {jsonl_file}...")

            # Download JSONL file
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(jsonl_file)
            jsonl_data = blob.download_as_text()

            valid_records = []
            invalid_lines = 0

            # Process each line individually to catch errors
            for line in jsonl_data.strip().split("\n"):
                try:
                    record = json.loads(line)
                    valid_records.append(record)
                except json.JSONDecodeError:
                    invalid_lines += 1  # Count invalid lines

            if invalid_lines > 0:
                print(f"Warning: Skipped {invalid_lines} invalid lines in {jsonl_file}")

            if not valid_records:
                print(f"Skipping {jsonl_file} - No valid data.")
                continue

            df = pd.DataFrame(valid_records)

            # Ensure 'asin' column exists before assigning seller IDs
            if "asin" in df.columns:
                df["seller_id"] = df["asin"].apply(lambda x: random.choice(SELLER_IDS))
            else:
                print(f"Skipping {jsonl_file} - missing 'asin' column.")

            all_data.append(df)

        except Exception as e:
            print(f"Error processing {jsonl_file}: {e}")

    if not all_data:
        print("No valid data found to merge.")
        return pd.DataFrame()  # Return empty DataFrame if no data

    # Merge all processed data
    merged_df = pd.concat(all_data, ignore_index=True)
    print(f"Merged {len(merged_df)} records from {len(jsonl_files)} files.")
    return merged_df

def save_csv_to_gcs(bucket_name, df, output_file):
    """Saves the processed DataFrame as a CSV file in GCS."""
    if df.empty:
        print("No data to save. Skipping CSV upload.")
        return

    try:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(output_file)

        # Convert DataFrame to CSV format
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)

        # Upload to GCS
        blob.upload_from_string(csv_buffer.getvalue(), content_type="text/csv")
        print(f"Processed data saved to: gs://{bucket_name}/{output_file}")
    except Exception as e:
        print(f"Error saving CSV to GCS: {e}")

def main():
    """Main function to process JSONL files and store the final CSV."""
    jsonl_files = list_jsonl_files(BUCKET_NAME, INPUT_FOLDER)

    if not jsonl_files:
        print("No JSONL files found in the bucket.")
        return

    # Process all JSONL files
    merged_df = process_jsonl_from_gcs(BUCKET_NAME, jsonl_files)

    # Save the merged CSV back to GCS
    save_csv_to_gcs(BUCKET_NAME, merged_df, OUTPUT_FILE)

if __name__ == "__main__":
    main()
