
@echo off

SET container_port=8080
SET host_port=8080
SET local_volume_folder_path=C:\Users\manakang\Videos\Repos\custom_airflow\dags
SET container_name=myAirflow

IF %1 EQU help (
    ECHO "Only pull and action are proper arguments"
) ELSE (
    IF %1 EQU pull  (
        ECHO "Pulling airflow container"
        docker pull puckel/docker-airflow
    )
    IF %1 EQU run (
        ECHO "Running airflow container"
        docker run -d --name %container_name% -p %host_port%:%container_port% puckel/docker-airflow webserver
    )
    IF %1 EQU run_with_volume (
        ECHO "Running Airflow container with volume"
        docker run -d --name %container_name% -p %host_port%:%container_port% -v %local_volume_folder_path%:/usr/local/airflow/dags  puckel/docker-airflow webserver
    )
    IF %1 EQU remove (
        ECHO "Removing airflow container"
        docker container stop %container_name%
        docker container rm %container_name%
    )
    IF %1 EQU start (
        ECHO "Starting Airflow container"
        docker container start %container_name%
    )
    IF %1 EQU stop (
        ECHO "Stopping Airflow container"
        docker container stop %container_name%
    )
    IF %1 EQU containers (
        ECHO "Showing all containers"
        docker container ls -a
    )
    IF %1 EQU images (
        ECHO "Showing all images"
        docker image ls -a
    )
    IF %1 EQU enter (
        ECHO "Entering Airflow container"
        docker exec -ti %container_name% bash
    )
)



