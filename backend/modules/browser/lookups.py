import json # remove when db is fixed
import logging
import re

import db

from . import utils

SEARCH_LIMIT = 10000


def add_rsid_to_variant(dataset:str, variant:str):
    """
    Add rsid to a variant in the database based on position

    Args:
        dataset (str): short name of the dataset
        variant (dict): values for a variant
    """
    refset = (db.Dataset
              .select(db.ReferenceSet)
              .join(db.ReferenceSet)
              .where(db.Dataset.short_name == dataset)
              .dicts()
              .get())
    dbsnp_version = refset['dbsnp_version']

    if not variant['rsid']:
        try:
            rsid = (db.DbSNP
                    .select()
                    .where((db.DbSNP.pos == variant['pos']) &
                           (db.DbSNP.chrom == variant['chrom']) &
                           (db.DbSNP.version == dbsnp_version))
                    .dicts()
                    .get())
            variant['rsid'] = 'rs{}'.format(rsid['rsid'])
        except db.DbSNP.DoesNotExist:
            pass
            # logging.error('add_rsid_to_variant({}, variant[dbid: {}]): unable to retrieve rsid'.format(dataset, variant['id']))


REGION_REGEX = re.compile(r'^\s*(\d+|X|Y|M|MT)\s*([-:]?)\s*(\d*)-?([\dACTG]*)-?([ACTG]*)')

def get_awesomebar_result(dataset:str, query:str, ds_version:str=None):
    """
    Parse the search input

    Datatype is one of:
    - 'gene'
    - 'transcript'
    - 'variant'
    - 'dbsnp_variant_set'
    - 'region'

    Identifier is one of:
    - ensembl ID for gene
    - variant ID string for variant (eg. 1-1000-A-T)
    - region ID string for region (eg. 1-1000-2000)

    Follow these steps:
    - if query is an ensembl ID, return it
    - if a gene symbol, return that gene's ensembl ID
    - if an RSID, return that variant's string

    Args:
        dataset (str): short name of dataset
        query (str): the search query
        ds_version (str): the dataset version

    Returns:
        tuple: (datatype, identifier)
    """
    query = query.strip()

    # Parse Variant types
    variant = get_variants_by_rsid(dataset, query.lower(), ds_version=ds_version)
    if not variant:
        variant = get_variants_by_rsid(dataset, query.lower(), check_position=True, ds_version=ds_version)

    if variant:
        if len(variant) == 1:
            retval = ('variant', variant[0]['variant_id'])
        else:
            retval = ('dbsnp_variant_set', variant[0]['rsid'])
        return retval

    gene = get_gene_by_name(dataset, query)
    # From here out, all should be uppercase (gene, tx, region, variant_id)
    query = query.upper()
    if not gene:
        gene = get_gene_by_name(dataset, query)
    if gene:
        return 'gene', gene['gene_id']

    # Ensembl formatted queries
    if query.startswith('ENS'):
        # Gene
        gene = get_gene(dataset, query)
        if gene:
            return 'gene', gene['gene_id']

        # Transcript
        transcript = get_transcript(dataset, query)
        if transcript:
            return 'transcript', transcript['transcript_id']

    # Region and variant queries
    query = query[3:] if query.startswith('CHR') else query

    match = REGION_REGEX.match(query)
    if match:
        target = match.group(0)
        target_type = 'region'
        if match.group(2) == ":":
            target = target.replace(":","-")
        if match.group(5) and set(match.group(4)).issubset(set("ACGT")):
            target_type = 'variant'

        return target_type, target

    return 'not_found', query


def get_coverage_for_bases(dataset:str, chrom:str, start_pos:int, end_pos:int=None, ds_version:str=None):
    """
    Get the coverage for the list of bases given by start_pos->end_pos, inclusive

    Args:
        dataset (str): short name for the dataset
        chrom (str): chromosome
        start_pos (int): first position of interest
        end_pos (int): last position of interest; if None it will be set to start_pos
        ds_version (str): version of the dataset

    Returns:
        list: coverage dicts for the region of interest. None if failed
    """
    dataset_version = db.get_dataset_version(dataset, ds_version)
    if not dataset_version:
        return None

    if end_pos is None:
        end_pos = start_pos
    return [values for values in (db.Coverage
                                  .select()
                                  .where((db.Coverage.pos >= start_pos) &
                                         (db.Coverage.pos <= end_pos) &
                                         (db.Coverage.chrom == chrom) &
                                         (db.Coverage.dataset_version == dataset_version.id))
                                  .dicts())]


