import handlers

from . import lookups
from . import mongodb
from .utils import get_xpos, add_consequence_to_variant, remove_extraneous_vep_annotations, \
                   order_vep_by_csq, get_proper_hgvs


class GetTranscript(handlers.UnsafeHandler):
    def get(self, dataset, transcript):
        transcript_id = transcript
        ret = {'transcript':{},
               'gene':{},
              }

        db_shared = mongodb.connect_db(dataset, True)
        if not db_shared:
            self.set_user_msg("Could not connect to database.", "error")
            self.finish( ret )
            return

        # Add transcript information
        transcript = lookups.get_transcript(db_shared, transcript_id)
        ret['transcript']['id'] = transcript['transcript_id']
        ret['transcript']['number_of_CDS'] = len([t for t in transcript['exons'] if t['feature_type'] == 'CDS'])

        # Add exon information
        ret['exons'] = []
        for exon in sorted(transcript['exons'], key=lambda k: k['start']):
            ret['exons'] += [{'start':exon['start'], 'stop':exon['stop'], 'type':exon['feature_type']}]

        # Add gene information
        gene                                = lookups.get_gene(db_shared, transcript['gene_id'])
        ret['gene']['id']                   = gene['gene_id']
        ret['gene']['name']                 = gene['gene_name']
        ret['gene']['full_name']            = gene['full_gene_name']
        ret['gene']['canonical_transcript'] = gene['canonical_transcript']

        gene_transcripts            = lookups.get_transcripts_in_gene(db_shared, transcript['gene_id'])
        ret['gene']['transcripts']  = [g['transcript_id'] for g in gene_transcripts]

        self.finish( ret )


class GetRegion(handlers.UnsafeHandler):
    def get(self, dataset, region):
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

        db_shared = mongodb.connect_db(dataset, True)
        if not db_shared:
            self.set_user_msg("Could not connect to database.", "error")
            self.finish( ret )
            return

        genes_in_region = lookups.get_genes_in_region(db_shared, chrom, start, stop)
        if genes_in_region:
            ret['region']['genes'] = []
            for gene in genes_in_region:
                ret['region']['genes'] += [{'gene_id':gene['gene_id'],
                                            'gene_name':gene['gene_name'],
                                            'full_gene_name':gene['full_gene_name'],
                                           }]

        self.finish( ret )


class GetGene(handlers.UnsafeHandler):
    def get(self, dataset, gene):
        gene_id = gene

        ret = {'gene':{'gene_id': gene_id}}
        db = mongodb.connect_db(dataset, False)
        db_shared = mongodb.connect_db(dataset, True)
        if not db_shared or not db:
            self.set_user_msg("Could not connect to database.", "error")
            self.finish( ret )
            return

        # Gene
        gene = lookups.get_gene(db_shared, gene_id)
        ret['gene'] = gene

        # Add exons from transcript
        transcript = lookups.get_transcript(db_shared, gene['canonical_transcript'])
        ret['exons'] = []
        for exon in sorted(transcript['exons'], key=lambda k: k['start']):
            ret['exons'] += [{'start':exon['start'], 'stop':exon['stop'], 'type':exon['feature_type']}]

        # Variants
        ret['gene']['variants'] = lookups.get_number_of_variants_in_transcript(db, gene['canonical_transcript'])

        # Transcripts
        transcripts_in_gene = lookups.get_transcripts_in_gene(db_shared, gene_id)
        if transcripts_in_gene:
            ret['transcripts'] = []
            for transcript in transcripts_in_gene:
                ret['transcripts'] += [{'transcript_id':transcript['transcript_id']}]

        self.finish( ret )


