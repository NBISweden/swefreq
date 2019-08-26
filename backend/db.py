#!/usr/bin/env python3

import logging

from peewee import (BlobField,
                    BooleanField,
                    CharField,
                    DateTimeField,
                    IntegerField,
                    Field,
                    FloatField,
                    ForeignKeyField,
                    Model,
                    TextField,
                    fn)
from playhouse.postgres_ext import ArrayField, BinaryJSONField, PostgresqlExtDatabase

import settings

# pylint: disable=no-member
database = PostgresqlExtDatabase(settings.psql_name,
                                 user=settings.psql_user,
                                 password=settings.psql_pass,
                                 host=settings.psql_host,
                                 port=settings.psql_port,
                                 register_hstore=False)
# pylint: enable=no-member

class BaseModel(Model):
    class Meta:
        database = database


class EnumField(Field):
    db_field = 'string'  # The same as for CharField

    def __init__(self, choices=None, *args, **kwargs):
        self.values = choices or []
        super().__init__(*args, **kwargs)

    def db_value(self, value):
        if value not in self.values:
            raise ValueError("Illegal value for '{}'".format(self.column_name))
        return value

    def python_value(self, value):
        if value not in self.values:
            raise ValueError("Illegal value for '{}'".format(self.column_name))
        return value

###
# Reference Tables
##


class ReferenceSet(BaseModel):
    """
    The gencode, ensembl, dbNSFP and omim data are combined to fill out the
    Gene, Transcript and Feature tables. DbSNP data is separate, and may be
    shared between reference sets, so it uses a foreign key instead.
    """
    class Meta:
        table_name = 'reference_sets'
        schema = 'data'

    name = CharField(column_name="reference_name", null=True)
    ensembl_version = CharField()
    gencode_version = CharField()
    dbnsfp_version = CharField()
    reference_build = CharField(unique=True)


class Gene(BaseModel):
    class Meta:
        table_name = 'genes'
        schema = 'data'

    reference_set = ForeignKeyField(ReferenceSet, column_name="reference_set", backref="genes")
    gene_id = CharField(unique=True, max_length=15)
    name = CharField(column_name="gene_name", null=True)
    full_name = CharField(null=True)
    canonical_transcript = CharField(null=True, max_length=15)
    chrom = CharField(max_length=10)
    start = IntegerField(column_name="start_pos")
    stop = IntegerField(column_name="end_pos")
    strand = EnumField(choices=['+', '-'])


class GeneOtherNames(BaseModel):
    class Meta:
        table_name = 'gene_other_names'
        schema = 'data'

    gene = ForeignKeyField(Gene, column_name="gene", backref="other_names")
    name = CharField(null=True)


class Transcript(BaseModel):
    class Meta:
        table_name = 'transcripts'
        schema = 'data'

    transcript_id = CharField(max_length=15)
    gene = ForeignKeyField(Gene, column_name="gene", backref="transcripts")
    mim_gene_accession = IntegerField()
    mim_annotation = CharField()
    chrom = CharField(max_length=10)
    start = IntegerField(column_name="start_pos")
    stop = IntegerField(column_name="stop_pos")
    strand = EnumField(choices=['+', '-'])


class Feature(BaseModel):
    class Meta:
        table_name = 'features'
        schema = 'data'

    gene = ForeignKeyField(Gene, column_name="gene", backref='exons')
    transcript = ForeignKeyField(Transcript, column_name="transcript", backref='transcripts')
    chrom = CharField(max_length=10)
    start = IntegerField(column_name="start_pos")
    stop = IntegerField(column_name="stop_pos")
    strand = EnumField(choices=['+', '-'])
    feature_type = CharField()


###
# Study and Dataset fields
##

class Collection(BaseModel):
    """
    A collection is a source of data which can be sampled into a SampleSet.
    """
    class Meta:
        table_name = 'collections'
        schema = 'data'

    name = CharField(column_name="study_name", null=True)
    ethnicity = CharField(null=True)


class Study(BaseModel):
    """
    A study is a scientific study with a PI and a description, and may include
    one or more datasets.
    """
    class Meta:
        table_name = 'studies'
        schema = 'data'

    pi_name = CharField()
    pi_email = CharField()
    contact_name = CharField()
    contact_email = CharField()
    title = CharField()
    description = TextField(column_name="study_description", null=True)
    publication_date = DateTimeField()
    ref_doi = CharField(null=True)