def get_coverage_for_transcript(dataset:str, chrom:str, start_pos:int, end_pos:int=None, ds_version:str=None):
    """
    Get the coverage for the list of bases given by start_pos->end_pos, inclusive

    Args:
        dataset (str): short name for the dataset
        chrom (str): chromosome
        start_pos (int): first position of interest
        end_pos (int): last position of interest; if None it will be set to start_pos
        ds_version (str): version of the dataset

    Returns:
        list: coverage dicts for the region of interest
    """
    # Is this function still relevant with postgres?
    # Only entries with reported cov are in database
    coverage_array = get_coverage_for_bases(dataset, chrom, start_pos, end_pos, ds_version)
    # only return coverages that have coverage (if that makes any sense?)
    # return coverage_array
    if not coverage_array:
        return None
    covered = [c for c in coverage_array if c['mean']]
    return covered


def get_exons_in_transcript(dataset:str, transcript_id:str):
    """
    Retrieve exons associated with the given transcript id

    Args:
        dataset (str): short name of the dataset
        transcript_id (str): the id of the transcript

    Returns:
        list: dicts with values for each exon sorted by start position
    """
    ref_dbid = db.get_reference_dbid_dataset(dataset)
    if not ref_dbid:
        logging.error('get_exons_in_transcript({}, {}): unable to find dataset dbid'.format(dataset, transcript_id))
        return None
    try:
        transcript = (db.Transcript
                      .select()
                      .join(db.Gene)
                      .where((db.Transcript.transcript_id == transcript_id) &
                             (db.Gene.reference_set == ref_dbid))
                      .get())
    except db.Transcript.DoesNotExist:
        logging.error('get_exons_in_transcript({}, {}): unable to retrieve transcript'.format(dataset, transcript_id))
        return None
    wanted_types = ('CDS', 'UTR', 'exon')
    return sorted(list(db.Feature.select().where((db.Feature.transcript == transcript) &
                                                 (db.Feature.feature_type in wanted_types)).dicts()),
                  key=lambda k: k['start'])


def get_gene(dataset:str, gene_id:str):
    """
    Retrieve gene by gene id

    Args:
        dataset (str): short name of the dataset
        gene_id (str): the id of the gene

    Returns:
        dict: values for the gene; empty if not found
    """
    ref_dbid = db.get_reference_dbid_dataset(dataset)
    if not ref_dbid:
        return {}
    try:
        return db.Gene.select().where((db.Gene.gene_id == gene_id) &
                                      (db.Gene.reference_set == ref_dbid)).dicts().get()
    except db.Gene.DoesNotExist:
        return {}


def get_gene_by_dbid(gene_dbid:str):
    """
    Retrieve gene by gene database id

    Args:
        gene_dbid (str): the database id of the gene

    Returns:
        dict: values for the gene; empty if not found
    """
    try:
        return db.Gene.select().where(db.Gene.id == gene_dbid).dicts().get()
    except db.Gene.DoesNotExist:
        return {}
    except ValueError:
        return {}


def get_gene_by_name(dataset:str, gene_name:str):
    """
    Retrieve gene by gene_name.
    First checks gene_name, then other_names.

    Args:
        gene_name (str): the id of the gene

    Returns:
        dict: values for the gene; empty if not found
    """
    ref_dbid = db.get_reference_dbid_dataset(dataset)
    if not ref_dbid:
        return {}
    try:
        return (db.Gene.select()
                .where((db.Gene.reference_set == ref_dbid) &
                       (db.Gene.name==gene_name))
                .dicts()
                .get())
    except db.Gene.DoesNotExist:
        try:
            return (db.GeneOtherNames.select(db.Gene)
                    .join(db.Gene)
                    .where((db.GeneOtherNames.name == gene_name) &
                           (db.Gene.reference_set == ref_dbid))
                    .dicts()
                    .get())
        except db.GeneOtherNames.DoesNotExist:
            logging.error('get_gene_by_name({}, {}): unable to retrieve gene'.format(dataset, gene_name))
            return {}


