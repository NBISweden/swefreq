import os
import logging
import settings
import handlers

import pymongo
import lookups
from utils import *
from collections import OrderedDict

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


class GetTranscript(handlers.UnsafeHandler):
    def get(self, dataset, transcript):
        transcript_id = transcript
        ret = {'transcript':{},
               'gene':{},
              }
        try:
            db = connect_db(dataset, False)
            db_shared = connect_db(dataset, True)
            try:
                transcript = lookups.get_transcript(db_shared, transcript_id)
                ret['transcript']['id'] = transcript['transcript_id']
                ret['transcript']['number_of_CDS'] = len([t for t in transcript['exons'] if t['feature_type'] == 'CDS'])
            except Exception as e:
                logging.error("{}".format(e))

            gene                                = lookups.get_gene(db_shared, transcript['gene_id'])
            ret['gene']['id']                   = gene['gene_id']
            ret['gene']['name']                 = gene['gene_name']
            ret['gene']['full_name']            = gene['full_gene_name']
            ret['gene']['canonical_transcript'] = gene['canonical_transcript']

            gene_transcripts            = lookups.get_transcripts_in_gene(db_shared, transcript['gene_id'])
            ret['gene']['transcripts']  = [g['transcript_id'] for g in gene_transcripts] 

        except Exception as e:
            logging.error('{} when loading transcript {}: {}'.format(type(e), transcript_id, e))

        self.finish( ret )


class GetRegion(handlers.UnsafeHandler):
    def get(self, dataset, region):
        region_id = region
        region = region.split('-')
        REGION_LIMIT = 100000

        chrom = region[0]
        start = None
        stop = None
        if len(region) > 1:
            start = int(region[1])
        if len(region) > 2:
            stop = int(region[2])
        if not start:
            start = 0
        if not stop and start:
            stop = start
        if start == stop:
            start -= min(start, 20)
            stop += 20
        ret = {'region':{'chrom': chrom,
                         'start': start,
                         'stop':  stop,
                         'limit': REGION_LIMIT,
                        },
              }
        try:
            db = connect_db(dataset, False)
            db_shared = connect_db(dataset, True)
            try:
                genes_in_region = lookups.get_genes_in_region(db_shared, chrom, start, stop)
                if (genes_in_region):
                    ret['region']['genes'] = []
                    for gene in genes_in_region:
                        ret['region']['genes'] += [{'gene_id':gene['gene_id'],
                                                    'gene_name':gene['gene_name'],
                                                    'full_gene_name':gene['full_gene_name'],
                                                   }]
            except Exception as e:
                logging.error("{}".format(e))
        except Exception as e:
            logging.error('{} when loading region {}: {}'.format(type(e), region_id, e))

        self.finish( ret )


class GetGene(handlers.UnsafeHandler):
    def get(self, dataset, gene):
        gene_id = gene

        ret = {'gene':{'gene_id': gene_id}}
        try:
            db = connect_db(dataset, False)
            db_shared = connect_db(dataset, True)
            try:
                # Gene
                gene = lookups.get_gene(db_shared, gene_id)
                ret['gene'] = gene

                # Variants
                variants_in_transcript = lookups.get_variants_in_transcript(db, gene['canonical_transcript'])
                if (variants_in_transcript):
                    ret['variants'] = {'filtered':len([v for v in variants_in_transcript if v['filter'] == 'PASS']),
                                       'total':   len( variants_in_transcript )}

                # Transcripts
                transcripts_in_gene = lookups.get_transcripts_in_gene(db_shared, gene_id)
                if (transcripts_in_gene):
                    ret['transcripts'] = []
                    for transcript in transcripts_in_gene:
                        ret['transcripts'] += [{'transcript_id':transcript['transcript_id']}]

            except Exception as e:
                logging.error("{}".format(e))
        except Exception as e:
            logging.error('{} when loading gene {}: {}'.format(type(e), gene_id, e))

        self.finish( ret )


class GetVariant(handlers.UnsafeHandler):
    def get(self, dataset, variant):
        variant_id = variant

        ret = {'variant':{}}
        try:
            db = connect_db(dataset, False)
            db_shared = connect_db(dataset, True)
            try:
                # Variant
                chrom, pos, ref, alt = variant_id.split('-')
                pos = int(pos)

                xpos = get_xpos(chrom, pos)
                variant = lookups.get_variant(db, db_shared, xpos, ref, alt)

                if variant is None:
                    variant = {
                        'chrom': chrom,
                        'pos': pos,
                        'xpos': xpos,
                        'ref': ref,
                        'alt': alt
                    }
                # Just get the information we need
                for item in ["variant_id", "chrom", "pos", "ref", "alt", "filter", "rsid", "allele_num",
                             "allele_freq", "allele_count", "orig_alt_alleles", "site_quality", "quality_metrics"]:
                    ret['variant'][item] = variant[item]
                consequences = OrderedDict()
            except Exception as e:
                logging.error("{}".format(e))
        except Exception as e:
            logging.error('{} when loading variant {}: {}'.format(type(e), variant_id, e))

        self.finish( ret )


class Search(handlers.UnsafeHandler):
    def get(self, dataset):
        try:
            db = connect_db(dataset, False)
            db_shared = connect_db(dataset, True)

            query = self.get_argument('query', "")
            datatype, identifier = lookups.get_awesomebar_result(db, db_shared, query)

            if datatype in ["error", "not_found"]:
                self.redirect("/dataset/{}/browser/not_found".format(dataset))
            if datatype == "dbsnp_variant_set":
                datatype = "dbsnp"

            self.redirect("/dataset/{}/browser/{}/{}".format(dataset,datatype,identifier))
        except Exception as e:
            logging.error('{} when connecting to database for dataset {}.'.format(type(e), dataset))
            self.redirect("/dataset/{}/browser/not_found".format(dataset))


class Autocomplete(handlers.UnsafeHandler):
    def get(self, dataset, query):
        ret = {}
        # This is a workaround so that I don't have to modify the lookups.py file (yet)
        class Autocomplete(object):
            pass
        g = Autocomplete()
        try:
            g.autocomplete_strings = [s.strip() for s in open(os.path.join(os.path.dirname(__file__), 'autocomplete_strings.txt'))]
            suggestions = lookups.get_awesomebar_suggestions(g, query)

            ret = {'values': sorted(list(set(suggestions)))[:5]}
        except Exception as e:
            logging.error('{} when fetching autocomplete for {} in dataset {}: {}'.format(type(e), query, dataset, e))
        self.finish( ret )
