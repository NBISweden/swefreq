#!/usr/bin/env python3
import re
import sys
import time
import logging

import db
from .data_importer import DataImporter

METRICS = [
    'BaseQRankSum',
    'ClippingRankSum',
    'DP',
    'FS',
    'InbreedingCoeff',
    'MQ',
    'MQRankSum',
    'QD',
    'ReadPosRankSum',
    'VQSLOD'
]


class RawDataImporter(DataImporter):
    def __init__(self, settings):
        super().__init__(settings)
        self.dataset_version = None
        self.dataset = None
        self.sampleset = None
        self.counter = {'coverage': None,
                        'variants': None,
                        'beaconvariants': 0,
                        'calls': 0,
                        'tmp_calls': set()}
        self.lastpos = 0
        self.chrom = None

    def _set_dataset_info(self):
        """ Save dataset information given as parameters """
        if self.settings.beacon_description:
            self.dataset.description = self.settings.beacon_description
            self.dataset.save()
        if self.settings.assembly_id:
            self.dataset_version.var_call_ref = self.settings.assembly_id
            self.dataset_version.save()
        if self.settings.sampleset_size:
            self.sampleset.sample_size = self.settings.sampleset_size
            self.sampleset.save()
        if self.settings.dataset_size:
            self.dataset.dataset_size = self.settings.dataset_size
            self.dataset.save()

    def _select_dataset_version(self):
        datasets = []

        # Make sure that the dataset exists
        try:
            ds = db.Dataset.get(short_name=self.settings.dataset)
        except db.Dataset.DoesNotExist:
            logging.error("Unknown dataset '%s'", self.settings.dataset)
            logging.info("Available datasets are:")
            for dataset in db.Dataset.select():
                logging.info(" * %s", dataset.short_name)
            sys.exit(1)
        logging.info("Using dataset {}".format(ds.short_name))
        self.dataset = ds

        versions = [v for v in db.DatasetVersion.select().where(db.DatasetVersion.dataset == ds)]

        # Make sure that the dataset version exists
        if not versions:
            raise db.DatasetVersion.DoesNotExist("No versions exist for this dataset")

        if self.settings.version not in [v.version for v in versions]:
            logging.error("Unknown version '%s' for dataset '%s'.", self.settings.version, self.dataset.short_name)
            logging.info("Available versions are:")
            for version in versions:
                logging.info(" * %s", version.version)
            sys.exit(1)
        self.dataset_version = [v for v in versions if v.version == self.settings.version][0]

        # Set the sample set's sample size
        if self.settings.set_vcf_sampleset_size or self.settings.sampleset_size:
            try:
                samplesets = db.SampleSet.select()
                self.sampleset = [s for s in samplesets if s.dataset.id == self.dataset.id][0]
            except IndexError:
                logging.warning("No sample set found for data set {}".format(self.dataset.id))
                logging.warning("Sample size will not be set")
                self.settings.set_vcf_sampleset_size = False
                self.settings.sampleset_size = 0

    def _create_beacon_counts(self):
        """
        Add the number of unique references at each position (callcount),
        the number of unique ref-alt pairs at each position (variantount)
        and the datasetid (eg GRCh37:swegen:2019-01-01)
        to the beacon_dataset_counts_table.
        """
        # count the calls at the last position
        self.counter['calls'] += len(self.counter['tmp_calls'])

        ref_build = self.dataset_version.reference_set.reference_build
        if not ref_build:
            logging.warning('Reference build not set for dataset version.')
            ref_build = ''  # avoid None
        datasetid = ':'.join([ref_build, self.dataset.short_name, self.dataset_version.version])
        datarow = {'datasetid': datasetid,
                   'callcount': self.counter['calls'],
                   'variantcount': self.counter['beaconvariants']}
        logging.info('Dataset counts: callcount: %s, variantcount: %s', datarow['callcount'], datarow['variantcount'])
        if not self.settings.dry_run:
            db.BeaconCounts.insert(datarow).execute()

    def _insert_coverage(self):
        """
        Header columns are chromosome, position, mean coverage, median coverage,
        and then coverage under 1, 5 10, 15, 20, 25, 30, 50, 100.
        """
        start = time.time()
        header = [('chrom', str), ('pos', int), ('mean', float),
                  ('median', float), ('cov1', float), ('cov5', float),
                  ('cov10', float), ('cov15', float), ('cov20', float), ('cov25', float),
                  ('cov30', float), ('cov50', float), ('cov100', float)]
        logging.info("Inserting Coverage")
        batch = []
        last_progress = -1.0
        counter = 0
        with db.database.atomic():
            for filename in self.settings.coverage_file:
                for line in self._open(filename, binary=False):
                    line = line.strip()
                    if line.startswith("#"):
                        continue

                    data = {}
                    for i, item in enumerate(line.strip().split("\t")):
                        if i == 0:
                            data['dataset_version'] = self.dataset_version
                        data[header[i][0]] = header[i][1](item)

                    # re-format coverage for batch
                    data['coverage'] = [data['cov1'], data['cov5'], data['cov10'],
                                        data['cov15'], data['cov20'], data['cov25'],
                                        data['cov30'], data['cov50'], data['cov100']]
                    del data['cov1']
                    del data['cov5']
                    del data['cov10']
                    del data['cov15']
                    del data['cov20']
                    del data['cov25']
                    del data['cov30']
                    del data['cov50']
                    del data['cov100']

                    if self.counter['coverage'] is not None:
                        counter += 1

                    batch += [data]
                    if len(batch) >= self.settings.batch_size:
                        if not self.settings.dry_run:
                            db.Coverage.insert_many(batch).execute()
                        batch = []
                        # Update progress
                        if self.counter['coverage'] is not None:
                            last_progress = self._update_progress_bar(counter, self.counter['coverage'], last_progress)
            if batch and not self.settings.dry_run:
                db.Coverage.insert_many(batch).execute()
        if self.counter['coverage'] is not None:
            last_progress = self._update_progress_bar(counter, self.counter['coverage'], last_progress, finished=True)
        if not self.settings.dry_run:
            logging.info("Inserted {} coverage records in {}".format(counter, self._time_since(start)))

    def _insert_variants(self):
        """
        Insert variants from a VCF file
        """
        logging.info("Inserting variants%s", " (dry run)" if self.settings.dry_run else "")
        header = [("chrom", str), ("pos", int), ("rsid", str), ("ref", str),
                  ("alt", str), ("site_quality", float), ("filter_string", str)]
        start = time.time()
        batch = []
        genes = []
        transcripts = []

        last_progress = -1.0
        counter = 0
        samples = 0
        vep_field_names = None
        dp_mids = None
        gq_mids = None
        with db.database.atomic():
            for filename in self.settings.variant_file:
                # Get reference set for the variant
                ref_set = self.dataset_version.reference_set

                # Get all genes and transcripts for foreign keys
                ref_genes = {gene.gene_id: gene.id for gene in (db.Gene.select(db.Gene.id, db.Gene.gene_id)
                                                                .where(db.Gene.reference_set == ref_set))}
                ref_transcripts = {tran.transcript_id: tran.id for tran in (db.Transcript
                                                                            .select(db.Transcript.id,
                                                                                    db.Transcript.transcript_id)
                                                                            .join(db.Gene)
                                                                            .where(db.Gene.reference_set == ref_set))}
                for line in self._open(filename, binary=False):
                    line = line.strip()

                    if line.startswith("#"):
                        # Check for some information that we need
                        if line.startswith('##INFO=<ID=CSQ'):
                            vep_field_names = line.split('Format: ')[-1].strip('">').split('|')
                        if line.startswith('##INFO=<ID=DP_HIST'):
                            dp_mids = map(float, line.split('Mids: ')[-1].strip('">').split('|'))
                        if line.startswith('##INFO=<ID=GQ_HIST'):
                            gq_mids = map(float, line.split('Mids: ')[-1].strip('">').split('|'))
                        if line.startswith('#CHROM'):
                            samples = len(line.split('\t')[9:])
                        continue

                    if not self.settings.beacon_only:
                        if vep_field_names is None:
                            logging.error("VEP_field_names is empty. Make sure VCF header is present.")
                            sys.exit(1)

                    base = {}
                    for i, item in enumerate(line.strip().split("\t")):
                        if i == 0:
                            base['dataset_version'] = self.dataset_version
                        if i < 7:
                            base[header[i][0]] = header[i][1](item)
                        elif i == 7 or not self.settings.beacon_only:
                            # only parse column 7 (maybe also for non-beacon-import?)
                            info = dict([(x.split('=', 1)) if '=' in x else (x, x) for x in re.split(';(?=\w)', item)])

                    if base["chrom"].startswith('GL') or base["chrom"].startswith('MT'):
                        continue

                    consequence_array = info['CSQ'].split(',') if 'CSQ' in info else []
                    if not self.settings.beacon_only:
                        annotations = [dict(zip(vep_field_names, x.split('|'))) for x in consequence_array if len(vep_field_names) == len(x.split('|'))]

                    alt_alleles = base['alt'].split(",")
                    if base['rsid'].startswith('rs'):
                        rsids = [int(rsid.strip('rs')) for rsid in base['rsid'].split(';')]
                    else:
                        rsids = [None]

                    try:
                        hom_counts = [int(info['AC_Hom'])]
                    except KeyError:
                        hom_counts = None # null is better than 0, as 0 has a meaning
                    except ValueError:
                        hom_counts = [int(count) for count in info['AC_Hom'].split(',')]

                    fmt_alleles = [f'{base["chrom"]}-{base["pos"]}-{base["ref"]}-{x}' for x in alt_alleles]

                    for i, alt in enumerate(alt_alleles):
                        if not self.settings.beacon_only:
                            vep_annotations = [ann for ann in annotations if int(ann['ALLELE_NUM']) == i + 1]

                        data = dict(base)
                        data['pos'], data['ref'], data['alt'] = base['pos'], base['ref'], alt
                        data['orig_alt_alleles'] = fmt_alleles

                        if len(rsids) <= i:
                            data['rsid'] = rsids[-1]  # same id as the last alternate
                        else:
                            data['rsid'] = rsids[i]

                        an, ac = 'AN_Adj', 'AC_Adj'
                        if 'AN_Adj' not in info:
                            an = 'AN'
                        if 'AC_Adj' not in info:
                            ac = 'AC'

                        data['allele_num'] = int(info[an])
                        data['allele_freq'] = None
                        if 'NS' in info and not samples:
                            # save this unless we already know the sample size
                            samples = int(info['NS'])

                        data['allele_count'] = int(info[ac].split(',')[i])
                        if 'AF' in info and data['allele_num'] > 0:
                            data['allele_freq'] = data['allele_count']/float(info[an])

                        if not self.settings.beacon_only:
                            data['vep_annotations'] = vep_annotations

                            genes.append(list(set({annotation['Gene'] for annotation in vep_annotations if annotation['Gene'][:4] == 'ENSG'})))
                            transcripts.append(list(set({annotation['Feature'] for annotation in vep_annotations if annotation['Feature'][:4] == 'ENST'})))

                        data['hom_count'] = hom_counts[i] if hom_counts else None

                        data['variant_id'] = '{}-{}-{}-{}'.format(data['chrom'], data['pos'], data['ref'], data['alt'])
                        data['quality_metrics'] = dict([(x, info[x]) for x in METRICS if x in info])
                        batch += [data]
                        if self.settings.count_calls:
                            self.get_callcount(data)  # count calls (one per reference)
                            self.counter['beaconvariants'] += 1  # count variants (one per alternate)
                    counter += 1  # count variants (one per vcf row)

                    if len(batch) >= self.settings.batch_size:
                        if not self.settings.dry_run:
                            if not self.settings.beacon_only:
                                try:
                                    curr_id = db.Variant.select(db.Variant.id).order_by(db.Variant.id.desc()).limit(1).get().id
                                except db.Variant.DoesNotExist:
                                    # assumes next id will be 1 if table is empty
                                    curr_id = 0

                            db.Variant.insert_many(batch).execute()

                            if not self.settings.beacon_only:
                                last_id = db.Variant.select(db.Variant.id).order_by(db.Variant.id.desc()).limit(1).get().id
                                if  last_id-curr_id == len(batch):
                                    indexes = list(range(curr_id+1, last_id+1))
                                else:
                                    indexes = []
                                    for entry in batch:
                                        indexes.append(db.Variant.select(db.Variant.id).where(db.Variant.variant_id == entry['variant_id']).get().id)
                                self.add_variant_genes(indexes, genes, ref_genes)
                                self.add_variant_transcripts(indexes, transcripts, ref_transcripts)

                        genes = []
                        transcripts = []
                        batch = []
                        # Update progress
                        if self.counter['variants'] != None:
                            last_progress = self._update_progress_bar(counter, self.counter['variants'], last_progress)

            if batch and not self.settings.dry_run:
                if not self.settings.dry_run:
                    if not self.settings.beacon_only:
                        try:
                            curr_id = db.Variant.select(db.Variant.id).order_by(db.Variant.id.desc()).limit(1).get().id
                        except db.Variant.DoesNotExist:
                            # assumes next id will be 1 if table is empty
                            curr_id = 0

                    db.Variant.insert_many(batch).execute()

                    if not self.settings.beacon_only:
                        last_id = db.Variant.select(db.Variant.id).order_by(db.Variant.id.desc()).limit(1).get().id
                        if  last_id-curr_id == len(batch):
                            indexes = list(range(curr_id+1, last_id+1))
                        else:
                            indexes = []
                            for entry in batch:
                                indexes.append(db.Variant.select(db.Variant.id).where(db.Variant.variant_id == entry['variant_id']).get().id)
                        self.add_variant_genes(indexes, genes, ref_genes)
                        self.add_variant_transcripts(indexes, transcripts, ref_transcripts)

        if self.settings.set_vcf_sampleset_size and samples:
            self.sampleset.sample_size = samples
            self.sampleset.save()

        self.dataset_version.num_variants = counter
        self.dataset_version.save()
        if self.counter['variants'] != None:
            last_progress = self._update_progress_bar(counter, self.counter['variants'], last_progress, finished=True)
        if not self.settings.dry_run:
            logging.info("Inserted {} variant records in {}".format(counter, self._time_since(start)))

    def get_callcount(self, data):
        """Increment the call count by the calls found at this position."""
        if data['chrom'] == self.chrom and data['pos'] < self.lastpos:
            # If this position is smaller than the last, the file order might be invalid.
            # Give a warning, but keep on counting.
            msg = "VCF file not ok, variants not given in incremental order. Callcount may not be valid!!!\n\n"
            logging.warning(msg)

        if data['chrom'] != self.chrom or data['pos'] != self.lastpos:
            # We are at a new position, count and save the calls for the last position
            self.counter['calls'] += len(self.counter['tmp_calls'])

            # reset the counters
            self.counter['tmp_calls'] = set()
            self.lastpos = data['pos']
            self.chrom = data['chrom']

        # save the references for this position
        self.counter['tmp_calls'].add(data['ref'])

    def count_entries(self):
        start = time.time()
        if self.settings.coverage_file:
            self.counter['coverage'] = 0
            logging.info("Counting coverage lines")
            for filename in self.settings.coverage_file:
                for line in self._open(filename, binary=False):
                    line = line.strip()
                    if line.startswith("#"):
                        continue
                    self.counter['coverage'] += 1
            logging.info("Found {:,} coverage lines".format(self.counter['coverage']))

        if self.settings.variant_file:
            self.counter['variants'] = 0
            logging.info("Counting variant lines")
            for filename in self.settings.variant_file:
                for line in self._open(filename, binary=False):
                    line = line.strip()
                    if line.startswith("#"):
                        continue
                    self.counter['variants'] += 1
            logging.info("Found {:,} variants".format(self.counter['variants']))

        logging.info("Counted input data lines in {} ".format(self._time_since(start)))

    def prepare_data(self):
        self._select_dataset_version()

    def start_import(self):
        self._set_dataset_info()
        if self.settings.variant_file:
            self._insert_variants()
            if self.settings.count_calls:
                self._create_beacon_counts()
        if not self.settings.beacon_only and self.settings.coverage_file:
            self._insert_coverage()

    def add_variant_genes(self, variant_indexes:list, genes_to_add:list, ref_genes:dict):
        batch = []
        for i in range(len(variant_indexes)):
            connected_genes = [{'variant':variant_indexes[i], 'gene':ref_genes[gene]} for gene in genes_to_add[i] if gene]
            batch += connected_genes
        if not self.settings.dry_run:
            db.VariantGenes.insert_many(batch).execute()

    def add_variant_transcripts(self, variant_indexes:list, transcripts_to_add:list, ref_transcripts:dict):
        batch = []
        for i in range(len(variant_indexes)):
            connected_transcripts = [{'variant':variant_indexes[i], 'transcript':ref_transcripts[transcript]}
                                     for transcript in transcripts_to_add[i]]
            batch += connected_transcripts
        if not self.settings.dry_run:
            db.VariantTranscripts.insert_many(batch).execute()
