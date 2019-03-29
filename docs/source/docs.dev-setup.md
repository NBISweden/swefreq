Set up a development system
===========================

In order to set up a minimal database system for development:

#. Install docker (and docker-compose in case it's not included in the installation)
#. Start the server and database: `$ docker-compose up`
#. Add test data: `$ psql -h localhost -U postgres swefreq -f test/data/browser_test_data.sql`

The test data contains all data required for the browser tests.
