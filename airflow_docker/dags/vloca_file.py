"""
Code that goes along with the Airflow located at:
http://airflow.readthedocs.org/en/latest/tutorial.html
"""
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta



default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2021, 8, 28),
    "email": ["airflow@airflow.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
}

dag = DAG("vloca_file", default_args=default_args, schedule_interval=timedelta(1))

# t1, t2 and t3 are examples of tasks created by instantiating operators
t1 = BashOperator(task_id="get_pages_request", bash_command="date", dag=dag)

t2 = BashOperator(task_id="vloca", bash_command="python /usr/local/airflow/dags/vloca.py", retries=1, dag=dag)

t2.set_upstream(t1)