class GetVariant(handlers.UnsafeHandler):
    def get(self, dataset, variant):

        ret = {'variant':{}}

        db = mongodb.connect_db(dataset, False)
        db_shared = mongodb.connect_db(dataset, True)

        if not db_shared or not db:
            self.set_user_msg("Could not connect to database.", "error")
            self.finish( ret )
            return

        # Variant
        v = variant.split('-')
        variant = lookups.get_variant(db, db_shared, get_xpos(v[0], int(v[1])), v[2], v[3])

        if variant is None:
            variant = {
                'chrom': v[0],
                'pos': int(v[1]),
                'xpos': get_xpos(v[0], int(v[1])),
                'ref': v[2],
                'alt': v[3]
            }

        # Just get the information we need
        for item in ["variant_id", "chrom", "pos", "ref", "alt", "filter", "rsid", "allele_num",
                     "allele_freq", "allele_count", "orig_alt_alleles", "site_quality", "quality_metrics",
                     "transcripts", "genes"]:
            ret['variant'][item] = variant[item]

        # Variant Effect Predictor (VEP) annotations
        # https://www.ensembl.org/info/docs/tools/vep/vep_formats.html
        ret['variant']['consequences'] = []
        if 'vep_annotations' in variant:
            add_consequence_to_variant(variant)
            variant['vep_annotations'] = remove_extraneous_vep_annotations(variant['vep_annotations'])
            # Adds major_consequence
            variant['vep_annotations'] = order_vep_by_csq(variant['vep_annotations'])
            ret['variant']['annotations'] = {}
            for annotation in variant['vep_annotations']:
                annotation['HGVS'] = get_proper_hgvs(annotation)

                # Add consequence type to the annotations if it doesn't exist
                consequence_type = annotation['Consequence'].split('&')[0]  \
                                   .replace("_variant", "")                 \
                                   .replace('_prime_', '\'')                \
                                   .replace('_', ' ')
                if consequence_type not in ret['variant']['annotations']:
                    ret['variant']['annotations'][consequence_type] = {'gene': {'name':annotation['SYMBOL'],
                                                                                'id':annotation['Gene']},
                                                                       'transcripts':[]}

                ret['variant']['annotations'][consequence_type]['transcripts'] += \
                    [{'id':           annotation['Feature'],
                      'sift':         annotation['SIFT'].rstrip("()0123456789"),
                      'polyphen':     annotation['PolyPhen'].rstrip("()0123456789"),
                      'canonical':    annotation['CANONICAL'],
                      'modification': annotation['HGVSp'].split(":")[1] if ':' in annotation['HGVSp'] else None}]


        # Dataset frequencies.
        # This is reported per variable in the database data, with dataset
        # information inside the variables,  so here we reorder to make the
        # data easier to use in the template
        frequencies = {'headers':[['Population','pop'],
                               ['Allele Count','acs'],
                               ['Allele Number', 'ans'],
                               ['Number of Homozygotes', 'homs'],
                               ['Allele Frequency', 'freq']],
                    'datasets':{},
                    'total':{}}
        for item in ['ans', 'acs', 'freq', 'homs']:
            key = 'pop_' + item
            if key not in variant:
                continue
            for _dataset, value in variant[key].items():
                if _dataset not in frequencies['datasets']:
                    frequencies['datasets'][_dataset] = {'pop':_dataset}
                frequencies['datasets'][_dataset][item] = value
                if item not in frequencies['total']:
                    frequencies['total'][item] = 0
                frequencies['total'][item] += value
        if 'freq' in frequencies['total']:
            frequencies['total']['freq'] /= len(frequencies['datasets'].keys())

        ret['variant']['pop_freq'] = frequencies

        self.finish( ret )


class GetVariants(handlers.UnsafeHandler):
    def get(self, dataset, datatype, item):
        ret = mongodb.get_variant_list(dataset, datatype, item)
        # inconvenient way of doing humpBack-conversion
        headers = []
        for a, h in ret['headers']:
            n = a[0] + "".join([b[0].upper() + b[1:] for b in a.split("_")])[1:]
            headers += [[n, h]]
        ret['headers'] = headers
        self.finish( ret )


class GetCoverage(handlers.UnsafeHandler):
    def get(self, dataset, datatype, item):
        ret = mongodb.get_coverage(dataset, datatype, item)
        self.finish( ret )


class GetCoveragePos(handlers.UnsafeHandler):
    def get(self, dataset, datatype, item):
        ret = mongodb.get_coverage_pos(dataset, datatype, item)
        self.finish( ret )


class Search(handlers.UnsafeHandler):
    def get(self, dataset, query):
        ret = {"dataset": dataset, "value": None, "type": None}

        db = mongodb.connect_db(dataset, False)
        db_shared = mongodb.connect_db(dataset, True)

        if not db_shared or not db:
            self.set_user_msg("Could not connect to database.", "error")
            self.finish( ret )
            return

        datatype, identifier = lookups.get_awesomebar_result(db, db_shared, query)

        if datatype == "dbsnp_variant_set":
            datatype = "dbsnp"

        ret["type"] = datatype
        ret["value"] = identifier

        self.finish( ret )


class Autocomplete(handlers.UnsafeHandler):
    def get(self, dataset, query):
        ret = {}

        results = mongodb.get_autocomplete(dataset, query)
        ret = {'values': sorted(list(set(results)))[:20]}

        self.finish( ret )


class Download(handlers.UnsafeHandler):
    def get(self, dataset, datatype, item):
        filename = "{}_{}_{}.csv".format(dataset, datatype, item)
        self.set_header('Content-Type','text/csv')
        self.set_header('content-Disposition','attachement; filename={}'.format(filename))

        data = mongodb.get_variant_list(dataset, datatype, item)
        # Write header
        self.write(','.join([h[1] for h in data['headers']]) + '\n')

        for variant in data['variants']:
            headers = [h[0] for h in data['headers']]
            self.write(','.join(map(str, [variant[h] for h in headers])) + '\n')
