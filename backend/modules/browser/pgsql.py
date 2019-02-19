"""
Replaces mongodb.py
"""

import logging

import db

from . import lookups

EXON_PADDING = 50

def get_autocomplete(query:str):
    """
    Provide autocomplete suggestions based on the query
    Args:
        query (str): the query to compare to the available gene names
    Returns:
        list: A list of genes names whose beginning matches the query
    """
    genes = db.Gene.select(db.Gene.name).where(db.Gene.name.startswith(query))
    gene_names = [str(gene.name) for gene in genes]
    return gene_names


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
