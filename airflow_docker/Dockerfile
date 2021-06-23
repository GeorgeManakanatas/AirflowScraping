FROM puckel/docker-airflow:latest

RUN pip install virtualenv
COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt