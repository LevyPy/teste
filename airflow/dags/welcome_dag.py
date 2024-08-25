from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from datetime import datetime
import requests

update_time = '28/07/2024'  # dd/mm/aaaa

def print_welcome():
    print('Welcome to Airflow!')

def print_date():
    print('Today is {}'.format(datetime.today().date()))

def last_update():
    print('Atualizado em ', update_time)

dag = DAG(
    'welcome_dag',
    default_args={'start_date': days_ago(1)},
    schedule_interval='0 23 * * *',
    catchup=False
)

print_welcome_task = PythonOperator(
    task_id='print_welcome',
    python_callable=print_welcome,
    dag=dag
)

print_date_task = PythonOperator(
    task_id='print_date',
    python_callable=print_date,
    dag=dag
)

print_last_update = PythonOperator(
    task_id='print_last_update',
    python_callable=last_update,
    dag=dag
)

dummy_operator = DummyOperator(
    task_id='dummy_task',
    retries=3
)

# Set the dependencies between the tasks

print_welcome_task >> [print_date_task >> print_last_update] >> dummy_operator
