import sys
import os
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime



# Importing necessary functions from scripts/data_process
import data_process
from data_process import list_jsonl_files, process_jsonl_from_gcs, save_csv_to_gcs

default_args = {
    "owner": "airflow",
    "start_date": datetime(2024, 2, 20),
    "retries": 1,
}

# Define the DAG
dag = DAG(
    "amazon_review_pipeline", 
    default_args=default_args, 
    schedule_interval="@daily",  # This will run the DAG daily
    catchup=False  # Ensures that the DAG doesn't backfill past runs when the scheduler starts
)

# Define Task 1: List JSONL Files in GCS
fetch_data = PythonOperator(
    task_id="fetch_data",
    python_callable=list_jsonl_files,
    op_kwargs={"bucket_name": "ai_chatbot_seller_central", "folder_name": "reviews/"},
    dag=dag,
)

# Define Task 2: Process JSONL Files & Merge Data
process_data = PythonOperator(
    task_id="process_data",
    python_callable=process_jsonl_from_gcs,
    op_kwargs={"bucket_name": "ai_chatbot_seller_central"},
    dag=dag,
)

# Define Task 3: Save Processed Data to GCS
upload_data = PythonOperator(
    task_id="upload_data",
    python_callable=save_csv_to_gcs,
    op_kwargs={
        "bucket_name": "ai_chatbot_seller_central",
        "output_file": "processed/reviews_processed.csv",
    },
    dag=dag,
)

# Set the task dependencies to ensure they execute in the correct order
fetch_data >> process_data >> upload_data
