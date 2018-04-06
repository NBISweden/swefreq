#!/bin/bash

docker run -v mysql-data-volume:/var/lib/mysql --rm --name mysql -d mysql:5.7

docker run -i --rm --link mysql:mysql mysql:5.7 mysql -h mysql -u swefreq swefreq_test < sql/swefreq.sql
docker run -i --rm --link mysql:mysql mysql:5.7 mysql -h mysql -u swefreq swefreq_test < test/data/load_dummy_data.sql

docker container stop mysql
