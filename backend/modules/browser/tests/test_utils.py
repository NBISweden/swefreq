"""
Tests for utils.py
"""

from .. import lookups
from .. import utils

import json


def test_add_consequence_to_variants():
    """
    Test add_consequence_to_variants()
    """
    variants = []
    variants.append(lookups.get_variant('SweGen', 47730411, '21', 'TA', 'T'))
    variants.append(lookups.get_variant('SweGen', 55500283, '1', 'A', 'T'))
    variants[0]['vep_annotations'] = json.loads(variants[0]['vep_annotations']) # remove when db is fixed
    variants[1]['vep_annotations'] = json.loads(variants[1]['vep_annotations']) # remove when db is fixed

    utils.add_consequence_to_variants(variants)
    assert variants[0]['major_consequence'] == 'intron_variant'
    assert variants[1]['major_consequence'] == 'upstream_gene_variant'


def test_add_consequence_to_variant():
    """
    Test add_consequence_to_variant()
    """
    variant = lookups.get_variant('SweGen', 47730411, '21', 'TA', 'T')
    variant['vep_annotations'] = json.loads(variant['vep_annotations']) # remove when db is fixed
    utils.add_consequence_to_variant(variant)
    assert variant['major_consequence'] == 'intron_variant'
    
    variant2 = lookups.get_variant('SweGen', 55500283, '1', 'A', 'T')
    variant2['vep_annotations'] = json.loads(variant2['vep_annotations']) # remove when db is fixed
    utils.add_consequence_to_variant(variant2)
    assert variant2['major_consequence'] == 'upstream_gene_variant'
    

def test_annotation_severity():
    """
    Test annotation_severity()
    """
    variant = lookups.get_variant('SweGen', 55500283, '1', 'A', 'T')
    variant['vep_annotations'] = json.loads(variant['vep_annotations']) # remove when db is fixed
    res = utils.annotation_severity(variant['vep_annotations'][0])
    assert res == -26.9
    

def test_get_flags_from_variant():
    """
    Test get_flags_from_variant()
    """
    fake_variant = {'vep_annotations':[{'LoF': 'LC', 'LoF_flags': 'something'},
                                       {'LoF': '', 'LoF_flags': ''},
                                       {'LoF': 'LC', 'LoF_flags': 'something'}]}
    flags = utils.get_flags_from_variant(fake_variant)
    assert flags == ['LC LoF', 'LoF flag']

    fake_variant = {'vep_annotations':[{'LoF': 'LC', 'LoF_flags': 'something'},
                                       {'LoF': 'HC', 'LoF_flags': 'something'}]}
    flags = utils.get_flags_from_variant(fake_variant)
    assert flags == ['LoF flag']

    fake_variant = {'mnps': 'no idea', 'vep_annotations':[]}
    flags = utils.get_flags_from_variant(fake_variant)
    assert flags == ['MNP']


def test_get_proper_hgvs():
    """
    Test get_proper_hgvs()
    """
    assert False


