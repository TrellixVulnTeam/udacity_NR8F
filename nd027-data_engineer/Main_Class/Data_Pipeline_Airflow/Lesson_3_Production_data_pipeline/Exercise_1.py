# create redshift cluster on AWS

# access Airflow /opt/airflow/start.sh
# create aws_credentials connection on Airflow
# type: Amazon Web Services
# Login: Access key
# Password: Secret key

# create redshift connection on Airflow
# Conn Id: redshift
# Conn type: Postgres
# Host: cluster end point
# Schema: DB name
# Password:xxxx
# port: 5439

#Instructions
#In this exercise, we’ll consolidate repeated code into Operator Plugins
#1 - Move the data quality check logic into a custom operator
#2 - Replace the data quality check PythonOperators with our new custom operator
#3 - Consolidate both the S3 to RedShift functions into a custom operator
#4 - Replace the S3 to RedShift PythonOperators with our new custom operator
#5 - Execute the DAG

import datetime
import logging

from airflow import DAG
from airflow.contrib.hooks.aws_hook import AwsHook
from airflow.hooks.postgres_hook import PostgresHook

from airflow.operators import (
    HasRowsOperator,
    PostgresOperator,
    PythonOperator,
    S3ToRedshiftOperator
)

import sql_statements


#
# TODO: Replace the data quality checks with the HasRowsOperator
#

dag = DAG(
    "lesson3.exercise1",
    start_date=datetime.datetime(2018, 1, 1, 0, 0, 0, 0),
    end_date=datetime.datetime(2018, 12, 1, 0, 0, 0, 0),
    schedule_interval="@monthly",
    max_active_runs=1
)

create_trips_table = PostgresOperator(
    task_id="create_trips_table",
    dag=dag,
    postgres_conn_id="redshift",
    sql=sql_statements.CREATE_TRIPS_TABLE_SQL
)

copy_trips_task = S3ToRedshiftOperator(
    task_id="load_trips_from_s3_to_redshift",
    dag=dag,
    table="trips",
    redshift_conn_id="redshift",
    aws_credentials_id="aws_credentials",
    s3_bucket="udac-data-pipelines",
    s3_key="divvy/partitioned/{execution_date.year}/{execution_date.month}/divvy_trips.csv"
)

#
# TODO: Replace this data quality check with the HasRowsOperator
#
check_trips = HasRowsOperator(
    task_id="check_trips_data",
    dag=dag,
    table="trips",
    redshift_conn_id="redshift"
)
"""
check_trips = PythonOperator(
    task_id='check_trips_data',
    dag=dag,
    python_callable=check_greater_than_zero,
    provide_context=True,
    params={
        'table': 'trips',
    }
)
"""
create_stations_table = PostgresOperator(
    task_id="create_stations_table",
    dag=dag,
    postgres_conn_id="redshift",
    sql=sql_statements.CREATE_STATIONS_TABLE_SQL
)

copy_stations_task = S3ToRedshiftOperator(
    task_id="load_stations_from_s3_to_redshift",
    dag=dag,
    redshift_conn_id="redshift",
    aws_credentials_id="aws_credentials",
    s3_bucket="udac-data-pipelines",
    s3_key="divvy/unpartitioned/divvy_stations_2017.csv",
    table="stations"
)

#
# TODO: Replace this data quality check with the HasRowsOperator
#
check_stations = HasRowsOperator(
    task_id="check_stations_data",
    dag=dag,
    table="stations",
    redshift_conn_id="redshift"
)
"""
check_stations = PythonOperator(
    task_id='check_stations_data',
    dag=dag,
    python_callable=check_greater_than_zero,
    provide_context=True,
    params={
        'table': 'stations',
    }
)
"""
create_trips_table >> copy_trips_task
create_stations_table >> copy_stations_task
copy_stations_task >> check_stations
copy_trips_task >> check_trips
