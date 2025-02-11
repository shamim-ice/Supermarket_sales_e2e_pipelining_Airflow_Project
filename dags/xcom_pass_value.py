from airflow import DAG
from datetime import datetime
from airflow.operators.python import PythonOperator

#define DAG
dag=DAG(
    dag_id='xcom_pass_value_dag',
    start_time=datetime(2025,2,5),
    schedule_interval=None
)