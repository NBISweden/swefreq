import logging
from operator import itemgetter

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
assert len(CSQ_ORDER) == len(set(CSQ_ORDER)) # No dupplicates

CSQ_ORDER_DICT = {csq:i for i,csq in enumerate(CSQ_ORDER)}
REV_CSQ_ORDER_DICT = dict(enumerate(CSQ_ORDER))
assert all(csq == REV_CSQ_ORDER_DICT[CSQ_ORDER_DICT[csq]] for csq in CSQ_ORDER)

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


def add_consequence_to_variants(variant_list):
    """
    Add information about variant consequence to multiple variants

    Args:
        variant_list (list): list of variants
    """
    for variant in variant_list:
        add_consequence_to_variant(variant)


def add_consequence_to_variant(variant):
    """
    Add information about variant consequence to a variant

    Args:
        variant (dict): variant information
    """
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


def annotation_severity(annotation):
    """
    Evaluate severity of the consequences; "bigger is more important"

    Args:
        annotation (dict): vep_annotation from a variant

    Returns:
        float: severity score
    """
    rv = -CSQ_ORDER_DICT[worst_csq_from_csq(annotation['Consequence'])]
    if annotation['CANONICAL'] == 'YES':
        rv += 0.1
    return rv


def get_flags_from_variant(variant):
    """
    Get flags from variant.
    checks for: 
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


def get_proper_hgvs(csq):
    # Needs major_consequence
    if csq['major_consequence'] in ('splice_donor_variant', 'splice_acceptor_variant', 'splice_region_variant'):
        return get_transcript_hgvs(csq)

    return get_protein_hgvs(csq)


def get_protein_hgvs(annotation):
    """
    Takes consequence dictionary, returns proper variant formatting for synonymous variants
    """
    if '%3D' in annotation['HGVSp']: # "%3D" is "="
        try:
            amino_acids = ''.join([PROTEIN_LETTERS_1TO3[x] for x in annotation['Amino_acids']])
            return "p." + amino_acids + annotation['Protein_position'] + amino_acids
        except KeyError:
            logging.error("Could not fetch protein hgvs - unknown amino acid")
    return annotation['HGVSp'].split(':')[-1]


def get_transcript_hgvs(csq):
    return csq['HGVSc'].split(':')[-1]


def order_vep_by_csq(annotation_list):
    """
    Adds "major_consequence" to each annotation.
    Returns them ordered from most deleterious to least.
    """
    for ann in annotation_list:
        ann['major_consequence'] = worst_csq_from_csq(ann['Consequence'])
    return sorted(annotation_list, key=(lambda ann:CSQ_ORDER_DICT[ann['major_consequence']]))


def remove_extraneous_vep_annotations(annotation_list):
    return [ann for ann in annotation_list if worst_csq_index(ann['Consequence'].split('&')) <= CSQ_ORDER_DICT['intron_variant']]


def worst_csq_from_list(csq_list):
    """
    Input list of consequences (e.g. ['frameshift_variant', 'missense_variant'])
    Return the worst consequence (In this case, 'frameshift_variant')
    Works well with worst_csq_from_list('non_coding_exon_variant&nc_transcript_variant'.split('&'))
    """
    return REV_CSQ_ORDER_DICT[worst_csq_index(csq_list)]


def worst_csq_from_csq(csq):
    """
    Find worst consequence in a possibly &-filled consequence string 

    Args:
        csq (str): string of consequences, seperated with & (if multiple)
    
    Returns:
        str: the worst consequence
    """
    return REV_CSQ_ORDER_DICT[worst_csq_index(csq.split('&'))]


def worst_csq_index(csq_list):
    """
    Find the index of the worst consequence.
    Corresponds to the lowest value (index) from CSQ_ORDER_DICT

    Args:
        csq_list (list): consequences

    Returns:
        int: index in CSQ_ODER_DICT of the worst consequence
    """
    return min([CSQ_ORDER_DICT[csq] for csq in csq_list])


def worst_csq_with_vep(annotation_list):
    """
    Choose the vep annotation with the most severe consequence

    Args:
        annotation_list (list): VEP annotations 
    
    Returns:
        dict: the annotation with the most severe consequence; also adds "major_consequence" for that annotation
    """
    if not annotation_list:
        return None
    worst = max(annotation_list, key=annotation_severity)
    worst['major_consequence'] = worst_csq_from_csq(worst['Consequence'])
    return worst
