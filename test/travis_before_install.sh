#!/bin/sh -x

docker pull mysql:5.7
docker pull ubuntu:16.04

VOLUME='mysql-data-volume'
MYSQL_PORT=3366

scripts/download_and_create_docker_db_volume.sh

docker run -v "$VOLUME:/var/lib/mysql" \
    --rm --name mysql -d -p "$MYSQL_PORT:3306" mysql:5.7
