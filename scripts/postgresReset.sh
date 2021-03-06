#!/bin/bash
################
# general info #
################

# reset postgres for development

########################
# supporting functions #
########################

reset_postgresql(){
  # postgresql variables
  postgresContainerName="scraperpostgresql"
  postgresName="autoscrapedb"
  postgresUserName="postgres"
  postgresPassword="scrapedbpass"
  postgresEnvironmentPort="5454"
  postgresContainerPort="5432"
  # stop remove and make new container
  sudo docker container stop $postgresContainerName ;
  sudo docker container rm $postgresContainerName ;

  sudo docker run --name $postgresContainerName \
                  -e POSTGRESQL_USER=$postgresUserName \
                  -e POSTGRESQL_PASSWORD=$postgresPassword \
                  -e POSTGRESQL_DATABASE=$postgresName \
                  -p $postgresEnvironmentPort:$postgresContainerPort \
                  --restart=always \
                  -d centos/postgresql-96-centos7 ;
  # wait for container to start
  sleep 10 ;
  sudo docker ps -a ;
  docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' scraperpostgresql;
  ifconfig ;
}

#################
# main function #
#################
reset_postgresql