import re
import db

#from .utils import METRICS, AF_BUCKETS, get_xpos, xpos_to_pos, add_consequence_to_variants, add_consequence_to_variant

SEARCH_LIMIT = 10000


def get_coverage_for_bases(chrom, start_pos, stop_pos=None):
    """
    Get the coverage for the list of bases given by start_pos->xstop_pos, inclusive
    Args:
        chrom (str): chromosome
        start_pos (int): first position of interest
        end_pos (int): last position of interest; if None it will be set to start_pos
    Returns:
        list: coverage dicts for the region of interest
    """
    if stop_pos is None:
        stop_pos = start_pos

    return [values for values in db.Coverage.select().where((db.Coverage.pos >= start_pos) &
                                                            (db.Coverage.pos <= stop_pos) &
                                                            (db.Coverage.chrom == chrom)).dicts()]


def get_coverage_for_transcript(chrom, start_pos, stop_pos=None):
    """
    Get the coverage for the list of bases given by start_pos->xstop_pos, inclusive
    Args:
        chrom (str): chromosome
        start_pos (int): first position of interest
        end_pos (int): last position of interest; if None it will be set to start_pos
    Returns:
        list: coverage dicts for the region of interest
    """
    # Is this function no longer relevant with postgres?
    # Only entries with reported cov are in database
    coverage_array = get_coverage_for_bases(chrom, start_pos, stop_pos)
    # only return coverages that have coverage (if that makes any sense?)
    # return coverage_array
    covered = [c for c in coverage_array if c['mean']]
    return covered


def get_exons_in_transcript(transcript_dbid):
    """
    Retrieve exons associated with the given transcript id
    Args:
        transcript_dbid: the id of the transcript in the database (Transcript.id; not transcript_id)
    Returns:
        list: dicts with values for each exon sorted by start position
    """
    return sorted(list(db.Feature.select().where(db.Feature.transcript==transcript_dbid).dicts()), key=lambda k: k['start'])


def get_gene(gene_id):
    """
    Retrieve gene by gene id
    Args:
        gene_id (str): the id of the gene
    Returns:
        dict: values for the gene; empty if not found
    """
    try:
        return db.Gene.select().where(db.Gene.gene_id==gene_id).dicts().get()
    except db.Gene.DoesNotExist:
        return {}


def get_gene_by_name(gene_name):
    """
    Retrieve gene by gene_name.
    First checks gene_name, then other_names.
    Args:
        gene_name (str): the id of the gene
    Returns:
        dict: values for the gene; empty if not found
    """
    # try gene_name field first
    try:
        return db.Gene.select().where(db.Gene.name==gene_name).dicts().get()
    except db.Gene.DoesNotExist:
        try:
            # troubles with KeyError
            return db.Gene.select().where(db.Gene.other_names.contains(gene_name)).dicts().get()
        except db.Gene.DoesNotExist:
            return {}


def get_transcript(transcript_id):
    """
    Retrieve transcript by transcript id
    Also includes exons as ['exons']
    Args:
        transcript_id (str): the id of the transcript
    Returns:
        dict: values for the transcript, including exons; empty if not found
    """
    try:
        transcript = db.Transcript.select().where(db.Transcript.transcript_id==transcript_id).dicts().get()
        transcript['exons'] = get_exons_in_transcript(transcript['id'])
        return transcript
    except db.Transcript.DoesNotExist:
        return {}


def get_raw_variant(pos, chrom, ref, alt):
    """
    Retrieve variant by position and change
    Args:
        pos (int): position of the variant
        chrom (str): name of the chromosome
        ref (str): reference sequence
        ref (str): variant sequence
    Returns:
        dict: values for the variant; empty if not found
    """
    try:
        return db.Variant.select().where((db.Variant.pos == pos) &
                                         (db.Variant.ref == ref) &
                                         (db.Variant.alt == alt) &
                                         (db.Variant.chrom == chrom)).dicts().get()
    except db.Variant.DoesNotExist:
        return {}


def get_variant(pos, chrom, ref, alt):
    """
    Retrieve variant by position and change
    Retrieves rsid from db (if available) if not present in variant
    Args:
        pos (int): position of the variant
        chrom (str): name of the chromosome
        ref (str): reference sequence
        ref (str): variant sequence
    Returns:
        dict: values for the variant; empty if not found
    """
    try:
        variant = get_raw_variant(pos, chrom, ref, alt)
        if not variant or 'rsid' not in variant:
            return variant
        if variant['rsid'] == '.' or variant['rsid'] is None:
            rsid = db.DbSNP.select().where((db.DbSNP.pos==pos) &
                                           (db.DbSNP.chrom==chrom)).dicts().get()
            if rsid:
                variant['rsid'] = 'rs{}'.format(rsid['rsid'])
        return variant
    except db.Variant.DoesNotExist:
        return {}