def test_get_protein_hgvs():
    """
    Test get_protein_hgvs()
    """
    annotation = {'MAX_AF_POPS': 'AA&gnomAD_AMR&gnomAD_ASJ&gnomAD_EAS&gnomAD_OTH&gnomAD_SAS&AFR&AMR&EAS&EUR&SAS', 'TSL': '', 'APPRIS': '', 'gnomAD_ASJ_AF': '1', 'AMR_AF': '1', 'SYMBOL': 'ADH6', 'AFR_AF': '1', 'Feature': 'ENST00000237653', 'Codons': 'Tgt/Agt', 'MOTIF_NAME': '', 'DOMAINS': 'hmmpanther:PTHR11695:SF307&hmmpanther:PTHR11695&Gene3D:3.90.180.10', 'SIFT': 'tolerated(1)', 'VARIANT_CLASS': 'SNV', 'EA_AF': '0.9995', 'CDS_position': '4', 'CCDS': 'CCDS3647.1', 'Allele': 'T', 'PolyPhen': 'benign(0)', 'AA_AF': '1', 'gnomAD_EAS_AF': '1', 'IMPACT': 'MODERATE', 'HGVSp': '', 'ENSP': 'ENSP00000237653', 'MAX_AF': '1', 'LoF': '', 'INTRON': '', 'gnomAD_FIN_AF': '0.9999', 'Existing_variation': 'rs4699735', 'HGVSc': '', 'SOURCE': 'Ensembl', 'LoF_filter': '', 'gnomAD_AF': '0.9998', 'gnomAD_AMR_AF': '1', 'GENE_PHENO': '', 'gnomAD_OTH_AF': '1', 'LoF_flags': '', 'MOTIF_SCORE_CHANGE': '', 'UNIPARC': 'UPI00001AE69C', 'cDNA_position': '389', 'ALLELE_NUM': '1', 'EAS_AF': '1', 'Feature_type': 'Transcript', 'AF': '1', 'gnomAD_AFR_AF': '0.9999', 'HGNC_ID': '255', 'SAS_AF': '1', 'LoF_info': '', 'SWISSPROT': 'P28332', 'FLAGS': '', 'miRNA': '', 'Consequence': 'missense_variant', 'Protein_position': '2', 'Gene': 'ENSG00000172955', 'HIGH_INF_POS': '', 'STRAND': '-1', 'gnomAD_NFE_AF': '0.9995', 'EUR_AF': '1', 'DISTANCE': '', 'CLIN_SIG': '', 'PHENO': '', 'SYMBOL_SOURCE': 'HGNC', 'Amino_acids': 'C/S', 'TREMBL': '', 'gnomAD_SAS_AF': '1', 'REFSEQ_MATCH': '', 'PUBMED': '', 'BIOTYPE': 'protein_coding', 'EXON': '1/8', 'SOMATIC': '', 'MOTIF_POS': '', 'CANONICAL': ''}
    print(utils.get_protein_hgvs(annotation))
    assert False


def test_get_transcript_hgvs():
    """
    Test get_transcript_hgvs()
    """
    assert False


def test_order_vep_by_csq():
    """
    Test order_vep_by_csq()
    """
    assert False


def test_remove_extraneous_vep_annotations():
    """
    Test remove_extraneous_vep_annotations()
    """
    assert False


def test_worst_csq_from_csq():
    """
    Test worst_csq_from_csq()
    """
    variant = lookups.get_variant('SweGen', 55500283, '1', 'A', 'T')
    variant['vep_annotations'] = json.loads(variant['vep_annotations']) # remove when db is fixed
    res = utils.worst_csq_from_csq(variant['vep_annotations'][0]['Consequence'])
    assert res == 'upstream_gene_variant'
    res = utils.worst_csq_from_csq('non_coding_exon_variant&nc_transcript_variant')
    assert res == 'non_coding_exon_variant'


def test_worst_csq_from_list():
    """
    Test worst_csq_from_list()
    """
    csqs = ['frameshift_variant', 'missense_variant']
    assert utils.worst_csq_from_list(csqs) == 'frameshift_variant'


def test_worst_csq_index():
    """
    Test worst_csq_index()
    """
    csqs = ['frameshift_variant', 'missense_variant']
    assert utils.worst_csq_index(csqs) == 4


def test_worst_csq_with_vep():
    """
    Test worst_csq_from_vep()
    """
    veps = [{'SYMBOL': '1', 'Consequence': 'intergenic_variant', 'CANONICAL': ''},
            {'SYMBOL': '2', 'Consequence': 'frameshift_variant', 'CANONICAL': ''},
            {'SYMBOL': '3', 'Consequence': 'intron_variant', 'CANONICAL': ''},
            {'SYMBOL': '4', 'Consequence': 'stop_lost', 'CANONICAL': ''}]
    res = utils.worst_csq_with_vep(veps)
    assert res == {'SYMBOL': '2', 'Consequence': 'frameshift_variant',
                   'CANONICAL': '', 'major_consequence': 'frameshift_variant'}

    veps = [{'SYMBOL': '1', 'Consequence': 'frameshift_variant', 'CANONICAL': 'YES'},
            {'SYMBOL': '2', 'Consequence': 'frameshift_variant', 'CANONICAL': ''},
            {'SYMBOL': '3', 'Consequence': 'intron_variant', 'CANONICAL': ''},
            {'SYMBOL': '4', 'Consequence': 'stop_lost', 'CANONICAL': ''}]
    res = utils.worst_csq_with_vep(veps)
    assert res == {'SYMBOL': '1', 'Consequence': 'frameshift_variant',
                   'CANONICAL': 'YES', 'major_consequence': 'frameshift_variant'}
