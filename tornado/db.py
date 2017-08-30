from peewee import *
import settings

database = MySQLDatabase(
        settings.mysql_schema,
        host=settings.mysql_host,
        user=settings.mysql_user,
        password=settings.mysql_passwd
    )

class BaseModel(Model):
    class Meta:
        database = database

class Study(BaseModel):
    study         = PrimaryKeyField(db_column='study_pk')
    pi_name       = CharField()
    pi_email      = CharField()
    contact_name  = CharField()
    contact_email = CharField()
    title         = CharField()
    description   = TextField(null=True)
    ts            = DateTimeField()
    ref_doi       = CharField(null=True)

    class Meta:
        db_table = 'study'

class SampleSet(BaseModel):
    sample_set  = PrimaryKeyField(db_column='sample_set_pk')
    study       = ForeignKeyField(db_column='study_pk', rel_model=Study, to_field='study')
    ethnicity   = CharField(null=True)
    collection  = CharField(null=True)
    sample_size = IntegerField()

    class Meta:
        db_table = 'sample_set'

class Dataset(BaseModel):
    dataset       = PrimaryKeyField(db_column='dataset_pk')
    sample_set    = ForeignKeyField(db_column='sample_set_pk', rel_model=SampleSet, to_field='sample_set')
    short_name    = CharField()
    full_name     = CharField()
    browser_uri   = CharField(null=True)
    beacon_uri    = CharField(null=True)
    avg_seq_depth = FloatField(null=True)
    seq_type      = CharField(null=True)
    seq_tech      = CharField(null=True)
    seq_center    = CharField(null=True)
    dataset_size  = IntegerField()

    def current_version(self):
        return DatasetVersion.get(DatasetVersion.is_current==1, DatasetVersion.dataset==self)

    def has_image(self):
        try:
            DatasetLogo.get(DatasetLogo.dataset == self)
            return True
        except:
            return False

    class Meta:
        db_table = 'dataset'

class User(BaseModel):
    user        = PrimaryKeyField(db_column='user_pk')
    name        = CharField(null=True)
    email       = CharField(unique=True)
    affiliation = CharField(null=True)
    country     = CharField(null=True)

    class Meta:
        db_table = 'user'

class DatasetAccess(BaseModel):
    dataset_access   = PrimaryKeyField(db_column='dataset_access_pk')
    dataset          = ForeignKeyField(db_column='dataset_pk', rel_model=Dataset, to_field='dataset')
    user             = ForeignKeyField(db_column='user_pk', rel_model=User, to_field='user')
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
    dataset_version   = PrimaryKeyField(db_column='dataset_version_pk')
    dataset           = ForeignKeyField(db_column='dataset_pk', rel_model=Dataset, to_field='dataset')
    version           = CharField()
    is_current        = IntegerField(null=True)
    description       = TextField()
    terms             = TextField()
    var_call_ref      = CharField(null=True)
    available_from_ts = DateTimeField()
    ref_doi           = CharField(null=True)

    class Meta:
        db_table = 'dataset_version'

class DatasetFile(BaseModel):
    dataset_file    = PrimaryKeyField(db_column='dataset_file_pk')
    dataset_version = ForeignKeyField(db_column='dataset_version_pk', rel_model=DatasetVersion, to_field='dataset_version')
    name            = CharField()
    uri             = CharField()

    class Meta:
        db_table = 'dataset_file'

class DatasetLogo(BaseModel):
    dataset_logo = PrimaryKeyField(db_column='dataset_logo_pk')
    dataset      = ForeignKeyField(db_column='dataset_pk', rel_model=Dataset, to_field='dataset')
    mimetype     = CharField()
    data         = BlobField()

    class Meta:
        db_table = 'dataset_logo'

class Linkhash(BaseModel):
    linkhash        = PrimaryKeyField(db_column='linkhash_pk')
    dataset_version = ForeignKeyField(db_column='dataset_version_pk', rel_model=DatasetVersion, to_field='dataset_version')
    user            = ForeignKeyField(db_column='user_pk', rel_model=User, to_field='user')
    hash            = CharField()
    expires_ts      = DateTimeField()

    class Meta:
        db_table = 'linkhash'

class EnumField(Field):
    db_field = 'string' # The same as for CharField

    def __init__(self, values=[], *args, **kwargs):
        self.values = values
        super(EnumField, self).__init__(*args, **kwargs)

    def db_value(self, value):
        if value not in self.values:
            raise ValueError("Illegal value for '{}'".format(self.db_column))
        return value

    def python_value(self, value):
        if value not in self.values:
            raise ValueError("Illegal value for '{}'".format(self.db_column))
        return value

class UserLog(BaseModel):
    user_log = PrimaryKeyField(db_column='user_log_pk')
    user     = ForeignKeyField(db_column='user_pk', rel_model=User, to_field='user')
    dataset  = ForeignKeyField(db_column='dataset_pk', rel_model=Dataset, to_field='dataset')
    action   = EnumField(null=True, values=['consent','download','access_requested','access_granted','access_revoked','private_link'])
    ts       = DateTimeField()

    class Meta:
        db_table = 'user_log'

def get_outstanding_requests(dataset):
    return User.select(User).join(
            DatasetAccess
        ).switch(
            User
        ).join(
            UserLog,
            on=(   (UserLog.user    == User.user)
                 & (UserLog.dataset == DatasetAccess.dataset)
            )
        ).where(
            DatasetAccess.dataset    == dataset,
            DatasetAccess.has_access == 0,
            UserLog.action           == 'access_requested'
        ).annotate(
            UserLog,
            fn.Max(UserLog.ts).alias('apply_date')
        )
