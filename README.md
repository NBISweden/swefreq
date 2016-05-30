SweFreq - Swedish Frequency database
====================================

Installation
------------

The application has only been tested with python 2.7.10. It will most likely work with at least other 2.7 versions.

`virtualenv` is not a requirement but it will help you to install the application.

1. Download the repository from [github](https://github.com/NBISweden/swefreq)
2. Create a file named `secrets.py` and place it in the same directory as `route.py`
3. MySql. Only tested with 5.6, but should work with version 4 and above

The file `secrets.py` should define the following python variables:

	# Google app-keys
	googleKey = 
	googleSecret = 

	# URI that google will redirect login to
	redirect_uri = 

	# MySql settings
	mysqlHost = 
	mysqlSchema = 
	mysqlUser = 
	mysqlPasswd = 
	
	# Mongodb settings
	mongodbhost = 
	monogdbport = 
	
	# URL to the ExAC server
	ExAC_server = 
	
	# port to bind application
	appPort =
	
	# ssl certificate files
	cert = 
	key = 



If you have `virtualenv` and `pip` installed then you can do the following to install the required python packages. Locate the `requirements.txt` file in the `swefreq` repository.


	source /path/to/bin/activate             # activate your virtualenv
	pip install -r /path/to/requrements.txt  # install the required python packages



Create the MySql database, user and tables with the following command:

	cd /path/to/the/directory/containing/swefreq.sql
	mysql -u root -p < swefreq.sql

You need to create an administrative user by inserting one row into the `swefreq.users` table. Start an interactive sql-shell with: `mysql -u swefreq -p` and then do:

	use swefreq
	insert into users (username, email, swefreq_admin, affiliation, full_user)
	values (
	'YourUsername',       -- Replace YourUsername with your own
	'YourGmailAddress',   -- Replace YourGmailAddress with your own
	'YES',
	'YourAffiliation',    -- Replace YourAffiliation with your own
	'YES');

To start the server:

	source /path/to/bin/activate                   # activate your virtualenv
	python /path/to/route.py