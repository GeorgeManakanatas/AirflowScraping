#!/bin/bash
################
# general info #
################

# General purpose script to make working with containers easyer.

########################
# supporting functions #
########################

# notification function
notification(){
  # will display a notification with given text
  zenity --notification --window-icon="info" --text="$1" --timeout=2
}
reset_postgresql(){
  ./postgresReset.sh
}
# open a terminal
open_terminal(){
  cd ~
  gnome-terminal & disown
}
start_airflow(){
  # 
  cd ../airflow_docker
  docker-compose -f docker-compose-LocalExecutor.yml up
  cd ../scripts
}
stop_airflow(){
  # 
  cd ../airflow_docker
  docker-compose -f docker-compose-LocalExecutor.yml down
  cd ../scripts
}
start_container(){
 # popup for user to give the name of the container to be started and starts it
 container=$(zenity --entry --title="Start Container" --text="Container to start" );
 sudo docker container start $container
}
stop_container(){
  # popup for user to give the name of the container to be stoped and stops it
  container=$(zenity --entry --title="Stop Container" --text="Container to stop" );
  sudo docker container stop $container
}
remove_container(){
  # popup for the user to give the name of the container to be removed
  container=$(zenity --entry --title="Remove Container" --text="Container to remove" );
  # and then proceeds to stop the container and remove it
  sudo docker container stop $container
  sudo docker container rm $container
}
remove_image(){
  # popup for the user to give the name of the image to be removed
  image=$(zenity --entry --title="Remove Image" --text="Image to remove" );
  # and then proceeds to remove iamge
  sudo docker image rm $image
}
build_image(){
  # 
  cd ../airflow_docker
  docker-compose -f docker-compose-LocalExecutor.yml build --no-cache
  cd ../scripts
}
export_postgresql_data(){
  container=$(zenity --entry --title="Postgres name" --text="Name of container" );
  docker exec -t $container pg_dumpall -c -U postgres > dump_$container`date +%d-%m-%Y"_"%H_%M_%S`.sql
}
import_data_to_postgresql(){
  dump=$(zenity --entry --title="Dump file" --text="Dump file name" );
  container=$(zenity --entry --title="Postgres name" --text="Name of container" );
  cat $dump | docker exec -i $container psql -U postgres
}

###################################
# containers window main function #
###################################
start_menu(){
  #zenity configuration
  title="Node project containers"
  prompt="Please pick a container to run"
  windowHeight=500
  #
  response=$(zenity --height="$windowHeight" --list --checklist \
    --title="$title" --column="" --column="Options" \
    False "Postgresql" \
    False "Show containers" \
    False "Start container" \
    False "Stop container" \
    False "Remove Container" \
    False "Start airflow" \
    False "Stop airflow" \
    False "Show Images" \
    False "Build Image" \
    False "Remove Image" --separator=':');

  # check for no selection
  if [ -z "$response" ] ; then
     echo "No selection"
     exit 1
  fi

  IFS=":" ; for word in $response ; do
     case $word in
        "Postgresql")
          reset_postgresql
          notification "PostgreSQL started" ;;
        "Stop container")
        	stop_container
        	notification "Container stoped" ;;
      	"Start container")
        	start_container
        	notification "Container started" ;;
        "Stop airflow")
        	stop_airflow
        	notification "Airflow stoped" ;;
      	"Start airflow")
        	start_airflow
        	notification "Airflow started" ;;
        "Show containers")
          sudo docker ps -a ;;
        "Remove Container" )
          remove_container
          notification "Container removed" ;;
        "Build Airflow Image" )
          build_image
          notification "Image built" ;;
        "Show Images")
          sudo docker images ;;
        "Remove Image")
        	remove_image
          notification "Image removed" ;;
     esac
  done
}

# loop ensuring that main window function restarts once task is finished
while true; do
  start_menu
done