class Dataset(BaseModel):
    """
    A dataset is part of a study, and usually include a certain population.

    Most studies only have a single dataset, but multiple are allowed.
    """
    class Meta:
        table_name = 'datasets'
        schema = 'data'

    study = ForeignKeyField(Study, column_name="study", backref='datasets')
    short_name = CharField()
    full_name = CharField()
    browser_uri = CharField(null=True)
    beacon_uri = CharField(null=True)
    description = TextField(column_name="beacon_description", null=True)
    avg_seq_depth = FloatField(null=True)
    seq_type = CharField(null=True)
    seq_tech = CharField(null=True)
    seq_center = CharField(null=True)
    dataset_size = IntegerField()

    def has_image(self):
        try:
            DatasetLogo.get(DatasetLogo.dataset == self)
            return True
        except DatasetLogo.DoesNotExist:
            return False


class SampleSet(BaseModel):
    class Meta:
        table_name = 'sample_sets'
        schema = 'data'

    dataset = ForeignKeyField(Dataset, column_name="dataset", backref='sample_sets')
    collection = ForeignKeyField(Collection, column_name="collection", backref='sample_sets')
    sample_size = IntegerField()
    phenotype = CharField(null=True)


class DatasetVersion(BaseModel):
    class Meta:
        table_name = 'dataset_versions'
        schema = 'data'

    dataset = ForeignKeyField(Dataset, column_name="dataset", backref='versions')
    reference_set = ForeignKeyField(ReferenceSet,
                                    column_name="reference_set",
                                    backref='dataset_versions')
    version = CharField(column_name="dataset_version")
    description = TextField(column_name="dataset_description")
    terms = TextField()
    available_from = DateTimeField()
    ref_doi = CharField(null=True)
    data_contact_name = CharField(null=True)
    data_contact_link = CharField(null=True)
    num_variants = IntegerField(null=True)
    coverage_levels = ArrayField(IntegerField, null=True)
    portal_avail = BooleanField(null=True)
    file_access = EnumField(null=False, choices=['PRIVATE', 'CONTROLLED',
                                                 'REGISTERED', 'PUBLIC'])
    beacon_access = EnumField(null=False, choices=['PRIVATE', 'CONTROLLED',
                                                   'REGISTERED', 'PUBLIC'])


class DatasetFile(BaseModel):
    class Meta:
        table_name = 'dataset_files'
        schema = 'data'

    dataset_version = ForeignKeyField(DatasetVersion,
                                      column_name="dataset_version",
                                      backref='files')
    name = CharField(column_name="basename")
    uri = CharField()
    file_size = IntegerField()


class DatasetLogo(BaseModel):
    class Meta:
        table_name = 'dataset_logos'
        schema = 'data'

    dataset = ForeignKeyField(Dataset, column_name="dataset", backref='logo')
    mimetype = CharField()
    data = BlobField(column_name="bytes")


###
# Variant and coverage data fields
##

class Variant(BaseModel):
    class Meta:
        table_name = "variants"
        schema = 'data'

    dataset_version = ForeignKeyField(DatasetVersion,
                                      column_name="dataset_version",
                                      backref="variants")
    rsid = IntegerField()
    chrom = CharField(max_length=10)
    pos = IntegerField()
    ref = CharField()
    alt = CharField()
    site_quality = FloatField()
    orig_alt_alleles = ArrayField(CharField)
    hom_count = IntegerField()
    allele_freq = FloatField()
    filter_string = CharField()
    variant_id = CharField()
    allele_count = IntegerField()
    allele_num = IntegerField()
    quality_metrics = BinaryJSONField()
    vep_annotations = BinaryJSONField()


class VariantMate(BaseModel):
    class Meta:
        table_name = "mates"
        schema = 'data'

    dataset_version = ForeignKeyField(DatasetVersion,
                                      column_name="dataset_version",
                                      backref="mates")
    chrom = CharField(max_length=10)
    pos = IntegerField()
    ref = CharField()
    alt = CharField()
    chrom_id = CharField()
    mate_chrom = CharField()
    mate_start = IntegerField()
    mate_id = CharField()
    allele_freq = FloatField()
    variant_id = CharField()
    allele_count = IntegerField()
    allele_num = IntegerField()