def get_variants_in_transcript(transcript_id):
    """
    Retrieve variants inside a transcript
    Args:
        pos (int): position of the variant
        chrom (str): name of the chromosome
        ref (str): reference sequence
        ref (str): variant sequence
    Returns:
        dict: values for the variant; empty if not found
    """
    variants = []
    for variant in db.Variant.select().where(db.Variant.transcripts.contains(transcript_id)).dicts():
        variants.append(variant)
    return variants
    variant['vep_annotations'] = [x for x in variant['vep_annotations'] if x['Feature'] == transcript_id]
    add_consequence_to_variant(variant)
    remove_extraneous_information(variant)
    variants.append(variant)
    return variants


REGION_REGEX = re.compile(r'^\s*(\d+|X|Y|M|MT)\s*([-:]?)\s*(\d*)-?([\dACTG]*)-?([ACTG]*)')

def get_awesomebar_result(db,sdb, query):
    """
    Similar to the above, but this is after a user types enter
    We need to figure out what they meant - could be gene, variant, region

    Return tuple of (datatype, identifier)
    Where datatype is one of 'gene', 'variant', or 'region'
    And identifier is one of:
    - ensembl ID for gene
    - variant ID string for variant (eg. 1-1000-A-T)
    - region ID string for region (eg. 1-1000-2000)

    Follow these steps:
    - if query is an ensembl ID, return it
    - if a gene symbol, return that gene's ensembl ID
    - if an RSID, return that variant's string


    Finally, note that we don't return the whole object here - only it's identifier.
    This could be important for performance later

    """
    query = query.strip()

    # Parse Variant types
    variant = get_variants_by_rsid(db, query.lower())
    if not variant:
        variant = get_variants_from_dbsnp(db,sdb, query.lower())

    if variant:
        if len(variant) == 1:
            retval = ('variant', variant[0]['variant_id'])
        else:
            retval = ('dbsnp_variant_set', variant[0]['rsid'])
        return retval

    gene = get_gene_by_name(sdb, query)
    # From here out, all should be uppercase (gene, tx, region, variant_id)
    query = query.upper()
    if not gene:
        gene = get_gene_by_name(sdb, query)
    if gene:
        return 'gene', gene['gene_id']

    # Ensembl formatted queries
    if query.startswith('ENS'):
        # Gene
        gene = get_gene(sdb, query)
        if gene:
            return 'gene', gene['gene_id']

        # Transcript
        transcript = get_transcript(sdb, query)
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


def get_genes_in_region(sdb, chrom, start, stop):
    """
    Genes that overlap a region
    """
    xstart = get_xpos(chrom, start)
    xstop = get_xpos(chrom, stop)
    genes = sdb.genes.find({
        'xstart': {'$lte': xstop},
        'xstop': {'$gte': xstart},
    }, projection={'_id': False})
    return list(genes)


def get_variants_in_region(db, sdb, chrom, start, stop):
    """
    Variants that overlap a region
    Unclear if this will include CNVs
    """
    xstart = get_xpos(chrom, start)
    xstop = get_xpos(chrom, stop)
    variants = list(db.variants.find({
        'xpos': {'$lte': xstop, '$gte': xstart}
    }, projection={'_id': False}, limit=SEARCH_LIMIT))
    add_consequence_to_variants(variants)
    for variant in variants:
        add_rsid_to_variant(sdb, variant)
        remove_extraneous_information(variant)
    return list(variants)


def get_metrics(db, variant):
    if 'allele_count' not in variant or variant['allele_num'] == 0:
        return None
    metrics = {}
    for metric in METRICS:
        metrics[metric] = db.metrics.find_one({'metric': metric}, projection={'_id': False})

    metric = None
    if variant['allele_count'] == 1:
        metric = 'singleton'
    elif variant['allele_count'] == 2:
        metric = 'doubleton'
    else:
        for af in AF_BUCKETS:
            if float(variant['allele_count'])/variant['allele_num'] < af:
                metric = af
                break
    if metric is not None:
        metrics['Site Quality'] = db.metrics.find_one({'metric': 'binned_%s' % metric}, projection={'_id': False})
    return metrics


def remove_extraneous_information(variant):
    #del variant['genotype_depths']
    #del variant['genotype_qualities']
    del variant['transcripts']
    del variant['genes']
    del variant['orig_alt_alleles']
    del variant['xpos']
    del variant['xstart']
    del variant['xstop']
    del variant['site_quality']
    del variant['vep_annotations']


def get_variants_in_gene(db, sdb, gene_id):
    variants = []
    for variant in db.variants.find({'genes': gene_id}, projection={'_id': False}):
        variant['vep_annotations'] = [x for x in variant['vep_annotations'] if x['Gene'] == gene_id]
        add_rsid_to_variant(sdb, variant)
        add_consequence_to_variant(variant)
        remove_extraneous_information(variant)
        variants.append(variant)
    return variants


def get_transcripts_in_gene(sdb, gene_id):
    return list(sdb.transcripts.find({'gene_id': gene_id}, projection={'_id': False}))


def get_number_of_variants_in_transcript(db, transcript_id):
    total = db.variants.count({'transcripts': transcript_id})
    filtered = db.variants.count({'transcripts': transcript_id, 'filter': 'PASS'})
    return {'filtered': filtered, 'total': total}
