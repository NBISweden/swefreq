import os
import sys
import json
import logging

ARG = "--settings_file"
SETTINGS_FILE = "settings.json"
if ARG in sys.argv:
    try:
        SETTINGS_FILE = sys.argv[sys.argv.index(ARG)+1]
    except IndexError:
        logging.error("No argument for --settings_file")
        sys.exit(1)

try:
    current_dir = os.path.dirname(os.path.realpath(__file__))
    json_settings_fh = open(os.path.join(current_dir, SETTINGS_FILE))
except FileNotFoundError:
    parent_dir = os.path.join(current_dir, os.pardir)
    json_settings_fh = open(os.path.join(parent_dir, SETTINGS_FILE))

json_settings = json.load(json_settings_fh)
json_settings_fh.close()

elixir = json_settings["elixir"]

# Generated with base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)
cookie_secret = json_settings["cookieSecret"]

# PostgreSQL settings
psql_host = json_settings["postgresHost"]
psql_port = json_settings["postgresPort"]
psql_name = json_settings["postgresName"]
psql_user = json_settings["postgresUser"]
psql_pass = json_settings["postgresPass"]

# e-mail config
mail_server = json_settings["mailServer"]
from_address = json_settings["fromAddress"]
reply_to_address = json_settings["replyToAddress"]
