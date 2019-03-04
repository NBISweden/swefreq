import logging

from . import lookups

AF_BUCKETS = [0.0001, 0.0002, 0.0005, 0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1]

CHROMOSOMES = ['chr%s' % x for x in range(1, 23)]
CHROMOSOMES.extend(['chrX', 'chrY', 'chrM'])
CHROMOSOME_TO_CODE = { item: i+1 for i, item in enumerate(CHROMOSOMES) }

# Note that this is the current as of v81 with some included for backwards compatibility (VEP <= 75)

CSQ_ORDER = ["transcript_ablation",
"splice_acceptor_variant",
"splice_donor_variant",
"stop_gained",
"frameshift_variant",
"stop_lost",
"start_lost",  # new in v81
"initiator_codon_variant",  # deprecated
"transcript_amplification",
"inframe_insertion",
"inframe_deletion",
"missense_variant",
"protein_altering_variant",  # new in v79
"splice_region_variant",
"incomplete_terminal_codon_variant",
"stop_retained_variant",
"synonymous_variant",
"coding_sequence_variant",
"mature_miRNA_variant",
"5_prime_UTR_variant",
"3_prime_UTR_variant",
"non_coding_transcript_exon_variant",
"non_coding_exon_variant",  # deprecated
"intron_variant",
"NMD_transcript_variant",
"non_coding_transcript_variant",
"nc_transcript_variant",  # deprecated
"upstream_gene_variant",
"downstream_gene_variant",
"TFBS_ablation",
"TFBS_amplification",
"TF_binding_site_variant",
"regulatory_region_ablation",
"regulatory_region_amplification",
"feature_elongation",
"regulatory_region_variant",
"feature_truncation",
"intergenic_variant",
""]

CSQ_ORDER_DICT = {csq:i for i,csq in enumerate(CSQ_ORDER)}
REV_CSQ_ORDER_DICT = dict(enumerate(CSQ_ORDER))

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

PROTEIN_LETTERS_1TO3 = {
    'A': 'Ala', 'C': 'Cys', 'D': 'Asp', 'E': 'Glu',
    'F': 'Phe', 'G': 'Gly', 'H': 'His', 'I': 'Ile',
    'K': 'Lys', 'L': 'Leu', 'M': 'Met', 'N': 'Asn',
    'P': 'Pro', 'Q': 'Gln', 'R': 'Arg', 'S': 'Ser',
    'T': 'Thr', 'V': 'Val', 'W': 'Trp', 'Y': 'Tyr',
    'X': 'Ter', '*': 'Ter', 'U': 'Sec'
}


def add_consequence_to_variants(variant_list:list):
    """
    Add information about variant consequence to multiple variants

    Args:
        variant_list (list): list of variants
    """
    for variant in variant_list:
        add_consequence_to_variant(variant)


def add_consequence_to_variant(variant:dict):
    """
    Add information about variant consequence to a variant

    Args:
        variant (dict): variant information
    """
    if not variant:
        return
    worst_csq = worst_csq_with_vep(variant['vep_annotations'])
    variant['major_consequence'] = ''
    if worst_csq is None:
        return

    variant['major_consequence'] = worst_csq['major_consequence']
    variant['HGVSp'] = get_protein_hgvs(worst_csq)
    variant['HGVSc'] = get_transcript_hgvs(worst_csq)
    variant['HGVS'] = get_proper_hgvs(worst_csq)
    variant['CANONICAL'] = worst_csq['CANONICAL']

    if CSQ_ORDER_DICT[variant['major_consequence']] <= CSQ_ORDER_DICT["frameshift_variant"]:
        variant['category'] = 'lof_variant'
        for annotation in variant['vep_annotations']:
            if annotation['LoF'] == '':
                annotation['LoF'] = 'NC'
                annotation['LoF_filter'] = 'Non-protein-coding gene'
    elif CSQ_ORDER_DICT[variant['major_consequence']] <= CSQ_ORDER_DICT["missense_variant"]:
        # Should be noted that this grabs inframe deletion, etc.
        variant['category'] = 'missense_variant'
    elif CSQ_ORDER_DICT[variant['major_consequence']] <= CSQ_ORDER_DICT["synonymous_variant"]:
        variant['category'] = 'synonymous_variant'
    else:
        variant['category'] = 'other_variant'
    variant['flags'] = get_flags_from_variant(variant)


def annotation_severity(annotation:dict):
    """
    Evaluate severity of the consequences; "bigger is more important".

    Args:
        annotation (dict): vep_annotation from a variant

    Returns:
        float: severity score
    """
    rv = -CSQ_ORDER_DICT[worst_csq_from_csq(annotation['Consequence'])]
    if annotation['CANONICAL'] == 'YES':
        rv += 0.1
    return rv


