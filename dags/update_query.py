from airflow import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from datetime import datetime

#define dag
dag = DAG(
    dag_id='update_query_dag',
    start_date=datetime(2025,2,9),
    schedule_interval=None
)

#define task
task_update_query=SQLExecuteQueryOperator(
    task_id='update_query_task',
    conn_id='postgres',
    sql="""
    WITH avg_salaries AS(
    SELECT department, avg(salary) AS avg_salary FROM employees GROUP BY department)
    UPDATE employees
    SET salary=salary*2.2
    WHERE department IN(SELECT department from avg_salaries WHERE avg_salary<50000);
    """,
    dag=dag
)

task_update_query