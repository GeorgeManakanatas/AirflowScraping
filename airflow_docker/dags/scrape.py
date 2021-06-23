from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2021, 6, 1),
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

dag = DAG("scrape", default_args=default_args, schedule_interval=timedelta(1))

# t1, t2 and t3 are examples of tasks created by instantiating operators
t1 = BashOperator(task_id="reset_postgres", bash_command="../../scripts/postgresReset.sh", dag=dag)

t2 = BashOperator(task_id="display_containers", bash_command="docker container ls -a", dag=dag)

t3 = BashOperator(task_id="create_virtualenv", bash_command="cd ../../web_scraping/ ; virtualenv scraper", retries=3, dag=dag)

t1 
t2 >> t3