def get_genes_in_region(dataset:str, chrom:str, start_pos:int, stop_pos:int):
    """
    Retrieve genes located within a region

    Args:
        dataset (str): short name of the dataset
        chrom (str): chromosome name
        start_pos (int): start of region
        stop_pos (int): end of region

    Returns:
        dict: values for the gene; empty if not found
    """
    ref_dbid = db.get_reference_dbid_dataset(dataset)
    if not ref_dbid:
        return {}

    gene_query = db.Gene.select().where((db.Gene.reference_set == ref_dbid) &
                                        ((((db.Gene.start >= start_pos) &
                                           (db.Gene.start <= stop_pos)) |
                                          ((db.Gene.stop >= start_pos) &
                                           (db.Gene.stop <= stop_pos))) &
                                         (db.Gene.chrom == chrom))).dicts()
    return [gene for gene in gene_query]


def get_number_of_variants_in_transcript(dataset:str, transcript_id:str, ds_version:str=None):
    """
    Get the total and filtered amount of variants in a transcript

    Args:
        dataset (str): short name of the dataset
        transcript_id (str): id of the transcript
        ds_version (str): version of the dataset

    Returns:
        dict: {filtered: nr_filtered, total: nr_total}, None if error
    """
    dataset_version = db.get_dataset_version(dataset, ds_version)
    if not dataset_version:
        return None

    variants = get_variants_in_transcript(dataset, transcript_id)
    if not variants:
        return None
    total = len(variants)
    filtered = len(tuple(variant for variant in variants if variant['filter_string'] == 'PASS'))
    return {'filtered': filtered, 'total': total}


def get_raw_variant(dataset:str, pos:int, chrom:str, ref:str, alt:str, ds_version:str=None):
    """
    Retrieve variant by position and change

    Args:
        dataset (str): short name of the reference set
        pos (int): position of the variant
        chrom (str): name of the chromosome
        ref (str): reference sequence
        alt (str): variant sequence
        ds_version (str): dataset version

    Returns:
        dict: values for the variant; None if not found
    """
    dataset_version = db.get_dataset_version(dataset, ds_version)
    if not dataset_version:
        return None

    try:
        variant = (db.Variant
                   .select()
                   .where((db.Variant.pos == pos) &
                          (db.Variant.ref == ref) &
                          (db.Variant.alt == alt) &
                          (db.Variant.chrom == chrom) &
                          (db.Variant.dataset_version == dataset_version.id))
                   .dicts()
                   .get())
        variant['genes'] = [gene for gene in
                            db.VariantGenes.select(db.VariantGenes.gene)
                            .where(db.VariantGenes.variant == variant['id'])
                            .dicts()]
        variant['transcripts'] = [transcript for transcript in
                                  db.VariantTranscripts.select(db.VariantTranscripts.transcript)
                                  .where(db.VariantTranscripts.variant == variant['id'])
                                  .dicts()]
        return variant
    except db.Variant.DoesNotExist:
        logging.error('get_raw_variant({}, {}, {}, {}, {}, {}): unable to retrieve variant'
                      .format(dataset, pos, chrom, ref, alt, dataset_version.id))
        return None


def get_transcript(dataset:str, transcript_id:str):
    """
    Retrieve transcript by transcript id
    Also includes exons as ['exons']

    Args:
        dataset (str): short name of the dataset
        transcript_id (str): the id of the transcript

    Returns:
        dict: values for the transcript, including exons; empty if not found
    """
    ref_dbid = db.get_reference_dbid_dataset(dataset)
    try:
        transcript = (db.Transcript
                      .select()
                      .join(db.Gene)
                      .where((db.Transcript.transcript_id == transcript_id) &
                             (db.Gene.reference_set == ref_dbid))
                      .dicts()
                      .get())
        transcript['exons'] = get_exons_in_transcript(dataset, transcript_id)
        return transcript
    except db.Transcript.DoesNotExist:
        return {}


