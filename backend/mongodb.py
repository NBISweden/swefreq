import logging
import settings
import handlers

import pymongo
import lookups


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


def get_variant_list(dataset, datatype, item):
    ret = {'variants':[], 'headers':[['variant_id','Variant'], ['chrom','Chrom'], ['pos','Position'],
                                     ['HGVS','Consequence'], ['filter','Filter'], ['major_consequence','Annotation'],
                                     ['flags','Flags'], ['allele_count','Allele Count'], ['allele_num','Allele Number'],
                                     ['hom_count','Number of Homozygous Alleles'], ['allele_freq','Allele Frequency']]}
    try:
        db = connect_db(dataset, False)
        db_shared = connect_db(dataset, True)
        try:
            if datatype == 'gene':
                variants = lookups.get_variants_in_gene(db, item)
            elif datatype == 'region':
                chrom, start, stop = item.split('-')
                variants = lookups.get_variants_in_region(db, chrom, start, stop)
            elif datatype == 'transcript':
                variants = lookups.get_variants_in_transcript(db, item)

            # Format output
            for variant in variants:
                formatted_variant = {}
                # Basic variables
                for var in ['variant_id', 'chrom', 'pos', 'HGVS', 'CANONICAL', 'major_consequence', 'filter', 'flags',
                            'allele_count', 'allele_num', 'hom_count', 'allele_freq', 'rsid']:
                    if var == 'major_consequence':
                        v = variant[var][:-8] if variant[var].endswith("_variant") else variant[var]
                        v = v.replace('_prime_', '\'')
                        formatted_variant[var] = v.replace('_', ' ')
                    elif var == 'rsid':
                        formatted_variant[var] = variant[var] if not variant[var] == "." else ""
                    elif type(variant[var]) == type([]):
                        formatted_variant[var] = ", ".join(variant[var])
                    else:
                        formatted_variant[var] = variant[var]
                ret['variants'] += [formatted_variant]
        except Exception as e:
            logging.error("{}".format(e))
    except Exception as e:
        logging.error('{} when loading variants for {} {}: {}'.format(type(e), datatype, item, e))
    return ret