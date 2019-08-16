#!/bin/sh -ex

DBNAME=swefreq

## SETUP SETTINGS
echo '>>> Preparing for testing: Fix settings.json file'
cp settings_sample.json settings.json

sed -i.tmp 's/"postgresHost" : "postgres host"/"postgresHost" : "127.0.0.1"/' settings.json
sed -i.tmp 's/"postgresPort" : 5432/"postgresPort" : 5433/' settings.json
sed -i.tmp "s/\"postgresName\" : \"swefreq\"/\"postgresName\" : \"$DBNAME\"/" settings.json

echo 'SETTINGS'
cat settings.json
echo '/SETTINGS'


echo '>>> Test 1: The SQL Patch'

LATEST_RELEASE=$(git tag | grep '^v' | sort -V | tail -n 1)
git show "$LATEST_RELEASE:sql/*_schema.sql" > master-schema.sql

psql -U postgres -h 127.0.0.1 -p 5433 -f master-schema.sql "$DBNAME"
psql -U postgres -h 127.0.0.1 -p 5433 -f sql/patch-master-db.sql "$DBNAME"

# Empty the database
psql -U postgres -h 127.0.0.1 -p 5433 "$DBNAME" <<__END__
DROP SCHEMA data CASCADE;
DROP SCHEMA users CASCADE;
__END__


echo '>>> Test 2: Load the swefreq schema'
psql -U postgres -h 127.0.0.1 -p 5433 -f sql/data_schema.sql "$DBNAME"
psql -U postgres -h 127.0.0.1 -p 5433 -f sql/user_schema.sql "$DBNAME"
psql -U postgres -h 127.0.0.1 -p 5433 -f sql/beacon_schema.sql "$DBNAME"
psql -U postgres -h 127.0.0.1 -p 5433 -f test/data/load_dummy_data.sql "$DBNAME"
psql -U postgres -h 127.0.0.1 -p 5433 -f test/data/browser_test_data.sql "$DBNAME"


echo '>>> Test 3: Check that the backend starts'

(cd backend && ../test/01_daemon_starts.sh)


echo '>>> Test 4: The backend'
COVERAGE_FILE=.coverage_server coverage run backend/route.py --port=4000 --develop 1>http_log.txt 2>&1 &
BACKEND_PID=$!

sleep 2 # Lets wait a little bit so the server has started

exit_handler () {
    rv=$?
    # Ignore errors in the exit handler
    set +e
    # We want to make sure the background process has stopped, otherwise the
    # travis test will stall for a long time.
    kill -9 "$BACKEND_PID"

    echo 'THE HTTP LOG WAS:'
    cat http_log.txt

    exit "$rv"
}

trap exit_handler EXIT


echo '>>> Test 4A: The backend API'
RETURN_VALUE=0
python backend/test.py -v
RETURN_VALUE=$((RETURN_VALUE + $?))


echo '>>> Test 4B: The browser backend'
# test browser
COVERAGE_FILE=.coverage_pytest PYTHONPATH=$PYTHONPATH:backend/ py.test backend/ --cov=backend/
RETURN_VALUE=$((RETURN_VALUE + $?))

# Quit the app
curl localhost:4000/developer/quit
sleep 2 # Lets wait a little bit so the server has stopped


echo '>>> Prepare for test 5'
psql -U postgres -h 127.0.0.1 -p 5433 "$DBNAME" <<__END__
DROP SCHEMA data CASCADE;
DROP SCHEMA users CASCADE;
__END__

psql -U postgres -h 127.0.0.1 -p 5433 -f sql/data_schema.sql "$DBNAME"
psql -U postgres -h 127.0.0.1 -p 5433 -f sql/user_schema.sql "$DBNAME"

BASE=scripts/importer
ln -s tests/data "$BASE/downloaded_files"
gzip -c "$BASE/downloaded_files/dbNSFP_gene.txt" > "$BASE/downloaded_files/dbNSFP2.9_gene.gz"
gzip -c "$BASE/downloaded_files/gencode.gtf" > "$BASE/downloaded_files/gencode.v19.annotation.gtf.gz"
gzip "$BASE/tests/data/dataset1_1.vcf"
gzip "$BASE/tests/data/dataset1_1_coverage.txt"
gzip "$BASE/tests/data/dataset1_2.vcf"
gzip "$BASE/tests/data/dataset1_2_coverage.txt"
gzip "$BASE/tests/data/dataset2_1.vcf"

