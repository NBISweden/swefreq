import json # remove when db is fixed
import logging

import handlers

from . import lookups
from . import pgsql

from .utils import add_consequence_to_variant, remove_extraneous_vep_annotations, \
    order_vep_by_csq, get_proper_hgvs

# maximum length of requested region (GetRegion)
REGION_LIMIT = 100000

class Autocomplete(handlers.UnsafeHandler):
    def get(self, dataset, query):
        ret = {}

        results = pgsql.get_autocomplete(query)
        ret = {'values': sorted(list(set(results)))[:20]}

        self.finish( ret )


class GetCoverage(handlers.UnsafeHandler):
    """
    Retrieve coverage
    """
    def get(self, dataset, datatype, item, ds_version=None):
        ret = pgsql.get_coverage(dataset, datatype, item, ds_version)
        self.finish(ret)


class GetCoveragePos(handlers.UnsafeHandler):
    """
    Retrieve coverage range
    """
    def get(self, dataset, datatype, item):
        ret = pgsql.get_coverage_pos(dataset, datatype, item)
        self.finish(ret)


class Download(handlers.UnsafeHandler):
    def get(self, dataset: str, datatype, item, ds_version=None):
        """
        Download variants as csv

        Args:
            dataset (str): dataset short name
            datatype (str): type of data
            item (str): query item
            ds_version (str): dataset version
        """
        filename = "{}_{}_{}.csv".format(dataset, datatype, item)
        self.set_header('Content-Type','text/csv')
        self.set_header('content-Disposition','attachement; filename={}'.format(filename))

        data = pgsql.get_variant_list(dataset, datatype, item)
        # Write header
        self.write(','.join([h[1] for h in data['headers']]) + '\n')

        for variant in data['variants']:
            headers = [h[0] for h in data['headers']]
            self.write(','.join(map(str, [variant[h] for h in headers])) + '\n')


class GetGene(handlers.UnsafeHandler):
    """
    Request information about a gene
    """
    def get(self, dataset, gene, ds_version=None):
        """
        Request information about a gene

        Args:
            dataset (str): short name of the dataset
            gene (str): the gene id
        """
        gene_id = gene

        ret = {'gene':{'gene_id': gene_id}}

        # Gene
        gene = lookups.get_gene(dataset, gene_id)
        #### Remove when db is fixed
        gene['stop'] = gene['start'] + 20000
        ####
        if gene:
            ret['gene'] = gene

        # Add exons from transcript
        transcript = lookups.get_transcript(dataset, gene['canonical_transcript'])
        ret['exons'] = []
        for exon in sorted(transcript['exons'], key=lambda k: k['start']):
            ret['exons'] += [{'start':exon['start'], 'stop':exon['stop'], 'type':exon['feature_type']}]

        # Variants
        ret['gene']['variants'] = lookups.get_number_of_variants_in_transcript(dataset, gene['canonical_transcript'], ds_version)

        # Transcripts
        transcripts_in_gene = lookups.get_transcripts_in_gene(dataset, gene_id)
        if transcripts_in_gene:
            ret['transcripts'] = []
            for transcript in transcripts_in_gene:
                ret['transcripts'] += [{'transcript_id':transcript['transcript_id']}]


        # temporary fix for names
        gene['gene_name'] = gene['name']
        gene['full_gene_name'] = gene['full_name']

        self.finish(ret)


class GetRegion(handlers.UnsafeHandler):
    """
    Request information about genes in a region
    """
    def get(self, dataset, region):
        """
        Request information about genes in a region

        Args:
            dataset (str): short name of the dataset
            region (str): the region in the format chr-startpos-endpos

        Returns:
            dict: information about the region and the genes found there
        """
        region = region.split('-')

        chrom = region[0]
        start = None
        stop = None

        try:
            if len(region) > 1:
                start = int(region[1])
            if len(region) > 2:
                stop = int(region[2])
        except ValueError:
            logging.error('GetRegion: unable to parse region ({})'.format(region))
            self.send_error(status_code=400)
            self.set_user_msg('Unable to parse region', 'error')
            return

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

        genes_in_region = lookups.get_genes_in_region(dataset, chrom, start, stop)
        if genes_in_region:
            ret['region']['genes'] = []
            for gene in genes_in_region:
                ret['region']['genes'] += [{'gene_id':gene['gene_id'],
                                            'gene_name':gene['gene_name'],
                                            'full_gene_name':gene['full_gene_name'],
                                           }]
        self.finish(ret)


