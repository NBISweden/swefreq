#!/usr/bin/env python3
"""Read data from a vcf file and add the variants to a database."""

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
    """Read data from a vcf file and add the variants to a database."""

    def __init__(self, settings):
        """Set the provided settings and prepare the main variables."""
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
        """Save dataset information given as parameters."""
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
        """Select the dataset version to use."""
        # Make sure that the dataset exists
        try:
            chosen_ds = db.Dataset.get(short_name=self.settings.dataset)
        except db.Dataset.DoesNotExist:
            logging.error(f"Unknown dataset {self.settings.dataset}")
            logging.info("Available datasets are:")
            for dataset in db.Dataset.select():
                logging.info(f" * {dataset.short_name}")
            sys.exit(1)
        logging.info(f"Using dataset {chosen_ds.short_name}")
        self.dataset = chosen_ds

        versions = [v for v in (db.DatasetVersion.select().
                                where(db.DatasetVersion.dataset == chosen_ds))]

        # Make sure that the dataset version exists
        if not versions:
            raise db.DatasetVersion.DoesNotExist("No versions exist for this dataset")

        if self.settings.version not in [v.version for v in versions]:
            logging.error(f"Unknown version '{self.settings.version}' " +
                          f"for dataset '{self.dataset.short_name}'.")
            logging.info("Available versions are:")
            for version in versions:
                logging.info(f" * {version.version}")
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
        Prepare counts for the beacon.

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
        logging.info(f"Dataset counts: callcount: {datarow['callcount']}, " +
                     f"variantcount: {datarow['variantcount']}")
        if not self.settings.dry_run:
            db.BeaconCounts.insert(datarow).execute()

    def _insert_coverage(self):
        """
        Import coverage.

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

                    data = self._parse_baseinfo(header, line)

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
                            last_progress = self._update_progress_bar(counter,
                                                                      self.counter['coverage'],
                                                                      last_progress)
            if batch and not self.settings.dry_run:
                db.Coverage.insert_many(batch).execute()
        if self.counter['coverage'] is not None:
            last_progress = self._update_progress_bar(counter,
                                                      self.counter['coverage'],
                                                      last_progress,
                                                      finished=True)
        self._log_insertion(counter, "coverage", start)

    def _parse_manta(self):
        """Parse a manta file."""
        # Skip column 5 and 6 (QUAL and FILTER), will not be used
        header = [("chrom", str), ("pos", int), ("chrom_id", str), ("ref", str), ("alt", str)]

        batch = []
        counter = 0
        last_progress = 0
        start = time.time()
        for filename in self.settings.variant_file:
            for line in self._open(filename):
                line = line.strip()
                if line.startswith("#"):
                    continue

                base = self._parse_baseinfo(header, line)
                info = self._parse_info(line)

                if info.get('SVTYPE') != 'BND':
                    continue

                if self._is_non_chromosome(base["chrom"]):
                    # A BND *from* a non-chromosome.
                    continue

                batch += self._parse_bnd_alleles(base, info)

                # count variants (one per vcf row)
                counter += 1

                if len(batch) >= self.settings.batch_size:
                    if not self.settings.dry_run:
                        db.VariantMate.insert_many(batch).execute()
                    batch = []

                    # Update progress
                    if self.counter['variants']:
                        last_progress = self._update_progress_bar(counter,
                                                                  self.counter['variants'],
                                                                  last_progress)

        # Store all variants and counter values
        if batch and not self.settings.dry_run:
            db.VariantMate.insert_many(batch).execute()

        if self.counter['variants']:
            last_progress = self._update_progress_bar(counter,
                                                      self.counter['variants'],
                                                      last_progress,
                                                      finished=True)
        self._log_insertion(counter, "breakend", start)

    def _estimate_variant_lastid(self):  # pylint: disable=no-self-use
        """
        Return the id of the variant with the highest id.

        Returns 0 if table is empty.

        Returns:
            int: id of the variant with highest id or 0

        """
        try:
            return (db.Variant.select(db.Variant.id)
                    .order_by(db.Variant.id.desc())
                    .limit(1)
                    .get().id)
        except db.Variant.DoesNotExist:
            return 0

    def _add_variants_to_db(self, batch: list, genes: list, transcripts: list, references: dict):
        """
        Add variants to db.

        Args:
            batch (list): variant data (dict)
            genes (list): genes for the variants
            transcripts(list): transcripts for the variants
            references (dict): reference genes and transcripts
        """
        if not self.settings.beacon_only:
            curr_id = self._estimate_variant_lastid()

        db.Variant.insert_many(batch).execute()

        # check if the variant dbid estimate is correct, otherwise must check manually
        if not self.settings.beacon_only:
            last_id = self._estimate_variant_lastid()
            if last_id and last_id-curr_id == len(batch):
                indexes = list(range(curr_id+1, last_id+1))
            else:
                logging.warning("Bad match between ids - slow check")
                indexes = []
                for entry in batch:
                    indexes.append(db.Variant.select(db.Variant.id)
                                   .where(db.Variant.variant_id == entry['variant_id'])
                                   .get().id)
            self._add_variant_genes(indexes, genes, references['genes'])
            self._add_variant_transcripts(indexes, transcripts, references['transcripts'])

    def _get_genes_transcripts(self):
        """
        Retrieve the genes and transcripts for the current dataset version in the form
        `{entity: dbid}`.

        Returns:
            tuple: (genes, transcripts)

        """
        ref_set = self.dataset_version.reference_set
        genes = {gene.gene_id: gene.id
                 for gene in (db.Gene.select(db.Gene.id, db.Gene.gene_id)
                              .where(db.Gene.reference_set == ref_set))}
        transcripts = {tran.transcript_id: tran.id
                       for tran in (db.Transcript.select(db.Transcript.id,
                                                         db.Transcript.transcript_id)
                                    .join(db.Gene)
                                    .where(db.Gene.reference_set == ref_set))}
        return genes, transcripts

    def _parse_variant_row(self, line: str, batch_cont: dict, headers: list, vep_field_names: list):  # pylint: disable=too-many-locals
        """
        Parse a VCF row for a position (potentially multiple variants).

        Data is added in-place.

        Args:
            line (str): the raw text row
            batch_cont (dict): should contain batch, genes, transcripts
            headers (list): (header, type)
            vep_field_names (list): VEP field names

        """
        base = self._parse_baseinfo(headers, line)
        info = self._parse_info(line)

        if self._is_non_chromosome(base["chrom"]):
            return

        consequence_array = info['CSQ'].split(',') if 'CSQ' in info else []

        alt_alleles = base['alt'].split(",")
        rsids = [int(rsid.strip('rs'))
                 for rsid in base['rsid'].split(';')
                 if rsid.startswith('rs')]
        if not rsids:
            rsids = [None]

        try:
            hom_counts = [int(info['AC_Hom'])]
        except KeyError:
            hom_counts = []  # null is better than 0, as 0 has a meaning
        except ValueError:
            # multiple variants on same row
            hom_counts = [int(count) for count in info['AC_Hom'].split(',')]

        base['orig_alt_alleles'] = [f'{base["chrom"]}-{base["pos"]}-{base["ref"]}-{x}'
                                    for x in alt_alleles]

        for i, alt in enumerate(alt_alleles):
            data = dict(base)
            data['alt'] = alt

            data['rsid'] = rsids[i] if i < len(rsids) else rsids[-1]

            data['allele_num'] = int((info['AN_Adj'] if 'AN_Adj' in info else info['AN']))
            data['allele_freq'] = None

            data['allele_count'] = int((info['AC_Adj'] if 'AC_Adj' in info
                                        else info['AC']).split(',')[i])
            if 'AF' in info and data['allele_num'] > 0:
                data['allele_freq'] = data['allele_count']/data['allele_num']

            if not self.settings.beacon_only:
                annotations = [dict(zip(vep_field_names, x.split('|')))
                               for x in consequence_array
                               if len(vep_field_names) == len(x.split('|'))]
                data['vep_annotations'] = [ann for ann in annotations
                                           if int(ann['ALLELE_NUM']) == i + 1]
                batch_cont['genes'].append(list({annotation['Gene']
                                                 for annotation in data['vep_annotations']
                                                 if annotation['Gene'][:4] == 'ENSG'}))
                batch_cont['transcripts'].append(list({annotation['Feature']
                                                       for annotation in data['vep_annotations']
                                                       if annotation['Feature'][:4] == 'ENST'}))

            data['hom_count'] = hom_counts[i] if hom_counts else None

            data['variant_id'] = '{}-{}-{}-{}'.format(data['chrom'],
                                                      data['pos'],
                                                      data['ref'],
                                                      data['alt'])
            data['quality_metrics'] = {x: info[x] for x in METRICS if x in info}
            batch_cont['batch'] += [data]
            if self.settings.count_calls:
                self._get_callcount(data)  # count calls (one per reference)
                self.counter['beaconvariants'] += 1  # count variants (one/alternate)

    def _insert_variants(self):
        """Import variants from a VCF file."""
        logging.info(f"Inserting variants{' (dry run)' if self.settings.dry_run else ''}")
        start = time.time()
        headers = [("chrom", str), ("pos", int), ("rsid", str), ("ref", str),
                   ("alt", str), ("site_quality", float), ("filter_string", str)]
        batch_container = {'batch': [],
                           'genes': [],
                           'transcripts': []}

        vep_field_names = None

        last_progress = -1.0
        counter = 0
        samples = 0

        references = dict(zip(('genes', 'transcripts'), self._get_genes_transcripts()))

        with db.database.atomic():
            for filename in self.settings.variant_file:
                for line in self._open(filename, binary=False):
                    line = line.strip()

                    if line.startswith("#"):
                        # Check for some information that we need
                        if line.startswith('##INFO=<ID=CSQ'):
                            vep_field_names = line.split('Format: ')[-1].strip('">').split('|')
                        if line.startswith('#CHROM'):
                            samples = len(line.split('\t')[9:])
                        continue

                    if not self.settings.beacon_only and not vep_field_names:
                        logging.error("VEP_field_names is empty. " +
                                      "Make sure VCF header is present.")
                        sys.exit(1)

                    self._parse_variant_row(line, batch_container, headers, vep_field_names)
                    counter += 1  # count variants (one per vcf row)

                    if len(batch_container['batch']) >= self.settings.batch_size:
                        if not self.settings.dry_run:
                            self._add_variants_to_db(batch_container['batch'],
                                                     batch_container['genes'],
                                                     batch_container['transcripts'],
                                                     references)

                        batch_container['genes'] = []
                        batch_container['transcripts'] = []
                        batch_container['batch'] = []
                        # Update progress
                        if self.counter['variants'] is not None:
                            last_progress = self._update_progress_bar(counter,
                                                                      self.counter['variants'],
                                                                      last_progress)

            if batch_container['batch'] and not self.settings.dry_run:
                self._add_variants_to_db(batch_container['batch'],
                                         batch_container['genes'],
                                         batch_container['transcripts'],
                                         references)

        if self.settings.set_vcf_sampleset_size and samples:
            self.sampleset.sample_size = samples
            self.sampleset.save()

        self.dataset_version.num_variants = counter
        self.dataset_version.save()
        if self.counter['variants'] is not None:
            last_progress = self._update_progress_bar(counter,
                                                      self.counter['variants'],
                                                      last_progress,
                                                      finished=True)

        self._log_insertion(counter, "variant", start)

    def _get_callcount(self, data):
        """Increment the call count by the calls found at this position."""
        if data['chrom'] == self.chrom and data['pos'] < self.lastpos:
            # If this position is smaller than the last, the file order might be invalid.
            # Give a warning, but keep on counting.
            msg = ("VCF file not ok, variants not given in incremental order." +
                   "Callcount may not be valid!\n\n")
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
        """Count the number of entries."""
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
            logging.info(f"Found {self.counter['coverage']:,} coverage lines")

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
        """Prepare for inserting data into db."""
        self._select_dataset_version()

    def start_import(self):
        """Start importing data."""
        self._set_dataset_info()
        if self.settings.add_mates:
            self._parse_manta()
            if self.settings.count_calls:
                logging.warning('Cannot count calls in the manta file. Skipping this...')
        elif self.settings.variant_file:
            self._insert_variants()
            if self.settings.count_calls:
                self._create_beacon_counts()
        if not self.settings.beacon_only and self.settings.coverage_file:
            self._insert_coverage()

    def _add_variant_genes(self, variant_indexes: list,
                           genes_to_add: list,
                           ref_genes: dict):
        """
        Add genes associated with the provided variants.

        Args:
            variant_indexes (list): dbids of the variants
            genes_to_add (list): the genes for each variant (str)
            ref_genes (dict): genename: dbid
        """
        batch = []
        for i in range(len(variant_indexes)):
            connected_genes = [{'variant': variant_indexes[i], 'gene': ref_genes[gene]}
                               for gene in genes_to_add[i]
                               if gene]
            batch += connected_genes
        if not self.settings.dry_run:
            db.VariantGenes.insert_many(batch).execute()

    def _add_variant_transcripts(self, variant_indexes: list,
                                 transcripts_to_add: list,
                                 ref_transcripts: dict):
        """
        Add transcripts associated with the provided variants.

        Args:
            variant_indexes (list): dbids of the variants
            transcripts_to_add (list): the transcripts for each variant (str)
            ref_transcripts (dict): genename: dbid
        """
        batch = []
        for i in range(len(variant_indexes)):
            connected_transcripts = [{'variant': variant_indexes[i],
                                      'transcript': ref_transcripts[transcript]}
                                     for transcript in transcripts_to_add[i]]
            batch += connected_transcripts
        if not self.settings.dry_run:
            db.VariantTranscripts.insert_many(batch).execute()

    @staticmethod
    def _is_non_chromosome(chrom):
        """
        Checks if this is a GL or MT.
        GL is an unplaced scaffold, MT is mitochondria.
        """
        return chrom.startswith('GL') or chrom.startswith('MT')

    def _log_insertion(self, counter, insertion_type, start):
        """Log the progress of the import."""
        action = "Inserted" if not self.settings.dry_run else "Dry-ran insertion of"
        logging.info("{} {} {} records in {}".format(action,
                                                     counter,
                                                     insertion_type,
                                                     self._time_since(start)))

    def _parse_baseinfo(self, header, line):
        """
        Parse the fixed columns of a vcf data line.

        Args:
              header (list): tuples of titles and converter functions for the colums of interest.
                  Ex ["chrom", str), ("pos", int)].
              line (str): a vcf line

        Returns:
            dict: the parsed info as specified by the header, plus the dataset_version.
        """
        base = {'dataset_version': self.dataset_version}
        line_info = line.split("\t")
        for i, (title, conv) in enumerate(header):
            base[title] = conv(line_info[i])
        return base

    def _parse_bnd_alleles(self, base, info):
        """Parse alleles of a structural variant (BND) in a manta file."""
        batch = []
        for alt in base['alt'].split(","):
            data = dict(base)
            data['allele_freq'] = float(info.get('FRQ'))
            data['alt'], data['mate_chrom'], data['mate_start'] = \
                    re.search(r'(.+)[[\]](.*?):(\d+)[[\]]', alt).groups()
            if self._is_non_chromosome(data['mate_chrom']):
                # A BND from a chromosome to a non-chromosome.
                # TODO ask a bioinformatician if these cases should be included or not   # pylint: disable=fixme
                continue
            data['mate_id'] = info.get('MATEID', '')
            data['variant_id'] = '{}-{}-{}-{}'.format(data['chrom'],
                                                      data['pos'],
                                                      data['ref'],
                                                      alt)
            # Note: these two fields are not present in our data, will always default to 0.
            # Set to 0 rather than None, as the type should be int (according to the Beacon
            # API specificition).
            data['allele_count'] = info.get('AC', 0)
            data['allele_num'] = info.get('AN', 0)

            batch += [data]
            if self.settings.add_reversed_mates:
                # If the vcf only contains one line per breakend,
                # add the reversed version to the database here.
                reversed_mates = dict(data)
                # Note: in general, ref and alt cannot be assumed to be the same in the
                # reversed direction, but our data (so far) only contains N, so we just
                # keep them as is for now.
                reversed_mates.update({'mate_chrom': data['chrom'],
                                       'chrom': data['mate_chrom'],
                                       'mate_start': data['pos'],
                                       'pos': data['mate_start'],
                                       'chrom_id': data['mate_id'],
                                       'mate_id': data['chrom_id']})
                reversed_mates['variant_id'] = '{}-{}-{}-{}'.format(reversed_mates['chrom'],
                                                                    reversed_mates['pos'],
                                                                    reversed_mates['ref'],
                                                                    alt)
                batch += [reversed_mates]

        return batch

    @staticmethod
    def _parse_info(line):
        """Parse the INFO field of a vcf line."""
        parts = re.split(r';(?=\w)', line.split('\t')[7])
        return {x[0]: x[1] for x in map(lambda s: s.split('=', 1) if '=' in s else (s, s), parts)}
