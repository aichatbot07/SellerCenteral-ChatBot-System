import pendulum #pendulum is used instad of days_ago for testing
from airflow import DAG
from airflow.operators.python import PythonOperator  #updated import for Airflow 2.0+ for testing purposes
#from airflow.utils.dates import days_ago  #commenting this out since days_ago is not used in the code due to deprecation for testing
from datetime import timedelta
from Data_pipeline.dags.dataflow_processing import read_csv_from_gcp, create_bigquery_dataset, upload_to_bigquery
from Data_pipeline.dags.fetch_data import upload_to_gcs_from_url
from Data_pipeline.dags.data_process import save_csv_to_gcs  

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    #'start_date': days_ago(1),  #commented it out since it is deprecated, using pendulum instead for testing
    # Use Pendulum to define start_date instead of days_ago
    'start_date': pendulum.today("UTC").subtract(days=1),
    'email': ['kaviarasu666@gmail.com'],
    'email_on_failure': True,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    "mlops_csv_pipeline",
    default_args=default_args,
    # Replace schedule_interval with schedule if you want to future-proof it - suggestion for testing
    schedule='@daily',
    #schedule_interval="@daily",
    catchup=False,  
)
fetch_data = PythonOperator(
    task_id="fetch_data",
    python_callable=upload_to_gcs_from_url,
    #provide_context=True,   #not needed in Airflow 2.0+ from testing
    dag=dag
)
data_processing = PythonOperator(
    task_id="data_processing",
    python_callable=save_csv_to_gcs,
    #provide_context=True,   #not needed in Airflow 2.0+ from testing
    dag=dag
)
read_csv = PythonOperator(
    task_id="read_csv",
    python_callable=read_csv_from_gcp,
    #provide_context=True,   #not needed in Airflow 2.0+ from testing
    dag=dag
)

create_dataset = PythonOperator(
    task_id='create_dataset',
    python_callable=create_bigquery_dataset,
    #provide_context=True,   #not needed in Airflow 2.0+ from testing
    dag=dag,
)
# Anamoly = PythonOperator(
#     task_id='Anamoly',
#     python_callable=validate_data_with_tfdv,
#     op_kwargs={"df": "{{ task_instance.xcom_pull(task_ids='read_csv') }}"},  
#     dag=dag,
# )

upload_bigquery = PythonOperator(
    task_id='upload_bigquery',
    python_callable=upload_to_bigquery,
    #provide_context=True,   #not needed in Airflow 2.0+ from testing
    dag=dag,
)

fetch_data >> data_processing >> read_csv >> create_dataset >> upload_bigquery

