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
    dag_id='e2e_data_loading_to_pg_dag',
    start_date=datetime(2025,2,10),
    schedule_interval=None
)



#task 1: Drop and create a table in postgresql
task_dorp_create_table=SQLExecuteQueryOperator(
    task_id='create_table_task',
    conn_id='postgres',
    sql="""
    DROP TABLE IF EXISTS staging_table;
    CREATE TABLE IF NOT EXISTs staging_table(
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    age INT,
    month VARCHAR(100),
    salary NUMERIC
    );
    """,
    dag=dag
)

#task 2: load pandas DataFrame

#load csv file into pandas DataFrame
df =pd.read_csv('emp_salary_info.csv')
#print(df.head(3))
#tuples=[tuple(x) for x in df.to_numpy()]
##print(tuples)
#column_name = ','.join(list(df.columns))
#print(column_name)

#Establish connection to postgreSQL database
conn = psycopg2.connect(
    database='airflow_db',
    user='postgres',
    password='1418',
    host='localhost',
    port='5432'
)
#define function for insert data into postgres table
def insert_df_into_pg(conn, df, table):
    start_time=time.time()
    tuples=[tuple(x) for x in df.to_numpy()]
    column_name = ','.join(list(df.columns))
    query = 'insert into %s(%s) values %%s' % (table,column_name)
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

task_load_df=PythonOperator(
    task_id='load_df_task',
    python_callable=insert_df_into_pg,
    op_kwargs={
        'conn':conn,
        'df':df,
        'table':'staging_table'
    },
    dag=dag
)

# Task 3: Use a stored procedure to transform data and load it into a fact table
task_load_final_table = SQLExecuteQueryOperator(
    task_id='load_final_table_task',
    conn_id='postgres',
    sql="""
    --postgres fact table
    DROP TABLE IF EXISTS fact_table;
    CREATE TABLE IF NOT EXISTS fact_table(
    name VARCHAR(100) NULL,
    salary NUMERIC(10,2) NULL
    );

    -- create and define postgres transform-load function
    CREATE OR REPLACE PROCEDURE transform_and_load_data()
    LANGUAGE plpgsql
    AS $procedure$
    BEGIN
        INSERT INTO fact_table(name,salary)
        SELECT name, SUM(salary) FROM staging_table
        GROUP BY name;
    END;
    $procedure$;
    CALL transform_and_load_data(); 
    """,
    dag=dag
)



task_dorp_create_table >> task_load_df >> task_load_final_table


