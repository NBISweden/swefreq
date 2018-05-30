import logging
import settings
import handlers
import pymongo

from . import lookups
from .utils import *

EXON_PADDING = 50

def connect_db(dataset, use_shared_data=False):
    """
    Connects to a specific database based on the values stored in settings for
    a given dataset, and whether to use shared data or not.
    """
    database = 'shared' if use_shared_data else 'db'
    try:
        client = pymongo.MongoClient(connect=False, host=settings.mongo_host, port=settings.mongo_port)

        auth_db = client['exac-user']
        auth_db.authenticate(settings.mongo_user, settings.mongo_password)

        db = client[settings.mongo_databases[dataset][database]]

        return db
    except Exception as e:
        logging.error("Failed to connect to database '{}' for dataset '{}'".format(database, dataset))
    return None


def get_autocomplete(dataset, query):
    try:
        db_shared = connect_db(dataset, True)
        results = db_shared.genes.distinct("gene_name", {"gene_name": {'$regex': '^{}.*'.format(query), '$options': 'i'}})
        return results
    except pymongo.errors.OperationFailure as e:
        logging.error("PyMongo OperationFailure: {}".format(e))


def get_variant_list(dataset, datatype, item):
    headers = [['variant_id','Variant'], ['chrom','Chrom'], ['pos','Position'],
                                     ['HGVS','Consequence'], ['filter','Filter'], ['major_consequence','Annotation'],
                                     ['flags','Flags'], ['allele_count','Allele Count'], ['allele_num','Allele Number'],
                                     ['hom_count','Number of Homozygous Alleles'], ['allele_freq','Allele Frequency']]

    try:
        db = connect_db(dataset, False)
        db_shared = connect_db(dataset, True)

        if datatype == 'gene':
            variants = lookups.get_variants_in_gene(db, item)
        elif datatype == 'region':
            chrom, start, stop = item.split('-')
            variants = lookups.get_variants_in_region(db, chrom, start, stop)
        elif datatype == 'transcript':
            variants = lookups.get_variants_in_transcript(db, item)

        # Format output
        def format_variant(variant):
            if variant['rsid'] == '.':
                variant['rsid'] = ''

            variant['major_consequence'] = (variant['major_consequence'].replace('_variant','')
                                                                        .replace('_prime_', '\'')
                                                                        .replace('_', ' '))

            # This is so an array values turns into a comma separated string instead
            return {k: ", ".join(v) if type(v) == type([]) else v for k, v in variant.items()}
        variants = list(map(format_variant, variants))
        return {'variants': variants, 'headers': headers}

    except pymongo.errors.OperationFailure as e:
        logging.error("PyMongo OperationFailure: {}".format(e))

    # TODO We should return a http error code here.


def get_coverage(dataset, datatype, item):
    ret = {'coverage':[]}

    db = connect_db(dataset, False)
    db_shared = connect_db(dataset, True)
    try:
        if datatype == 'gene':
            gene = lookups.get_gene(db_shared, item)
            transcript = lookups.get_transcript(db_shared, gene['canonical_transcript'])
            xstart = transcript['xstart'] - EXON_PADDING
            xstop  = transcript['xstop'] + EXON_PADDING
            ret['coverage'] = lookups.get_coverage_for_transcript(db, xstart, xstop)
        elif datatype == 'region':
            chrom, start, stop = item.split('-')
            xstart = get_xpos(chrom, int(start))
            xstop = get_xpos(chrom, int(stop))
            ret['coverage'] = lookups.get_coverage_for_bases(db, xstart, xstop)
        elif datatype == 'transcript':
            transcript = lookups.get_transcript(db_shared, item)
            xstart = transcript['xstart'] - EXON_PADDING
            xstop  = transcript['xstop'] + EXON_PADDING
            ret['coverage'] = lookups.get_coverage_for_transcript(db, xstart, xstop)

    except pymongo.errors.OperationFailure as e:
        logging.error("PyMongo OperationFailure: {}".format(e))

    return ret


def get_coverage_pos(dataset, datatype, item):
    ret = {'start':None, 'stop':None, 'chrom':None}

    db = connect_db(dataset, False)
    db_shared = connect_db(dataset, True)
    try:
        if datatype == 'gene':
            gene = lookups.get_gene(db_shared, item)
            transcript = lookups.get_transcript(db_shared, gene['canonical_transcript'])
        elif datatype == 'transcript':
            transcript = lookups.get_transcript(db_shared, item)

        if datatype == 'region':
            chrom, start, stop = item.split('-')
            start = int(start)
            stop = int(stop)
        else:
            start = transcript['start'] - EXON_PADDING
            stop  = transcript['stop'] + EXON_PADDING
            chrom = transcript['chrom']

        ret['start'] = start
        ret['stop'] = stop
        ret['chrom'] = chrom
    except pymongo.errors.OperationFailure as e:
        logging.error("PyMongo OperationFailure: {}".format(e))

    return ret
