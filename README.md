SweFreq - Swedish Frequency database
====================================
[![Travis Status][travis-badge]][travis-link]
[![Coverage Status][coveralls-badge]][coveralls-link]


Running on a production system
------------------------------

The application is targeted at python 3.6. It will most likely work with later versions as well.

`venv` is not a requirement but it will help you to install the application.

1. Download the repository from [github](https://github.com/NBISweden/swefreq)

2. Make sure you have registered an Elixir AAI application with the Elixir.

3. Rename the file `settings_sample.json` into `settings.json` and edit all
   the values.

4. If you have `venv` and `pip` available you can do the following
   to install the required Python packages:

   ```
   python -m venv venv-folder
   source /path/to/venv-folder/bin/activate             # activate your virtual environment
   pip install -r /path/to/requrements.txt  # install the required Python packages
   ```

   * backend: `backend/requirements.txt`
   * importer: `scripts/importer/requirements.txt`
   * documentation: `docs/requirements.txt`


5. Create the PostgreSQL database and its tables with the following command:

   ```
   psql -U postgres -h 127.0.0.1 -f sql/data_schema.sql
   psql -U postgres -h 127.0.0.1 -f sql/user_schema.sql
   ```

   To experience the full site you need to manually add a dataset and a user to the database.
   You can use the test data in `test/data/browser_test_data.sql` as reference.

6. Add reference data and variants using the import scripts found in `scripts/`, e.g.:

   ```
   ./manage.sh import --add_reference \
                      --gencode_version 19 \
                      --ensembl_version homo_sapiens_core_75_37 \
                      --assembly_id GRCh37p13 \
                      --dbnsfp_version 2.9.3 \
                      --ref_name GRCh37p13

   ./manage.sh import --add_raw_data \
                      --dataset variant_data \
                      --version 20190415 \
                      --variant_file variants/chr22.vcf.gz \
                      --coverage_file coverage/chr22.coverage.txt.gz
   ```

### Start the server

```
    source /path/to/bin/activate                   # activate your virtual environment
    python /path/to/route.py
```

Quick development mode
----------------------

1. Install docker (and docker-compose in case it's not included in the installation) 
2. Run the server:
```bash
docker-compose up
```
3. Add test data to db:
```bash
psql -h localhost -U postgres swefreq -f test/data/browser_test_data.sql
```

[travis-badge]: https://travis-ci.org/NBISweden/swefreq.svg?branch=develop
[travis-link]: https://travis-ci.org/NBISweden/swefreq
[coveralls-badge]: https://coveralls.io/repos/github/NBISweden/swefreq/badge.svg?branch=develop
[coveralls-link]: https://coveralls.io/github/NBISweden/swefreq?branch=develop
