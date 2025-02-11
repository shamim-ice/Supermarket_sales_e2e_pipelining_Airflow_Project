from airflow import DAG
from datetime import datetime
from airflow.operators.python import PythonOperator
import time

#define DAG
dag=DAG(
    dag_id='seq_parallel_dag',
    start_time=datetime(2025,2,5),
    schedule_interval=None
)

#define simple unction for printing taks
def task_function(task_id):
    print(f'Task {task_id} is starting...')
    time.sleep(5)
    print(f'Task {task_id} is completed.')

task_1 = PythonOperator(
    task_id='task1',
    python_callable=task_function,
    op_kwargs={'task_id':1},
    dag=dag
)

task_2 = PythonOperator(
    task_id='task2',
    python_callable=task_function,
    op_kwargs={'task_id':2},
    dag=dag
)

task_3 = PythonOperator(
    task_id='task3',
    python_callable=task_function,
    op_kwargs={'task_id':3},
    dag=dag
)

task_4 = PythonOperator(
    task_id='task4',
    python_callable=task_function,
    op_kwargs={'task_id':4},
    dag=dag
)
          
task_1 >> [task_2, task_3] >> task_4