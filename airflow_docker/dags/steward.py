from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator, PythonVirtualenvOperator
from datetime import datetime, timedelta
import json
import csv


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2021, 4, 26),
    "email": ["steward@gailm.com"],
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
def read_config(**kwargs):
    """Read configuration and setup files"""
    # not reading from file at the moment
    print()

def callable_virtualenv(**kwargs):
        """
        Example function that will be performed in a virtual environment.
        Importing at the module level ensures that it will not attempt to import the
        library before it is installed.
        """
        import requests
        import random
        from time import sleep

        pages = {
            "MeestVerwezenPaginas":"https://vloca-kennishub.vlaanderen.be/vloca-kennishub/Speciaal:MeestVerwezenPaginas",
            "Categorieen":"https://vloca-kennishub.vlaanderen.be/vloca-kennishub/Speciaal:Categorie%C3%ABn",
            "Weespaginas":"https://vloca-kennishub.vlaanderen.be/vloca-kennishub/Speciaal:Weespaginas",
            "KortePaginas":"https://vloca-kennishub.vlaanderen.be/vloca-kennishub/Speciaal:KortePaginas",
            "RecenteWijzigingen":"https://vloca-kennishub.vlaanderen.be/vloca-kennishub/Speciaal:RecenteWijzigingen?limit=500&days=1&enhanced=1&urlversion=2"
        }
        # scraping

        page = requests.get(pages["KortePaginas"], verify=False)
        print(page.content)
        time.sleep(random.randint(1,3))
        page = requests.get(pages["Categorieen"], verify=False)
        print(page.content)
        time.sleep(random.randint(1,3))
        page = requests.get(pages["Weespaginas"], verify=False)
        print(page.content)
        time.sleep(random.randint(1,3))
        page = requests.get(pages["MeestVerwezenPaginas"], verify=False)
        print(page.content)
        time.sleep(random.randint(1,3))
        page = requests.get(pages["RecenteWijzigingen"], verify=False)
        print(page.content)



def send_email_to_all(**kwargs):
    """Send information to stweards"""
    # emailer function
    print('send_email_to_all')

def proscess_information(**kwargs):
    """Proscess the information"""
    # 
    print('proscess_information')

def store_information_to_db(**kwargs):
    """Store the information"""
    # 
    print('store_information_to_db')


# t1, t2 and t3 are examples of tasks created by instantiating operators
t1 = PythonOperator(
    task_id="read_configuration",
    python_callable=read_config,
    dag=dag,
)

t2 = PythonVirtualenvOperator(
    task_id="get_info", 
    python_callable=callable_virtualenv, 
    dag=dag,
)

t3 = PythonOperator(
    task_id="proscess_info", 
    python_callable=proscess_information,
    requirements=['time','random'],
    dag=dag,
)


t4 = PythonOperator(
    task_id="store_stats",
    python_callable=store_information_to_db,
    dag=dag,
)

t5 = PythonOperator(
    task_id="send_emails",
    python_callable=send_email_to_all,
    dag=dag,
)

t1
t2.set_upstream(t1)
t3.set_upstream(t2)
t4.set_upstream(t3)
t5.set_upstream(t3)