def get_coverage(dataset:str, datatype:str, item:str, ds_version:str=None):
    """
    Retrieve coverage for a gene/region/transcript

    Args:
        dataset (str): short name of the dataset
        datatype (str): type of "region" (gene/region/transcript)
        item (str): the datatype item to look up
        ds_version (str): the dataset version

    Returns:
        dict: start, stop, coverage list
    """
    ret = {'coverage':[]}

    if datatype == 'gene':
        gene = lookups.get_gene(dataset, item)
        if gene:
            transcript = lookups.get_transcript(dataset, gene['canonical_transcript'])
            if transcript:
                start = transcript['start'] - EXON_PADDING
                stop  = transcript['stop'] + EXON_PADDING
                ret['coverage'] = lookups.get_coverage_for_transcript(dataset, transcript['chrom'], start, stop, ds_version)
    elif datatype == 'region':
        chrom, start, stop = item.split('-')
        start = int(start)
        stop = int(stop)

        if is_region_too_large(start, stop):
            return {'coverage': [], 'region_too_large': True}

        ret['coverage'] = lookups.get_coverage_for_bases(dataset, chrom, start, stop, ds_version)
    elif datatype == 'transcript':
        transcript = lookups.get_transcript(dataset, item)
        if transcript:
            start = transcript['start'] - EXON_PADDING
            stop  = transcript['stop'] + EXON_PADDING
            ret['coverage'] = lookups.get_coverage_for_transcript(dataset, transcript['chrom'], start, stop, ds_version)
    return ret


def get_coverage_pos(dataset:str, datatype:str, item:str):
    """
    Retrieve coverage range

    Args:
        dataset (str): short name of the dataset
        datatype (str): type of "region" (gene/region/transcript)
        item (str): the datatype item to look up

    Returns:
        dict: start, stop, chromosome
    """
    ret = {'start':None, 'stop':None, 'chrom':None}

    if datatype == 'region':
        chrom, start, stop = item.split('-')
        if start and stop and chrom:
            ret['start'] = int(start)
            ret['stop'] = int(stop)
            ret['chrom'] = chrom
    else:
        if datatype == 'gene':
            gene = lookups.get_gene(dataset, item)
            transcript = lookups.get_transcript(dataset, gene['canonical_transcript'])
        elif datatype == 'transcript':
            transcript = lookups.get_transcript(dataset, item)
        if transcript:
            ret['start'] = transcript['start'] - EXON_PADDING
            ret['stop']  = transcript['stop'] + EXON_PADDING
            ret['chrom'] = transcript['chrom']

    return ret


def get_flags_from_variant(variant:dict):
    """
    Get flags from variant.
    Checks for:
    - MNP (identical length of reference and variant)
    - LoF (loss of function)

    Args:
        variant (dict): a variant

    Returns:
        list: flags for the variant
    """
    flags = []
    if 'mnps' in variant:
        flags.append('MNP')
    lof_annotations = [x for x in variant['vep_annotations'] if x['LoF'] != '']
    if not lof_annotations:
        return flags
    if all([x['LoF'] != 'HC' for x in lof_annotations]):
        flags.append('LC LoF')
    if all([x['LoF_flags'] != '' for x in lof_annotations]):
        flags.append('LoF flag')
    return flags


def get_proper_hgvs(annotation:dict):
    """
    Get HGVS for change, either at transcript or protein level.

    Args:
        annotation (dict): VEP annotation with HGVS information

    Returns:
        str: variant effect at aa level in HGVS format (p.), None if parsing fails
    """
    # Needs major_consequence
    try:
        if annotation['major_consequence'] in ('splice_donor_variant',
                                               'splice_acceptor_variant',
                                               'splice_region_variant'):
            return get_transcript_hgvs(annotation)
        return get_protein_hgvs(annotation)
    except KeyError:
        return None


def get_protein_hgvs(annotation):
    """
    Aa changes in HGVS format.

    Args:
        annotation (dict): VEP annotation with HGVS information

    Returns:
        str: variant effect at aa level in HGVS format (p.), None if parsing fails
    """
    try:
        if '%3D' in annotation['HGVSp']: # "%3D" is "="
            amino_acids = ''.join([PROTEIN_LETTERS_1TO3[aa] for aa in annotation['Amino_acids']])
            return "p." + amino_acids + annotation['Protein_position'] + amino_acids
        return annotation['HGVSp'].split(':')[-1]
    except KeyError:
        logging.error("Could not fetch protein hgvs")
        return None


