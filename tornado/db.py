from peewee import *
import secrets

database = MySQLDatabase(
        secrets.mysql_schema,
        host=secrets.mysql_host,
        user=secrets.mysql_user,
        password=secrets.mysql_passwd
    )

class BaseModel(Model):
    class Meta:
        database = database

class Dataset(BaseModel):
    dataset     = PrimaryKeyField(db_column='dataset_pk')
    name        = CharField()
    browser_uri = CharField(null=True)
    beacon_uri  = CharField(null=True)

    class Meta:
        db_table = 'dataset'

class User(BaseModel):
    user        = PrimaryKeyField(db_column='user_pk')
    name        = CharField(null=True)
    email       = CharField(unique=True)
    affiliation = CharField(null=True)
    country     = CharField(null=True)
    create_date = DateTimeField()

    class Meta:
        db_table = 'user'

class DatasetAccess(BaseModel):
    dataset_access   = PrimaryKeyField(db_column='dataset_access_pk')
    dataset          = ForeignKeyField(db_column='dataset_pk', rel_model=Dataset, to_field='dataset', related_name='access')
    user             = ForeignKeyField(db_column='user_pk', rel_model=User, to_field='user', related_name='access')
    wants_newsletter = IntegerField(null=True)
    is_admin         = IntegerField(null=True)
    has_consented    = IntegerField(null=True)
    has_access       = IntegerField(null=True)

    class Meta:
        db_table = 'dataset_access'
        indexes = (
            (('dataset_pk', 'user_pk'), True),
        )

class DatasetVersion(BaseModel):
    dataset_version = PrimaryKeyField(db_column='dataset_version_pk')
    dataset         = ForeignKeyField(db_column='dataset_pk', rel_model=Dataset, to_field='dataset', related_name='versions')
    version         = CharField()
    ts              = DateTimeField()
    is_current      = IntegerField(null=True)
    description     = TextField()
    terms           = TextField()

    class Meta:
        db_table = 'dataset_version'

class DatasetFile(BaseModel):
    dataset_file    = PrimaryKeyField(db_column='dataset_file_pk')
    dataset_version = ForeignKeyField(db_column='dataset_version_pk', rel_model=DatasetVersion, to_field='dataset_version', related_name='files')
    name            = CharField()
    uri             = CharField()

    class Meta:
        db_table = 'dataset_file'

class UserLog(BaseModel):
    user_log   = PrimaryKeyField(db_column='user_log_pk')
    user       = ForeignKeyField(db_column='user_pk', rel_model=User, to_field='user')
    dataset_pk = ForeignKeyField(db_column='dataset_pk', rel_model=Dataset, to_field='dataset')
    action     = CharField(null=True)
    ts         = DateTimeField()

    class Meta:
        db_table = 'user_log'