def get_transcripts_in_gene(dataset:str, gene_id:str):
    """
    Get the transcripts associated with a gene
    Args:
        dataset (str): short name of the reference set
        gene_id (str): id of the gene
    Returns:
        list: transcripts (dict) associated with the gene; empty if no hits
    """
    ref_dbid = db.get_reference_dbid_dataset(dataset)
    if not ref_dbid:
        logging.error('get_transcripts_in_gene({}, {}): unable to get referenceset dbid'.format(dataset, gene_id))
        return []
    try:
        gene = db.Gene.select().where((db.Gene.reference_set == ref_dbid) &
                                      (db.Gene.gene_id == gene_id)).dicts().get()
    except db.Gene.DoesNotExist:
        logging.error('get_transcripts_in_gene({}, {}): unable to retrieve gene'.format(dataset, gene_id))
        return []

    return [transcript for transcript in db.Transcript.select().where(db.Transcript.gene == gene['id']).dicts()]


def get_transcripts_in_gene_by_dbid(gene_dbid:int):
    """
    Get the transcripts associated with a gene
    Args:
        gene_dbid (int): database id of the gene
    Returns:
        list: transcripts (dict) associated with the gene; empty if no hits
    """
    return [transcript for transcript in db.Transcript.select().where(db.Transcript.gene == gene_dbid).dicts()]


def get_variant(dataset:str, pos:int, chrom:str, ref:str, alt:str, ds_version:str=None):
    """
    Retrieve variant by position and change
    Retrieves rsid from db (if available) if not present in variant

    Args:
        dataset (str): short name of the dataset
        pos (int): position of the variant
        chrom (str): name of the chromosome
        ref (str): reference sequence
        alt (str): variant sequence
        ds_version (str): version of the dataset

    Returns:
        dict: values for the variant; None if not found
    """
    variant = get_raw_variant(dataset, pos, chrom, ref, alt, ds_version)
    if not variant or 'rsid' not in variant:
        return variant
    if variant['rsid'] == '.' or variant['rsid'] is None:
        add_rsid_to_variant(dataset, variant)
    else:
        if not str(variant['rsid']).startswith('rs'):
            variant['rsid'] = 'rs{}'.format(variant['rsid'])
    return variant


def get_variants_by_rsid(dataset:str, rsid:str, check_position:str=False, ds_version:str=None):
    """
    Retrieve variants by their associated rsid
    May also look up rsid and search for variants at the position

    Args:
        dataset (str): short name of dataset
        rsid (str): rsid of the variant (starting with rs)
        check_position (bool): check for variants at the position of the rsid instead of by rsid
        ds_version (str): version of the dataset

    Returns:
        list: variants as dict; no hits returns None
    """
    dataset_version = db.get_dataset_version(dataset, ds_version)
    if not dataset_version:
        return None

    if not rsid.startswith('rs'):
        logging.error('get_variants_by_rsid({}, {}): rsid not starting with rs'.format(dataset, rsid))
        return None

    try:
        rsid = int(rsid.lstrip('rs'))
    except ValueError:
        logging.error('get_variants_by_rsid({}, {}): not an integer after rs'.format(dataset, rsid))
        return None
    if check_position:
        refset = (db.Dataset
                  .select(db.ReferenceSet)
                  .join(db.ReferenceSet)
                  .where(db.Dataset.short_name == dataset)
                  .dicts()
                  .get())
        dbsnp_version = refset['dbsnp_version']

        rsid_dbsnp = (db.DbSNP
                     .select()
                     .where((db.DbSNP.rsid == rsid) &
                            (db.DbSNP.version_id == dbsnp_version) )
                     .dicts()
                     .get())
        query = (db.Variant
                 .select()
                 .where((db.Variant.pos == rsid_dbsnp['pos']) &
                        (db.Variant.chrom == rsid_dbsnp['chrom']) &
                        (db.Variant.dataset_version == dataset_version))
                 .dicts())
    else:
        query = (db.Variant
                 .select()
                 .where((db.Variant.rsid == rsid) &
                        (db.Variant.dataset_version == dataset_version))
                 .dicts())

    variants = [variant for variant in query]
    # add_consequence_to_variants(variants)
    return variants