class VariantGenes(BaseModel):
    class Meta:
        table_name = 'variant_genes'
        schema = 'data'

    variant = ForeignKeyField(Variant, column_name="variant", backref="genes")
    gene = ForeignKeyField(Gene, column_name="gene", backref="variants")


class VariantTranscripts(BaseModel):
    class Meta:
        table_name = 'variant_transcripts'
        schema = 'data'

    variant = ForeignKeyField(Variant, column_name="variant", backref="transcripts")
    transcript = ForeignKeyField(Transcript, column_name="transcript", backref="variants")


class Coverage(BaseModel):
    """
    Coverage statistics are pre-calculated for each variant for a given
    dataset.

    The fields show the fraction of a population that reaches the
    mapping coverages given by the variable names.

    ex. cov20 = 0.994 means that 99.4% of the population had at a mapping
        coverage of at least 20 in this position.
    """
    class Meta:
        table_name = "coverage"
        schema = 'data'

    dataset_version = ForeignKeyField(DatasetVersion, column_name="dataset_version")
    chrom = CharField(max_length=10)
    pos = IntegerField()
    mean = FloatField()
    median = FloatField()
    coverage = ArrayField(FloatField, null=True)


class Metrics(BaseModel):
    class Meta:
        table_name = "metrics"
        schema = 'data'

    dataset_version = ForeignKeyField(DatasetVersion, column_name="dataset_version")
    metric = CharField()
    mids = ArrayField(IntegerField)
    hist = ArrayField(IntegerField)


class User(BaseModel):
    class Meta:
        table_name = "users"
        schema = 'users'

    name = CharField(column_name="username", null=True)
    email = CharField(unique=True)
    identity = CharField(unique=True)
    identity_type = EnumField(null=False, choices=['google', 'elixir'], default='elixir')
    affiliation = CharField(null=True)
    country = CharField(null=True)

    def is_admin(self, dataset):
        return (DatasetAccess.select()
                .where(DatasetAccess.dataset == dataset,
                       DatasetAccess.user == self,
                       DatasetAccess.is_admin)
                .count())

    def has_access(self, dataset, ds_version=None):
        """
        Check whether user has permission to access a dataset.

        Args:
            dataset (Database): peewee Database object
            ds_version (str): the dataset version

        Returns:
            bool: allowed to access

        """
        dsv = get_dataset_version(dataset.short_name, ds_version)
        if not dsv:
            return False
        if dsv.file_access in ('REGISTERED', 'PUBLIC'):
            return True
        if dsv.file_access == 'PRIVATE':
            return False

        return (DatasetAccessCurrent.select()
                .where(DatasetAccessCurrent.dataset == dataset,
                       DatasetAccessCurrent.user == self)
                .count()) > 0

    def has_requested_access(self, dataset):
        return (DatasetAccessPending.select()
                .where(DatasetAccessPending.dataset == dataset,
                       DatasetAccessPending.user == self)
                .count())


class SFTPUser(BaseModel):
    class Meta:
        table_name = "sftp_users"
        schema = 'users'

    user = ForeignKeyField(User, backref='sftp_user')
    user_uid = IntegerField(unique=True)
    user_name = CharField(null=False)
    password_hash = CharField(null=False)
    account_expires = DateTimeField(null=False)


class UserAccessLog(BaseModel):
    class Meta:
        table_name = "user_access_log"
        schema = 'users'

    user = ForeignKeyField(User, backref='access_logs')
    dataset = ForeignKeyField(Dataset, column_name='dataset', backref='access_logs')
    action = EnumField(null=True, choices=['access_granted', 'access_revoked',
                                           'access_requested', 'private_link'])
    ts = DateTimeField()


class UserConsentLog(BaseModel):
    class Meta:
        table_name = "user_consent_log"
        schema = 'users'

    user = ForeignKeyField(User, backref='consent_logs')
    dataset_version = ForeignKeyField(DatasetVersion,
                                      column_name='dataset_version',
                                      backref='consent_logs')
    ts = DateTimeField()


class UserDownloadLog(BaseModel):
    class Meta:
        table_name = "user_download_log"
        schema = 'users'

    user = ForeignKeyField(User, backref='download_logs')
    dataset_file = ForeignKeyField(DatasetFile,
                                   column_name='dataset_file',
                                   backref='download_logs')
    ts = DateTimeField()


