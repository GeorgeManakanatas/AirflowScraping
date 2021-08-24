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
reset_maria(){
  ./mariaReset.sh
}
reset_mongo(){
  ./mongoReset.sh
}
reset_postgresql(){
  ./postgresReset.sh
}
# open a terminal
open_terminal(){
  cd ~
  gnome-terminal & disown
}
start_container(){
 # popup for user to give the name of the container to be started and starts it
 container=$(zenity --entry --title="Start Container" --text="Container to start" );
 sudo docker container start $container
}
# stop container
# presents popup for user to give the name of the container to be stoped and stops it
stop_container(){
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
     False "MongoDB" \
     False "MariaDB" \
     False "Show containers" \
     False "Start container" \
     False "Stop container" \
     False "Remove Container" \
     False "Show Images" \
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
        "MongoDB")
          reset_mongo
          notification "MongoDB started" ;;
        "MariaDB")
          reset_maria
          notification "MariaDB started" ;;
        "Stop container")
        	stop_container
        	notification "Container stoped" ;;
      	"Start container")
        	start_container
        	notification "Container started" ;;
        "Show containers")
          sudo docker ps -a ;;
        "Remove Container" )
          remove_container
          notification "Container removed" ;;
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
