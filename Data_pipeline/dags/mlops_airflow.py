from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
from dataflow_processing import read_csv_from_gcp, create_bigquery_dataset, upload_to_bigquery

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

read_csv = PythonOperator(
    task_id="read_csv",
    python_callable=read_csv_from_gcp,
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
    op_kwargs={"df": "{{ task_instance.xcom_pull(task_ids='read_csv') }}"},  
    dag=dag,
)

read_csv >> create_dataset >> upload_bigquery
