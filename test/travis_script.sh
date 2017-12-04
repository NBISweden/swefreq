#!/usr/bin/env bash

cp settings_sample.json settings.json

cd backend
bash ../test/01_daemon_starts.sh
cd ..

mysql -u root -h 127.0.0.1 -P 3366 -e 'CREATE DATABASE swefreq;'
mysql -u root -h 127.0.0.1 -P 3366 swefreq < sql/swefreq.sql
