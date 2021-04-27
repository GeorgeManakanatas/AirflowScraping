from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import json
import csv


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2021, 4, 1),
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

dag = DAG("steward", default_args=default_args, schedule_interval=timedelta(1))

# functions 
def read_config(ds, **kwargs):
    """Read configuration and setup files"""
    # not reading from file at the moment

    return

def get_page(ds, **kwargs):
    """get the information from the knowledge hub"""
    # scraping
    pages = {
        "MeestVerwezenPaginas":"https://vloca-kennishub.vlaanderen.be/vloca-kennishub/Speciaal:MeestVerwezenPaginas",
        "Categorieen":"https://vloca-kennishub.vlaanderen.be/vloca-kennishub/Speciaal:Categorie%C3%ABn",
        "Weespaginas":"https://vloca-kennishub.vlaanderen.be/vloca-kennishub/Speciaal:Weespaginas",
        "KortePaginas":"https://vloca-kennishub.vlaanderen.be/vloca-kennishub/Speciaal:KortePaginas",
        "RecenteWijzigingen":"https://vloca-kennishub.vlaanderen.be/vloca-kennishub/Speciaal:RecenteWijzigingen?limit=500&days=1&enhanced=1&urlversion=2"
    }

    page = requests.get(pages.KortePaginas, verify=False)

    print(short_pages)

    return

def send_email_to_all(ds, **kwargs):
    """Send information to stweards"""
    # emailer function
    return 

def proscess_information(ds, **kwargs):
    """Proscess the information"""
    # 
    return 'information'

# t1, t2 and t3 are examples of tasks created by instantiating operators
t1 = PythonOperator(
    task_id="read_configuration",
    python_callable=read_config,
    dag=dag,
)

t2 = PythonOperator(
    task_id="get_info", 
    python_callable=get_page, 
    dag=dag,
)

t3 = PythonOperator(
    task_id="proscess_info", 
    python_callable=proscess_information, 
    dag=dag,
)


t4 = PythonOperator(
    task_id="store_stats",
    python_callable=get_page,
    dag=dag,
)

t5 = PythonOperator(
    task_id="send_emails",
    python_callable=send_email_to_all,
    dag=dag,
)

t2.set_upstream(t1)
t3.set_upstream(t2)
t4.set_upstream(t3)
t5.set_upstream(t3)
