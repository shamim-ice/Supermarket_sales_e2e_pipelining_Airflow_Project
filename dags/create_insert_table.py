from airflow import DAG
from datetime import datetime
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

dag = DAG(
    dag_id='table_create_insert_dag',
    start_date=datetime(2025,2,9),
    schedule_interval=None
)

task_table_create_insert=SQLExecuteQueryOperator(
    task_id='table_create_insert_task',
    conn_id='postgres',
    sql="""
    --DDL: Create Employees Table
CREATE TABLE IF NOT EXISTS employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    department VARCHAR(50),
    hire_date DATE,
    salary NUMERIC(10, 2)
);

--DML: Insert Sample Data

INSERT INTO employees (name, department, hire_date, salary) VALUES
('Alice Johnson', 'Engineering', '2022-01-10', 60000),
('Bob Smith', 'Engineering', '2023-03-12', 75000),
('Charlie Brown', 'Marketing', '2023-05-15', 48000),
('David Wilson', 'Marketing', '2021-07-20', 52000),
('Eve Davis', 'Sales', '2023-09-01', 30000),
('Frank Miller', 'Sales', '2022-04-25', 45000),
('Grace Lee', 'Sales', '2024-01-05', 70000),
('Heidi White', 'HR', '2020-11-11', 55000),
('Ivan Black', 'HR', '2023-08-30', 47000),
('Judy Green', 'Finance', '2021-12-01', 80000),
('Karl Blue', 'Finance', '2022-10-15', 49000),
('Liam Red', 'Engineering', '2023-02-28', 62000),
('Mona Gold', 'Engineering', '2024-03-17', 72000),
('Nina Silver', 'Marketing', '2022-09-09', 53000),
('Oscar Orange', 'Sales', '2023-07-19', 35000);
    """,

    dag=dag

)
task_table_create_insert
