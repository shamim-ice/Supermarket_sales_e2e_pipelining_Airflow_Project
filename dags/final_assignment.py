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
def extract_data(**kwargs):
    ##read csv file from url
    url='https://raw.githubusercontent.com/plotly/datasets/refs/heads/master/supermarket_Sales.csv'
    df = pd.read_csv(url)
    #print(columns_name)
    ##create pandas DataFrame
    df = pd.DataFrame(df)
    #print(df.head(2))
    kwargs['ti'].xcom_push(key='DataFram', value=df)


task_extract_data= PythonOperator(
    task_id ='extract_data_task',
    python_callable=extract_data,
    provide_context=True,
    dag=dag
)

# Step 2: Transform Data and load to postgreSQL
##Implement data pre-processing (duplicate/missing data handling etc.) methodologies to clean the raw data.
def transform_data(**kwargs):
    df = kwargs['ti'].xcom_pull(key='DataFrame', task_ids='extract_data_task')
    df = df.fillna(0)
    kwargs['ti'].xcom_push(key='DataFram', value=df)

task_transform_data=PythonOperator(
    task_id='transform_data_task',
    python_callable=transform_data,
    provide_context=True,
    dag=dag
)

##Load transformed data from Pandas dataframe to PostgreSQL
####create staging table supermarket_sales
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
#Establish connection to postgreSQL database
conn = psycopg2.connect(
    database='airflow_db',
    user='postgres',
    password='1418',
    host='localhost',
    port='5432'
)



def insert_df_pg(conn, table, **kwargs):
    start_time=time.time()
    df = kwargs['ti'].xcom_pull(key='DataFrame', task_ids='transform_data_task')
    tuples=[tuple(x) for x in df.to_numpy()]
    #column_name = ','.join(list(df.columns))
    columns_name = df.columns  # Join column names as a single string (incorrect approach)
    formatted_columns = [s.lower().replace(" ", "_").replace("%","_percent") for s in df.columns]  # Correct approach on actual column names
    columns_name = ','.join(formatted_columns)  # Convert back to a single string
    query = 'insert into %s(%s) values %%s' % (table,columns_name)
    print(query)
    cursor=conn.cursor()
    try:
        cursor.execute(f'Delete From {table}')
        conn.commit()
        print(f'Existing records from {table} deleted successfully!')
        extras.execute_values(cursor,query,tuples)
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print('Error: %s'% error)
        conn.rollback()
        conn.close()
        return 1

    end_time=time.time()
    elapsed_time=end_time-start_time
    print('Dataframe is inserted successfully!')
    print(f'Insert Time: {elapsed_time} seconds.')
    cursor.close()



task_load_clean_data_into_postgresql=PythonOperator(
    task_id='load_clean_data_pg_task',
    python_callable=insert_df_pg,
    op_kwargs={
        'conn':conn,
        'table':'supermarket_sales'
    },
    provide_context=True,
    dag=dag
)



task_extract_data >> task_transform_data >> task_create_table >> task_load_clean_data_into_postgresql

#url='https://raw.githubusercontent.com/plotly/datasets/refs/heads/master/supermarket_Sales.csv'
#df = pd.read_csv(url)
    #print(columns_name)
    ##create pandas DataFrame
##df = pd.DataFrame(df)
#columns_name = df.columns  # Join column names as a single string (incorrect approach)
#formatted_columns = [s.lower().replace(" ", "_").replace("%","_percent") for s in df.columns]  # Correct approach on actual column names
#columns_name = ','.join(formatted_columns)  # Convert back to a single string
#print(columns_name)