def get_variants_in_gene(dataset:str, gene_id:str, ds_version:str=None):
    """
    Retrieve variants present inside a gene

    Args:
        dataset (str): short name of the dataset
        gene_id (str): id of the gene
        ds_version (str): version of the dataset

    Returns:
        list: values for the variants
    """
    ref_dbid = db.get_reference_dbid_dataset(dataset)
    if not ref_dbid:
        return None
    dataset_version = db.get_dataset_version(dataset, ds_version)
    if not dataset_version:
        return None

    gene = get_gene(dataset, gene_id)

    variants = [variant for variant in db.Variant.select()
                                                 .join(db.VariantGenes)
                                                 .where((db.VariantGenes.gene == gene['id']) &
                                                        (db.Variant.dataset_version == dataset_version)).dicts()]
    ##### remove when db is fixed
    for variant in variants:
        variant['hom_count'] = 0
        variant['filter'] = variant['filter_string']
    #####

    utils.add_consequence_to_variants(variants)
    for variant in variants:
        if variant['rsid']:
            variant['rsid'] = 'rs{}'.format(variant['rsid'])
        else:
            add_rsid_to_variant(dataset, variant)
        remove_extraneous_information(variant)
    return variants


def get_variants_in_region(dataset:str, chrom:str, start_pos:int, end_pos:int, ds_version:str=None):
    """
    Variants that overlap a region

    Args:
        dataset (str): short name of the dataset
        chrom (str): name of the chromosom
        start_pos (int): start of the region
        end_pos (int): start of the region
        ds_version (str): version of the dataset

    Returns:
        list: variant dicts, None if no hits
    """
    dataset_version = db.get_dataset_version(dataset, ds_version)
    if not dataset_version:
        return None
    query = (db.Variant
             .select()
             .where((db.Variant.pos >= start_pos) &
                    (db.Variant.pos <= end_pos) &
                    (db.Variant.chrom == chrom) &
                    (db.Variant.dataset_version == dataset_version))
             .dicts())

    variants = [variant for variant in query]

    ##### remove when db is fixed
    for variant in variants:
        variant['hom_count'] = 0
        variant['filter'] = variant['filter_string']
    #####

    utils.add_consequence_to_variants(variants)
    for variant in variants:
        if variant['rsid']:
            variant['rsid'] = 'rs{}'.format(variant['rsid'])
        else:
            add_rsid_to_variant(dataset, variant)
        remove_extraneous_information(variant)
    return variants


def get_variants_in_transcript(dataset:str, transcript_id:str, ds_version:str=None):
    """
    Retrieve variants inside a transcript

    Args:
        dataset (str): short name of the dataset
        transcript_id (str): id of the transcript (ENST)
        ds_version (str): version of the dataset

    Returns:
        dict: values for the variant; None if not found
    """
    ref_dbid = db.get_reference_dbid_dataset(dataset)
    if not ref_dbid:
        return None
    dataset_version = db.get_dataset_version(dataset, ds_version)
    if not dataset_version:
        return None

    transcript = get_transcript(dataset, transcript_id)

    variants = [variant for variant in db.Variant.select()
                .join(db.VariantTranscripts)
                .where((db.VariantTranscripts.transcript == transcript['id']) &
                       (db.Variant.dataset_version == dataset_version))
                .dicts()]

    ##### remove when db is fixed
    for variant in variants:
        variant['hom_count'] = 0
        variant['filter'] = variant['filter_string']
    #####

    utils.add_consequence_to_variants(variants)
    for variant in variants:
        variant['vep_annotations'] = [anno for anno in variant['vep_annotations'] if anno['Feature'] == transcript_id]
        if variant['rsid']:
            variant['rsid'] = 'rs{}'.format(variant['rsid'])
        else:
            add_rsid_to_variant(dataset, variant)
        remove_extraneous_information(variant)
    return variants


def remove_extraneous_information(variant):
    #del variant['genotype_depths']
    #del variant['genotype_qualities']
#    del variant['transcripts']
#    del variant['genes']
    del variant['orig_alt_alleles']
    del variant['site_quality']
    del variant['vep_annotations']
