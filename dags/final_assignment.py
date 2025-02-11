from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from datetime import datetime
import time
import psycopg2
import psycopg2.extras as extras
import pandas as pd

#defin dag
dag=DAG(
    dag_id='supermarket_sales_eTOe_dag',
    start_date=datetime(2025,2,10),
    schedule_interval=None
)

# Step 1: Extract Data
df = pd.read_csv('/home/shamim/Downloads/supermarket_sales.csv')
columns_name = ','.join(df.columns)  # Join column names as a single string (incorrect approach)
formatted_columns = [s.lower().replace(" ", "_").replace("%","_percent") for s in df.columns]  # Correct approach on actual column names
columns_name = ','.join(formatted_columns)  # Convert back to a single string
#print(columns_name)
#tuples=[tuple(x) for x in df.to_numpy()]


# Step 2: Transform Data
task_create_table=SQLExecuteQueryOperator(
    task_id='create_table_task',
    conn_id='postgres',
    sql="""
    DROP TABLE IF EXISTS supermarket_sales;
    CREATE TABLE IF NOT EXISTS supermarket_sales(
    invoice_id VARCHAR(100) PRIMARY KEY,
    branch VARCHAR(100),
    city VARCHAR(100),
    customer_type VARCHAR(100),
    gender VARCHAR(100),
    product_line VARCHAR(100),
    unit_price NUMERIC(10,2),
    quantity INT,
    tax_5_percent NUMERIC(10,2),
    total NUMERIC(10,2),
    date DATE,
    time TIME,  -- Use TIME if only storing time; use TIMESTAMP for date and time
    payment VARCHAR(100),
    cost_of_goods_sold NUMERIC(10,2),
    gross_margin_percentage NUMERIC(10,2),
    gross_income NUMERIC(10,2),
    customer_stratification_rating NUMERIC(10,2)
    );
    """,
    dag=dag
)

task_create_table
