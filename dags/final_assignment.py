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
    kwargs['ti'].xcom_push(key='DataFrame', value=df)


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
    # drop any row if contain NaN (missing) value
    df = df.dropna()
    # drop duplicate rows
    df = df.drop_duplicates() 
    # drop duplicate invoice_id
    df = df.drop_duplicates(subset=['Invoice ID'], keep='first')
    # drop duplicate columns
    df =df.loc[:, ~df.T.duplicated()] 
    # drop constant columns
    df =  df.loc[:, df.apply(pd.Series.nunique) > 1] 
    kwargs['ti'].xcom_push(key='DataFrame', value=df)

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
    -- gross_margin_percentage NUMERIC(10,2),
    -- gross_income NUMERIC(10,2),
    customer_stratification_rating NUMERIC(10,2)
    );
    """,
    dag=dag
)
#Establish connection to postgreSQL database
conn = psycopg2.connect(
    database='airflow_db',
    user='postgres',
    password='1418',   #password
    host='localhost',
    port='5432'
)



def insert_df_pg(conn, table, **kwargs):
    start_time=time.time()
    df = kwargs['ti'].xcom_pull(key='DataFrame', task_ids='transform_data_task')
    tuples=[tuple(x) for x in df.to_numpy()]
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


task_create_dim_fact_table=SQLExecuteQueryOperator(
    task_id='create_dim_fact_table_task',
    conn_id='postgres',
    sql="""
    -- branch dimension
    drop table if exists dim_branch CASCADE;
    create table if not exists dim_branch(
    branch_id SERIAL primary key,
    branch VARCHAR(100),
    city VARCHAR(100)
    );

    -- customer dimension
    drop table if exists dim_customer CASCADE;
    create table if not exists dim_customer(
    customer_id SERIAL primary key,
    customer_type VARCHAR(100)
    );

     -- gender dimension
    drop table if exists dim_gender CASCADE;
    create table if not exists dim_gender(
    gender_id SERIAL primary key,
    gender VARCHAR(100)
    );

    -- product dimension
    drop table if exists dim_product CASCADE;
    create table if not exists dim_product(
    product_id SERIAL primary key,
    product_line VARCHAR(100)
    );

    -- payment dimension
    drop table if exists dim_payment CASCADE;
    create table if not exists dim_payment(
    payment_id SERIAL primary key,
    payment varchar(100)
    );

    -- date dimension
    drop table if exists dim_sales_date CASCADE;
    create table if not exists dim_sales_date(
    date_id SERIAL primary key,
    date DATE
    );


    -- fact table
    drop table if exists fact_sales CASCADE;
    create table if not exists fact_sales(
    invoice_id VARCHAR(100) primary key,
    branch_id INT references dim_branch(branch_id),
    cutstomer_id INT references dim_customer(customer_id),
    gender_id INT references dim_gender(gender_id),
    product_id INT references dim_product(product_id),
    unit_price NUMERIC(10,2),
    quantity INT,
    cost_of_goods_sold NUMERIC(10,2),
    tax_5_percent NUMERIC(10,2),
    total NUMERIC(10,2),
    payment_id INT references dim_payment(payment_id),
    date_id  INT references dim_sales_date(date_id),
    time TIME,
    customer_satisfiction_rating NUMERIC(10,2) 
    );

    """,
    dag=dag
)

task_load_final_data=SQLExecuteQueryOperator(
    task_id='load_fanal_data_task',
    conn_id='postgres',
    sql="""
    CREATE OR REPLACE PROCEDURE transform_and_load_data()
    LANGUAGE plpgsql
    AS $procedure$
    BEGIN
        insert into dim_branch(branch,city)
        select distinct branch, city from supermarket_sales ss ;
        
        insert into dim_customer(customer_type)
        select distinct customer_type from supermarket_sales;

        insert into dim_gender(gender)
        select distinct gender from supermarket_sales ss;

        insert into dim_product(product_line)
        select distinct product_line from supermarket_sales ss ;

        insert into dim_payment(payment)
        select distinct payment from supermarket_sales ss ;

        insert into dim_sales_date(date)
        select distinct date from supermarket_sales ss ;

        insert into fact_sales(invoice_id, branch_id, cutstomer_id, gender_id, product_id, unit_price, 
        quantity, cost_of_goods_sold , tax_5_percent, total, payment_id,  date_id, time, customer_satisfiction_rating)
        select distinct(ss.invoice_id), db.branch_id , dc.customer_id , dg.gender_id, dp.product_id , ss.unit_price , 
        ss.quantity , ss.cost_of_goods_sold , ss.tax_5_percent , ss.total , dpm.payment_id, dsd.date_id , 
        ss.time, ss.customer_stratification_rating 
        from supermarket_sales ss
        join dim_branch db on ss.branch=db.branch  
        join dim_customer dc on ss.customer_type=dc.customer_type
        join dim_gender dg on ss.gender=dg.gender
        join dim_product dp on ss.product_line=dp.product_line
        join dim_payment dpm on ss.payment=dpm.payment
        join dim_sales_date dsd on ss.date=dsd.date;
    END;
    $procedure$;
    CALL transform_and_load_data(); 
    """,
    dag=dag
)



task_extract_data >> task_transform_data >> task_create_table >> \
task_load_clean_data_into_postgresql >> task_create_dim_fact_table >> task_load_final_data

#url='https://raw.githubusercontent.com/plotly/datasets/refs/heads/master/supermarket_Sales.csv'
#df = pd.read_csv(url)
    #print(columns_name)
    ##create pandas DataFrame
##df = pd.DataFrame(df)
#columns_name = df.columns  # Join column names as a single string (incorrect approach)
#formatted_columns = [s.lower().replace(" ", "_").replace("%","_percent") for s in df.columns]  # Correct approach on actual column names
#columns_name = ','.join(formatted_columns)  # Convert back to a single string
#print(columns_name)
