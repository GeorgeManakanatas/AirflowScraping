#!/bin/bash
################
# general info #
################

# reset mongodb for development

########################
# supporting functions #
########################

reset_mongocontainer(){
  # mariadb variables
  mongoName="maria"
  mongoPassword="pass"
  mongoEnvironmentPort="27017"
  mongoContainerPort="27017"
  mongoDatabaseName="scrapedatabase"
  # stop and remove container
  sudo docker container stop $mongoName ;
  sudo docker container rm $mongoName ;
  # make new container
  sudo docker run --name $mongoName \
                  -e MYSQL_ROOT_PASSWORD=$mongoPassword \
                  -e MYSQL_DATABASE=$mariaDatabaseName \
                  -p $mongoEnvironmentPort:$mongoContainerPort \
                  -d mongo:3.6

  # wait for container to start
  sleep 10 ;
  sudo docker ps -a ;
}

#################
# main function #
#################
reset_mongocontainer
