#!/bin/bash

########################
# supporting functions #
########################

notification(){
  # will display a notification with given text
  zenity --notification --window-icon="info" --text="$1" --timeout=2
}
pull_airflow_image(){
    # rabbitmq variables
    image_name="puckel/docker-airflow"
    #
    sudo docker pull $image_name
}
remove_airflow_image(){
    image=$(zenity --entry --title="Remove Image" --text="Image to remove?" );
    sudo docker image rm $image
}
show_images(){
    sudo docker image ls -a
}
show_containers(){
    sudo docker container ls -a
}
run_airflow_container(){
    #
    host_port="8080"
    container_port="8080"
    container_name="myAirflow"
    #
    sudo docker run -d --name $container_name -p $host_port:$container_port puckel/docker-airflow webserver
}
run_airflow_container_with_volume(){
    #
    host_port="8080"
    container_port="8080"
    local_volume_folder_path="/home/georgemanakanatas/Documents/projects/custom_airflow/dags"
    container_name="myAirflow"
    #
    # sudo docker run -d --name $container_name -p $host_port:$container_port -v $local_volume_folder_path:/usr/local/airflow/dags logal:airflow webserver
    # sudo docker run -d --name $container_name -p $host_port:$container_port -v $local_volume_folder_path:/usr/local/airflow/dags apache/airflow webserver
    # with local executor
    sudo docker-compose -f docker_compose_LocalExecutor.yml up -d
}
start_airflow_container(){
    #
    container_name=$(zenity --entry --title="Start Container" --text="Container to start?" );
    #
    sudo docker container start $container_name
}
stop_airflow_container(){
    #
    container_name=$(zenity --entry --title="Stop Container" --text="Container to stop?" );

    #
    sudo docker container stop $container_name
}
remove_airflow_container(){
    #
    container_name=$(zenity --entry --title="Remove Container" --text="Container to remove?" );
    #
    sudo docker container stop $container_name
    sudo docker container rm $container_name
}
enter_container(){
    #
    container_name=$(zenity --entry --title="Target Container" --text="Container to enter?" );
    sudo docker exec -ti $container_name bash
}
#################
# main function #
#################
start_menu(){
  #zenity configuration
  title="Airflow GUI"
  prompt="Please pick action to perform"
  windowHeight=500
  windowWidth=300
  #
  response=$(zenity --height="$windowHeight" --width="$windowWidth" --list --checklist \
    --title="$title" --column="" --column="Options" \
    False "Show images" \
    False "Pull Airflow image" \
    False "Remove Airflow image" \
    False "Show containers" \
    False "Run Airflow container" \
    False "Run Airflow container with volume" \
    False "Start Airflow container" \
    False "Stop Airflow container" \
    False "Remove Airflow container" \
    False "Enter Airflow container" \
    --separator=':');

  # check for no selection
  if [ -z "$response" ] ; then
     echo "No selection"
     exit 1
  fi

  IFS=":" ; for word in $response ; do
     case $word in
        "Show images")
            #
            show_images ;;
        "Pull Airflow image")
            #
            pull_airflow_image
            notification "Airflow image pulled" ;;
        "Remove Airflow image")
            #
            show_images
            remove_airflow_image
            notification "Airflow image removed" ;;
        "Show containers")
            #
            show_containers ;;
        "Run Airflow container")
            #
            run_airflow_container
            notification "Airflow container running" ;;
        "Run Airflow container with volume")
            #
            run_airflow_container_with_volume
            notification "Airflow container running with volume" ;;
        "Start Airflow container")
            #
            show_containers
            start_airflow_container
            notification "Airflow container started" ;;
        "Stop Airflow container")
            #
            show_containers
            stop_airflow_container
            notification "Airflow container stoped" ;;
        "Remove Airflow container")
            #
            show_containers
            remove_airflow_container
            notification "Airflow container removed" ;;
        "Enter Airflow container")
            #
            show_containers
            enter_container ;;
     esac
  done
}


# loop ensuring that main window function restarts once task is finished
while true; do
  start_menu
done
