import json

try:
    json_settings_fh = open("settings.json")
except FileNotFoundError:
    json_settings_fh = open("../settings.json")

json_settings = json.load(json_settings_fh)
json_settings_fh.close()

# Mongodb settings
mongo_host      = json_settings["mongoHost"]
mongo_port      = json_settings["mongoPort"]
mongo_user      = json_settings["mongoUser"]
mongo_password  = json_settings["mongoPassword"]
mongo_databases = json_settings["mongoDatabases"]