echo '>>> Test 5. Importing data'

sed -i -e 's/\"\$SCRIPT_DIR\/importer/COVERAGE_FILE=.coverage_import_1 coverage run \"\$SCRIPT_DIR\/importer/g' scripts/manage.sh
# read reference data
scripts/manage.sh import --add_reference\
                  --gencode_version 19\
                  --ensembl_version homo_sapiens_core_75_37\
		  --assembly_id GRCh37p13\
                  --dbnsfp_version 2.9.3\
		  --batch_size 2\
                  --ref_name GRCh37p13

# read dataset names, versions etc
psql -U postgres -h 127.0.0.1 -p 5433 -f "$BASE/tests/data/base_info.sql" "$DBNAME"


# read variant data
sed -i -e 's/import_1/import_2/' scripts/manage.sh
scripts/manage.sh import --add_raw_data \
                   --dataset  "Dataset 1"\
                   --version "Version 1"\
                   --variant_file "$BASE/tests/data/dataset1_1.vcf.gz"\
                   --count_calls \
		   --coverage_file "$BASE/tests/data/dataset1_1_coverage.txt.gz"

sed -i -e 's/import_2/import_3/' scripts/manage.sh
scripts/manage.sh import --add_raw_data \
                   --dataset  "Dataset 1"\
                   --version "Version 2"\
                   --variant_file "$BASE/tests/data/dataset1_2.vcf.gz"\
		   --batch_size 2\
		   --coverage_file "$BASE/tests/data/dataset1_2_coverage.txt.gz"

sed -i -e 's/import_3/import_4/' scripts/manage.sh
scripts/manage.sh import --add_raw_data \
                   --dataset  "Dataset 2"\
                   --version "Version 1"\
                   --count_calls \
                   --variant_file "$BASE/tests/data/dataset2_1.vcf.gz"\
		   --beacon-only

# make pg_dump
# compare file to reference; must remove comments, empty rows and id column
pg_dump -U postgres -h 127.0.0.1 -p 5433 "$DBNAME" -f dbdump.psql --data-only
sed -i -r -e '/^--/d;/^$/d;s/^[0-9]+[^I]//' dbdump.psql
grep -v -P "^SE[TL]" dbdump.psql | sort > sdump.psql
sed -i -r -e 's/^[0-9]+[^I]//' "$BASE/tests/data/reference.psql"
sort "$BASE/tests/data/reference.psql" > ref.psql

# compare dump to reference
diff sdump.psql ref.psql
RETURN_VALUE=$((RETURN_VALUE + $?))

echo '>>> Test 6. Reading manta file'

sed -i -e 's/import_4/mate_1/' scripts/manage.sh
./scripts/manage.sh import --add_raw_data \
                   --dataset "Dataset 1" \
                   --version "Version 1" \
                   --add_mates \
                   --add_reversed_mates \
                   --variant_file "$BASE/tests/data/manta.vcf"

psql -U postgres -h 127.0.0.1 -p 5433 "$DBNAME" -c "select chrom_id, pos, ref, alt, chrom, mate_chrom, mate_start, mate_id, allele_freq, variant_id, allele_count, allele_num from data.mates ;" > mates_res.txt
diff mates_res.txt "$BASE/tests/data/mates_reference.txt"
RETURN_VALUE=$((RETURN_VALUE + $?))

echo '>>> Code evaluation'
pylint backend
RETURN_VALUE=$((RETURN_VALUE + $?))
pylint scripts
RETURN_VALUE=$((RETURN_VALUE + $?))

echo '>>> Finalising: Combine coverage'

coverage combine .coverage_pytest .coverage_server .coverage_import_1 .coverage_import_2 .coverage_import_3 .coverage_import_4 .coverage_mate_1

if [ -f .coverage ]; then
    coveralls
    coverage report
fi

exit "$RETURN_VALUE"
