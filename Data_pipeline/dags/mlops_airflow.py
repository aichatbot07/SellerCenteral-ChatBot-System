from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
from read_csv_from_gcp_code import read_csv_from_gcp
from create_bigquery_dataset_code import create_bigquery_dataset
from upload_to_bigquery_code import upload_to_bigquery
from fetch_data import upload_to_gcs_from_url
#from data_process import save_csv_to_gcs
from anamoly_handler import remove_anomalies
from product_features import extract_features
from best_bundled_together_3 import merge_with_previous_model_output_bundle
#from csv_to_pkl import convert_all_csv_to_pickle
from product_performance_predictor_2 import merge_performance_and_features
from optimal_price_range_4 import merge_with_previous_model_output
# from most_liked_feature_5 import sentiment_analysis
from verified_nonverified_6 import verified_vs_nonverified_6
#from sentiment_analysis_5 import merge_with_previous_model_output_5

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),  
    'email': ['kaviarasu666@gmail.com'],
    'email_on_failure': True,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    "mlops_csv_pipeline",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False,  
)
fetch_data = PythonOperator(
    task_id="fetch_data",
    python_callable=upload_to_gcs_from_url,
    provide_context=True, 
    dag=dag
)
# data_processing = PythonOperator(
#     task_id="data_processing",
#     python_callable=save_csv_to_gcs,
#     provide_context=True, 
#     dag=dag
# )
read_csv = PythonOperator(
    task_id="read_csv",
    python_callable=read_csv_from_gcp,
    provide_context=True, 
    dag=dag
)
removing_anamolies = PythonOperator(
    task_id="removing_anamolies",
    python_callable=remove_anomalies,
    provide_context=True, 
    dag=dag
)

# csv_to_pkl = PythonOperator(
#     task_id="csv_to_pkl",
#     python_callable=convert_all_csv_to_pickle,
#     provide_context=True, 
#     dag=dag
# )

extracting_features = PythonOperator(
    task_id="extracting_features",
    python_callable=extract_features,
    provide_context=True, 
    dag=dag
)

product_performance_predictor = PythonOperator(
    task_id="product_performance_predictor",
    python_callable=merge_performance_and_features,
    provide_context=True,
    dag=dag
)

best_bundled_together = PythonOperator(
    task_id="best_bundled_together",
    python_callable=merge_with_previous_model_output_bundle,
    provide_context=True,
    dag=dag
)

optimal_price_range = PythonOperator(
    task_id="optimal_price_range",
    python_callable=merge_with_previous_model_output,
    provide_context=True,
    dag=dag
)

# sentiment_analysis = PythonOperator(
#     task_id="sentiment_analysis",
#     python_callable=merge_with_previous_model_output_5,
#     provide_context=True,
#     dag=dag
# )

verified_vs_nonverified = PythonOperator(
    task_id="verified_vs_nonverified",
    python_callable=verified_vs_nonverified_6,
    provide_context=True,
    dag=dag
)

create_dataset = PythonOperator(
    task_id='create_dataset',
    python_callable=create_bigquery_dataset,
    dag=dag,
)

upload_bigquery = PythonOperator(
    task_id='upload_bigquery',
    python_callable=upload_to_bigquery,
    provide_context=True,
    dag=dag,
)

# read_csv >> removing_anamolies

fetch_data >> read_csv >> removing_anamolies >> extracting_features >> product_performance_predictor >> best_bundled_together >> optimal_price_range  >> verified_vs_nonverified >> create_dataset >> upload_bigquery
# sentiment_analysis >>>> sentiment_analysis