def get_transcript_hgvs(annotation:dict):
    """
    Nucleotide change in HGVS format.

    Args:
        annotation (dict): VEP annotation with HGVS information

    Returns:
        str: variant effect at nucleotide level in HGVS format (c.), None if parsing fails
    """
    try:
        return annotation['HGVSc'].split(':')[-1]
    except KeyError:
        return None


def get_variant_list(dataset:str, datatype:str, item:str, ds_version:str=None):
    """
    Retrieve variants for a datatype

    Args:
        dataset (str): dataset short name
        datatype (str): type of data
        item (str): query item
        ds_version (str): dataset version

    Returns:
        dict: {variants:list, headers:list}
    """
    headers = [['variant_id','Variant'], ['chrom','Chrom'], ['pos','Position'],
               ['HGVS','Consequence'], ['filter','Filter'], ['major_consequence','Annotation'],
               ['flags','Flags'], ['allele_count','Allele Count'], ['allele_num','Allele Number'],
               ['hom_count','Number of Homozygous Alleles'], ['allele_freq','Allele Frequency']]

    if datatype == 'gene':
        variants = lookups.get_variants_in_gene(dataset, item)
    elif datatype == 'region':
        chrom, start, stop = item.split('-')
        if is_region_too_large(start, stop):
            return {'variants': [], 'headers': [], 'region_too_large': True}
        variants = lookups.get_variants_in_region(dataset, chrom, start, stop)
    elif datatype == 'transcript':
        variants = lookups.get_variants_in_transcript(dataset, item)

    # Format output
    def format_variant(variant):
        variant['major_consequence'] = (variant['major_consequence'].replace('_variant','')
                                        .replace('_prime_', '\'')
                                        .replace('_', ' '))

        # This is so an array values turns into a comma separated string instead
        return {k: ", ".join(v) if isinstance(v,list) else v for k, v in variant.items()}

    variants = list(map(format_variant, variants))
    return {'variants': variants, 'headers': headers}


def order_vep_by_csq(annotation_list:list):
    """
    Adds "major_consequence" to each annotation, orders by severity.

    Args:
        annotation_list (list): VEP annotations (as dict)

    Returns:
        list: annotations ordered by major consequence severity
    """
    for ann in annotation_list:
        try:
            ann['major_consequence'] = worst_csq_from_csq(ann['Consequence'])
        except KeyError:
            ann['major_consequence'] = ''
    return sorted(annotation_list, key=(lambda ann:CSQ_ORDER_DICT[ann['major_consequence']]))


def is_region_too_large(start:int, stop:int):
    '''
    Evaluates whether the size of a region is larger than maximum query
    Args:
        start (int): Start position of the region
        stop (int): End position of the region

    Returns:
        bool: True if too large
    '''
    region_limit = 100000
    return int(stop)-int(start) > region_limit


def remove_extraneous_vep_annotations(annotation_list:list):
    """
    Remove annotations with low-impact consequences (less than intron variant)

    Args:
        annotation_list (list): VEP annotations (as dict)

    Returns:
        list: VEP annotations with higher impact
    """
    return [ann for ann in annotation_list
            if worst_csq_index(ann['Consequence'].split('&')) <= CSQ_ORDER_DICT['intron_variant']]


def worst_csq_from_list(csq_list:list):
    """
    Choose the worst consequence

    Args:
        csq_list (list): list of consequences

    Returns:
        str: the worst consequence
    """
    return REV_CSQ_ORDER_DICT[worst_csq_index(csq_list)]


def worst_csq_from_csq(csq:str):
    """
    Find worst consequence in a possibly &-filled consequence string

    Args:
        csq (str): string of consequences, seperated with & (if multiple)

    Returns:
        str: the worst consequence
    """
    return REV_CSQ_ORDER_DICT[worst_csq_index(csq.split('&'))]


def worst_csq_index(csq_list:list):
    """
    Find the index of the worst consequence.
    Corresponds to the lowest value (index) from CSQ_ORDER_DICT

    Args:
        csq_list (list): consequences

    Returns:
        int: index in CSQ_ODER_DICT of the worst consequence
    """
    return min([CSQ_ORDER_DICT[csq] for csq in csq_list])


def worst_csq_with_vep(annotation_list:list):
    """
    Choose the vep annotation with the most severe consequence
    Adds a"major_consequence" field for that annotation

    Args:
        annotation_list (list): VEP annotations

    Returns:
        dict: the annotation with the most severe consequence
    """
    if not annotation_list:
        return None
    worst = max(annotation_list, key=annotation_severity)
    worst['major_consequence'] = worst_csq_from_csq(worst['Consequence'])
    return worst
