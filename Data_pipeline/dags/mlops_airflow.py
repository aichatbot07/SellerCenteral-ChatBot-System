from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

# Import your processing module; this should not run the heavy code at import time
from dataflow_processing  import read_csv_from_gcp,create_bigquery_dataset,upload_to_bigquery

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 2, 20),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "mlops_csv_pipeline",
    schedule_interval="@daily",
    start_date=datetime(2024, 2, 20),
    catchup=False,
)


read_csv = PythonOperator(
    task_id="read_csv",
    python_callable=read_csv_from_gcp,
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
    op_args=[read_csv.output],
    dag=dag,
)

read_csv >> create_dataset >> upload_bigquery
