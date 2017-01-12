import json

json_settings_fh = open("../secrets.json")
json_settings = json.load(json_settings_fh)

googleKey = json_settings["googleKey"]
googleSecret = json_settings["googleSecret"]
redirect_uri = json_settings["redirect_uri"]

## Generated with base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)
cookie_secret = json_settings["cookie_secret"]

# MySql settings
mysqlHost = json_settings["mysqlHost"]
mysqlSchema = json_settings["mysqlSchema"]
mysqlUser = json_settings["mysqlUser"]
mysqlPasswd = json_settings["mysqlPasswd"]

# Mongodb settings
mongoHost = json_settings["mongoHost"]
mongoPort = json_settings["mongoPort"]
mongoDb = json_settings["mongoDb"]
mongoUser = json_settings["mongoUser"]
mongoPassword = json_settings["mongoPassword"]

# ExAC server location
ExAC_server = json_settings["ExAC_server"]

# ssl certificate files
cert = json_settings["cert"]
key = json_settings["key"]

# e-mail config
MAIL_SERVER = json_settings["MAIL_SERVER"]
FROM_ADDRESS = json_settings["FROM_ADDRESS"]
REPLY_TO_ADDRESS = json_settings["REPLY_TO_ADDRESS"]
ADMIN_ADDRESS = json_settings["ADMIN_ADDRESS"]
