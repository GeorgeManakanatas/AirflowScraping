#!/bin/bash
################
# general info #
################

# reset mariadb for development

########################
# supporting functions #
########################

reset_mariacontainer(){
  # mariadb variables
  mariaName="maria"
  mariaPassword="pass"
  mariaEnvironmentPort="3306"
  mariaContainerPort="3306"
  mariaDatabaseName="scrapedatabase"
  # stop and remove container
  sudo docker container stop $mariaName ;
  sudo docker container rm $mariaName ;
  # make new container
  sudo docker run --name $mariaName \
                  -e MYSQL_ROOT_PASSWORD=$mariaPassword \
                  -e MYSQL_DATABASE=$mariaDatabaseName \
                  -p $mariaEnvironmentPort:$mariaContainerPort \
                  -d mariadb:10.3.10-bionic

  # wait for container to start
  sleep 10 ;
  sudo docker ps -a ;
}

#################
# main function #
#################
reset_mariacontainer
