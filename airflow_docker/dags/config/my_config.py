import json

def config_file():
    '''
    Reads configuration file and saves in global variable
    '''
    global config_values
    # read configuration file
    with open('/usr/local/airflow/dags/config/config.json', 'r') as conf:
        config_values = json.load(conf)
    return