class DatasetAccess(BaseModel):
    class Meta:
        table_name = "dataset_access"
        schema = 'users'

    dataset = ForeignKeyField(Dataset, column_name='dataset', backref='access')
    user = ForeignKeyField(User, backref='dataset_access')
    wants_newsletter = BooleanField(null=True)
    is_admin = BooleanField(null=True)


class Linkhash(BaseModel):
    class Meta:
        table_name = "linkhash"
        schema = 'users'

    dataset_version = ForeignKeyField(DatasetVersion,
                                      column_name='dataset_version',
                                      backref='link_hashes')
    user = ForeignKeyField(User, backref='link_hashes')
    hash = CharField()
    expires_on = DateTimeField()


class BeaconCounts(BaseModel):
    class Meta:
        table_name = "beacon_dataset_counts_table"
        schema = 'beacon'

    datasetid = CharField(primary_key=True)
    callcount = IntegerField()
    variantcount = IntegerField()


#####
# Views
##

class DatasetVersionCurrent(DatasetVersion):
    class Meta:
        table_name = 'dataset_version_current'
        schema = 'data'

    dataset = ForeignKeyField(Dataset, column_name="dataset", backref='current_version')
    reference_set = ForeignKeyField(ReferenceSet,
                                    column_name="reference_set",
                                    backref='current_version')


class DatasetAccessCurrent(DatasetAccess):
    class Meta:
        table_name = 'dataset_access_current'
        schema = 'users'

    dataset = ForeignKeyField(Dataset, column_name='dataset', backref='access_current')
    user = ForeignKeyField(User, backref='access_current')
    has_access = IntegerField()
    access_requested = DateTimeField()


class DatasetAccessPending(DatasetAccess):
    class Meta:
        table_name = 'dataset_access_pending'
        schema = 'users'

    dataset = ForeignKeyField(Dataset, column_name='dataset', backref='access_pending')
    user = ForeignKeyField(User, backref='access_pending')
    has_access = IntegerField()
    access_requested = DateTimeField()


#####
# Help functions
##

def get_next_free_uid() -> int:
    """
    Get the next free uid >= 10000 and > than the current uids
    from the sftp_user table in the db.

    Returns:
        int: the next free uid

    """
    default = 10000
    next_uid = default
    try:
        current_max_uid = SFTPUser.select(fn.MAX(SFTPUser.user_uid)).get().user_uid
        if current_max_uid:
            next_uid = current_max_uid+1
    except SFTPUser.DoesNotExist:
        pass

    return next_uid


def get_admin_datasets(user):
    """
    Get a list of datasets where user is admin

    Args:
        user (User): Peewee User object for the user of interest

    Returns:
        DataSetAccess:

    """
    return DatasetAccess.select().where(DatasetAccess.user == user, DatasetAccess.is_admin)


def get_dataset(dataset: str):
    """
    Given dataset name get Dataset

    Args:
        dataset (str): short name of the dataset

    Returns:
        Dataset: the corresponding DatasetVersion entry

    """
    dataset = Dataset.select().where(Dataset.short_name == dataset).get()
    return dataset


def get_dataset_version(dataset: str, version: str = None):
    """
    Given dataset get DatasetVersion

    Args:
        dataset (str): short name of the dataset

    Returns:
        DatasetVersion: the corresponding DatasetVersion entry

    """
    if version:
        try:
            dataset_version = (DatasetVersion
                               .select(DatasetVersion, Dataset)
                               .join(Dataset)
                               .where(DatasetVersion.version == version,
                                      Dataset.short_name == dataset)).get()
        except DatasetVersion.DoesNotExist:
            logging.error(f"get_dataset_version(%s, %s): " +
                          "cannot retrieve dataset version", dataset, version)
            return None
    else:
        try:
            dataset_version = (DatasetVersionCurrent
                               .select(DatasetVersionCurrent, Dataset)
                               .join(Dataset)
                               .where(Dataset.short_name == dataset)).get()
        except DatasetVersionCurrent.DoesNotExist:
            logging.error(f"get_dataset_version({dataset}, version=None): " +
                          "cannot retrieve dataset version")
            return None
    return dataset_version


def build_dict_from_row(row) -> dict:
    """Build a dictionary from a row object"""
    outdict = {}

    for field, value in row.__dict__['__data__'].items():
        if field == "id":
            continue
        outdict[field] = value
    return outdict
