#!/usr/bin/env bash

docker pull mysql:5.7
docker run --name mysql -e MYSQL_ALLOW_EMPTY_PASSWORD=1 -d -p 3366:3306  mysql:5.7
