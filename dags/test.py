from airflow import DAG
from datetime import datetime
from airflow.operators.python import PythonOperator


dag = DAG(
    dag_id='test_git_dag',
    start_date=datetime(2025,2,8),
    schedule_interval=None
)

task = PythonOperator(
    task_id='test_git_task',
    python_callable=lambda: print('This test dag for git purpose.'),
    dag=dag
)

task