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
