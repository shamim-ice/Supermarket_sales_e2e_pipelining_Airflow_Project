from airflow import DAG
from datetime import datetime
from airflow.operators.python import PythonOperator

#define DAG
dag=DAG(
    dag_id='xcom_pass_value_dag',
    start_date=datetime(2025,2,5),
    schedule_interval=None
)

def cal_sum(**kwargs):
    n1=10
    n2=20
    res=n1+n2
    #push res to xcom
    kwargs['ti'].xcom_push(key='sum', value=res)

task_cal_sum=PythonOperator(
    task_id='cal_sum_task',
    python_callable=cal_sum,
    provide_context=True,
    dag=dag
)

def print_sum(**kwargs):
    #pull res from xcom
    sum_res = kwargs['ti'].xcom_pull(key='sum', task_ids='cal_sum_task')
    print(f'The sum is: {sum_res}')

task_print_sum=PythonOperator(
    task_id='print_sum_task',
    python_callable=print_sum,
    provide_context=True,
    dag=dag
)

task_cal_sum >> task_print_sum