class GetTranscript(handlers.UnsafeHandler):
    """
    Request information about a transcript
    """
    def get(self, dataset, transcript):
        """
        Request information about a transcript

        Args:
            dataset (str): short name of the dataset
            transcript (str): the transcript id

        Returns:
            dict: transcript (transcript and exons), gene (gene information)
        """
        transcript_id = transcript
        ret = {'transcript':{},
               'gene':{},
              }

        # Add transcript information
        transcript = lookups.get_transcript(dataset, transcript_id)
        ret['transcript']['id'] = transcript['transcript_id']
        ret['transcript']['number_of_CDS'] = len([t for t in transcript['exons'] if t['feature_type'] == 'CDS'])

        # Add exon information
        ret['exons'] = []
        for exon in sorted(transcript['exons'], key=lambda k: k['start']):
            ret['exons'] += [{'start':exon['start'], 'stop':exon['stop'], 'type':exon['feature_type']}]

        # Add gene information
        gene                                = lookups.get_gene_by_dbid(transcript['gene'])
        ret['gene']['id']                   = gene['gene_id']
        ret['gene']['name']                 = gene['name']
        ret['gene']['full_name']            = gene['full_name']
        ret['gene']['canonical_transcript'] = gene['canonical_transcript']

        gene_transcripts            = lookups.get_transcripts_in_gene_by_dbid(transcript['gene'])
        ret['gene']['transcripts']  = [g['transcript_id'] for g in gene_transcripts]

        self.finish(ret)


class GetVariant(handlers.UnsafeHandler):
    """
    Request information about a gene
    """
    def get(self, dataset, variant):
        """
        Request information about a gene

        Args:
            dataset (str): short name of the dataset
            variant (str): variant in the format chrom-pos-ref-alt
        """
        ret = {'variant':{}}

        # Variant
        v = variant.split('-')
        try:
            v[1] = int(v[1])
        except ValueError:
            logging.error('GetVariant: unable to parse variant ({})'.format(variant))
            self.send_error(status_code=400)
            self.set_user_msg('Unable to parse variant', 'error')
            return
        orig_variant = variant
        variant = lookups.get_variant(dataset, v[1], v[0], v[2], v[3])

        if not variant:
            logging.error('Variant not found ({})'.format(orig_variant))
            self.send_error(status_code=404)
            self.set_user_msg('Variant not found', 'error')
            return

        # Just get the information we need
        variant['quality_metrics'] = json.loads(variant['quality_metrics'])  # remove when db is fixed
        for item in ["variant_id", "chrom", "pos", "ref", "alt", "rsid", "allele_num",
                     "allele_freq", "allele_count", "orig_alt_alleles", "site_quality", "quality_metrics",
                     "transcripts", "genes"]:
            ret['variant'][item] = variant[item]
        ret['variant']['filter'] = variant['filter_string']

        variant['vep_annotations'] = json.loads(variant['vep_annotations'])  # remove when db is fixed
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
        term_map = {'allele_num':'ans', 'allele_count':'acs', 'allele_freq':'freq', 'hom_count':'homs'}
        if dataset not in frequencies['datasets']:
            frequencies['datasets'][dataset] = {'pop':dataset}
        for item in term_map:
            if item not in frequencies['total']:
                frequencies['total'][term_map[item]] = 0
            if variant[item] is None:
                frequencies['datasets'][dataset][term_map[item]] = 0
                frequencies['total'][term_map[item]] += 0
            else:
                frequencies['datasets'][dataset][term_map[item]] = variant[item]
                frequencies['total'][term_map[item]] += variant[item]
        if 'freq' in frequencies['total']:
            frequencies['total']['freq'] /= len(frequencies['datasets'].keys())

        ret['variant']['pop_freq'] = frequencies

        self.finish( ret )


class GetVariants(handlers.UnsafeHandler):
    """
    Retrieve variants
    """
    def get(self, dataset, datatype, item):
        """
        Retrieve variants

        Args:
            dataset (str): short name of the dataset
            datatype (str): gene, region, or transcript
            item (str): item to query
        """
        ret = pgsql.get_variant_list(dataset, datatype, item)
        # inconvenient way of doing humpBack-conversion
        headers = []
        for a, h in ret['headers']:
            n = a[0] + "".join([b[0].upper() + b[1:] for b in a.split("_")])[1:]
            headers += [[n, h]]
        ret['headers'] = headers
        logging.error('Variant request {} items'.format(len(ret)))
        logging.error('Variant request {} items'.format(ret))
        self.finish( ret )


class Search(handlers.UnsafeHandler):
    """
    Perform a search for the wanted object
    """
    def get(self, dataset, query):
        """
        Perform a search for the wanted object

        Args:
            dataset (str): short name of the dataset
            query (str): search query
        """
        ret = {"dataset": dataset, "value": None, "type": None}

        datatype, identifier = lookups.get_awesomebar_result(dataset, query)

        if datatype == "dbsnp_variant_set":
            datatype = "dbsnp"

        ret["type"] = datatype
        ret["value"] = identifier

        self.finish(ret)
