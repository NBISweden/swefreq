#!/usr/bin/env bash
set -xe

## SETUP SETTINGS
cp settings_sample.json settings.json
sed -i 's/password//' settings.json
sed -i 's/"mysqlSchema" : "swefreq"/"mysqlSchema" : "swefreq_test"/' settings.json
sed -i 's/"mysqlPort" : 3306/"mysqlPort" : 3366/' settings.json

echo "SETTINGS"
cat settings.json
echo "/SETTINGS"

echo ">>> Test 1. The SQL Patch"

git fetch origin refs/heads/master:master
git show master:sql/swefreq.sql > master-schema.sql

mysql -u swefreq -h 127.0.0.1 -P 3366 swefreq_test < master-schema.sql
mysql -u swefreq -h 127.0.0.1 -P 3366 swefreq_test < sql/patch-master-db.sql
# Empty the database
mysql -u swefreq -h 127.0.0.1 -P 3366 swefreq_test <<__END__
SET FOREIGN_KEY_CHECKS = 0;

SELECT group_concat(trigger_name) INTO @t FROM information_schema.triggers WHERE trigger_schema='swefreq_test';
SET @t = concat('DROP TRIGGER ', @t);
PREPARE stmt FROM @v;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SELECT group_concat(table_name) INTO @v FROM information_schema.views WHERE table_schema='swefreq_test';
SET @v = concat('DROP VIEW IF EXISTS ', @v);
PREPARE stmt FROM @v;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SELECT group_concat(table_name) INTO @t FROM information_schema.tables WHERE table_schema='swefreq_test';
SET @t = concat('DROP TABLE IF EXISTS ', @t);
PREPARE stmt FROM @v;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET FOREIGN_KEY_CHECKS = 1;
__END__


echo ">>> Test 2. Load the swefreq schema"
mysql -u swefreq -h 127.0.0.1 -P 3366 swefreq_test < sql/swefreq.sql
mysql -u swefreq -h 127.0.0.1 -P 3366 swefreq_test < test/data/load_dummy_data.sql


echo ">>> Test 3. Check that the backend starts"
cd backend

../test/01_daemon_starts.sh


echo ">>> Test 4. the backend API"
python route.py --develop 1>http_log.txt 2>&1 &
BACKEND_PID=$!

function exit_handler() {
    kill -9 $BACKEND_PID

    echo "THE HTTP LOG WAS:"
    cat http_log.txt
}

trap exit_handler EXIT

sleep 2 # Lets wait a little bit so the server has started
python test.py -v
