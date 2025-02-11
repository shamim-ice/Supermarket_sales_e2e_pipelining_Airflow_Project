from airflow import DAG
from datetime import datetime
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.operators.python import PythonOperator

#define DAG
dag=DAG(
    dag_id='count_rw_qc_dag',
    start_date=datetime(2025,2,5),
    schedule_interval=None
)

#task1 count rows and push to xcom automatically
task_count_rows=SQLExecuteQueryOperator(
    task_id='count_row_task',
    conn_id='postgres',
    sql="""
    SELECT COUNT(*) FROM employees;
    """,
    do_xcom_push=True,
    dag=dag
)

#task2: quality check based on row count
def quality_check(**kwargs):
    count_row=kwargs['ti'].xcom_pull(task_ids='count_row_task')
    if(count_row[0][0]>=10):
        print(f"Quality Check Passed:{count_row[0][0]} rows found.")
    else:
        print("Quality Check Failed: Not enough rows.")

task_qc_check=PythonOperator(
    task_id='qc_task',
    python_callable=quality_check,
    provide_context=True,
    dag=dag
)

task_count_rows >> task_qc_check