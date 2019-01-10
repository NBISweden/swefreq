"""
Tests for the functions available in lookups.py
"""

import lookups


def test_add_rsid_to_variant():
    """
    Test add_rsid_to_variant()
    """
    # "with ."
    variant = lookups.get_variant('SweGen', 55500283, '1', 'A', 'T')
    rsid = variant['rsid']
    variant['rsid'] = '.'
    lookups.add_rsid_to_variant('SweGen', variant)
    assert variant['rsid'] == rsid
    # "non-existing"
    del variant['rsid']
    lookups.add_rsid_to_variant(variant)
    assert variant['rsid'] == rsid


def test_get_awesomebar_result():
    """
    Test get_awesomebar_result()
    """
    assert False


def test_get_coverage_for_bases():
    """
    Test get_coverage_for_bases()
    """
    coverage = lookups.get_coverage_for_bases('SweGen', '1', 55500283, 55500320)
    expected = [{'id': 5474062, 'dataset_version': 4, 'chrom': '1',
                 'pos': 55500290, 'mean': 40.66, 'median': 39.0,
                 'coverage': [1.0, 1.0, 1.0, 1.0, 0.996, 0.97, 0.867, 0.127, 0.001]},
                {'id': 5474063, 'dataset_version': 4, 'chrom': '1',
                 'pos': 55500300, 'mean': 40.7, 'median': 39.0,
                 'coverage': [1.0, 1.0, 1.0, 1.0, 0.996, 0.971, 0.878, 0.132, 0.001]},
                {'id': 5474064, 'dataset_version': 4, 'chrom': '1',
                 'pos': 55500310, 'mean': 40.35, 'median': 39.0,
                 'coverage': [1.0, 1.0, 1.0, 1.0, 0.995, 0.974, 0.859, 0.138, 0.001]},
                {'id': 5474065, 'dataset_version': 4, 'chrom': '1',
                 'pos': 55500320, 'mean': 39.69, 'median': 38.0,
                 'coverage': [1.0, 1.0, 1.0, 1.0, 0.996, 0.961, 0.856, 0.117, 0.001]}]
    assert coverage == expected


def test_get_coverage_for_transcript():
    coverage = lookups.get_coverage_for_transcript('SweGen', '1', 55500283, 55500320)
    expected = [{'id': 5474062, 'dataset_version': 4, 'chrom': '1',
                 'pos': 55500290, 'mean': 40.66, 'median': 39.0,
                 'coverage': [1.0, 1.0, 1.0, 1.0, 0.996, 0.97, 0.867, 0.127, 0.001]},
                {'id': 5474063, 'dataset_version': 4, 'chrom': '1',
                 'pos': 55500300, 'mean': 40.7, 'median': 39.0,
                 'coverage': [1.0, 1.0, 1.0, 1.0, 0.996, 0.971, 0.878, 0.132, 0.001]},
                {'id': 5474064, 'dataset_version': 4, 'chrom': '1',
                 'pos': 55500310, 'mean': 40.35, 'median': 39.0,
                 'coverage': [1.0, 1.0, 1.0, 1.0, 0.995, 0.974, 0.859, 0.138, 0.001]},
                {'id': 5474065, 'dataset_version': 4, 'chrom': '1',
                 'pos': 55500320, 'mean': 39.69, 'median': 38.0,
                 'coverage': [1.0, 1.0, 1.0, 1.0, 0.996, 0.961, 0.856, 0.117, 0.001]}]
    assert coverage == expected


def test_get_exons_in_transcript():
    """
    Test get_exons_in_transcript()
    """
    result = lookups.get_exons_in_transcript('SweGen', 'ENST00000346817')
    expected = [{'id': 326403, 'gene': 8600, 'transcript': 28186, 'chrom': '2',
                 'start': 202047893, 'stop': 202048032, 'strand': '+', 'feature_type': 'exon'},
                {'id': 326404, 'gene': 8600, 'transcript': 28186, 'chrom': '2',
                 'start': 202050495, 'stop': 202050848, 'strand': '+', 'feature_type': 'exon'},
                {'id': 326406, 'gene': 8600, 'transcript': 28186, 'chrom': '2',
                 'start': 202052430, 'stop': 202052523, 'strand': '+', 'feature_type': 'exon'},
                {'id': 326408, 'gene': 8600, 'transcript': 28186, 'chrom': '2',
                 'start': 202057708, 'stop': 202057843, 'strand': '+', 'feature_type': 'exon'},
                {'id': 326410, 'gene': 8600, 'transcript': 28186, 'chrom': '2',
                 'start': 202060566, 'stop': 202060672, 'strand': '+', 'feature_type': 'exon'},
                {'id': 326412, 'gene': 8600, 'transcript': 28186, 'chrom': '2',
                 'start': 202072799, 'stop': 202072907, 'strand': '+', 'feature_type': 'exon'},
                {'id': 326414, 'gene': 8600, 'transcript': 28186, 'chrom': '2',
                 'start': 202073794, 'stop': 202074286, 'strand': '+', 'feature_type': 'exon'},
                {'id': 326416, 'gene': 8600, 'transcript': 28186, 'chrom': '2',
                 'start': 202082312, 'stop': 202084804, 'strand': '+', 'feature_type': 'exon'}]
    assert result == expected


def test_get_gene():
    """
    Test get_gene()
    """
    # normal entry
    expected = {'id': 1,
                'reference_set': 1,
                'gene_id': 'ENSG00000223972',
                'gene_name': 'DDX11L1',
                'full_name': 'DEAD/H (Asp-Glu-Ala-Asp/His) box helicase 11 like 1',
                'canonical_transcript': 'ENST00000456328',
                'chrom': '1',
                'start_pos': 11870,
                'strand': '+'}
    result = lookups.get_gene('SweGen', 'ENSG00000223972')
    print(result)
    assert result['id'] == expected['id']
    assert result['reference_set'] == expected['reference_set']
    assert result['gene_id'] == expected['gene_id']
    assert result['name'] == expected['gene_name']
    assert result['full_name'] == expected['full_name']
    assert result['canonical_transcript'] == expected['canonical_transcript']
    assert result['chrom'] == expected['chrom']
    assert result['start'] == expected['start_pos']
    assert result['strand'] == expected['strand']

    # non-existing gene
    result = lookups.get_gene('SweGen', 'NOT_A_GENE')
    assert not result
    
    # non-existing dataset
    result = lookups.get_gene('NoDataset', 'ENSG00000223972')
    assert not result


def test_get_gene_by_name():
    """
    Test get_gene_by_name()
    """
    # normal entry
    expected = {'id': 1,
                'reference_set': 1,
                'gene_id': 'ENSG00000223972',
                'gene_name': 'DDX11L1',
                'full_name': 'DEAD/H (Asp-Glu-Ala-Asp/His) box helicase 11 like 1',
                'canonical_transcript': 'ENST00000456328',
                'chrom': '1',
                'start_pos': 11870,
                'strand': '+'}
    result = lookups.get_gene_by_name('SweGen', 'DDX11L1')
    assert result['id'] == expected['id']
    assert result['reference_set'] == expected['reference_set']
    assert result['gene_id'] == expected['gene_id']
    assert result['name'] == expected['gene_name']
    assert result['full_name'] == expected['full_name']
    assert result['canonical_transcript'] == expected['canonical_transcript']
    assert result['chrom'] == expected['chrom']
    assert result['start'] == expected['start_pos']
    assert result['strand'] == expected['strand']

    # non-existing gene
    result = lookups.get_gene_by_name('SweGen', 'NOT_A_GENE')
    assert not result
    
    # non-existing dataset
    result = lookups.get_gene_by_name('NoDataset', 'ENSG00000223972')
    assert not result

    # name in other_names
    result = lookups.get_gene_by_name('SweGen', 'NIR')
    assert result['gene_id'] == 'ENSG00000188976'
    

def test_get_genes_in_region():
    """
    Test get_genes_in_region()
    """
    res = lookups.get_genes_in_region('4', 99080000, 99210000)
    # stop_pos missing in db, so needs to be updated when available
    # exp_names = 
    assert False


def test_get_number_of_variants_in_transcript():
    """
    Test get_number_of_variants_in_transcripts()
    """
    assert False
    lookups.get_number_of_variants_in_transcripts()


def test_get_transcript():
    """
    Test get_transcript()
    """
    # normal entry
    expected = {'id': 5,
                'transcript_id': 'ENST00000438504',
                'gene': '2',
                'mim_annotation': 'Was protein family homolog 1; wash1',
                'chrom': '1',
                'mim_gene_accession': 613632,
                'start_pos': 14364,
                'stop_pos': 29371,
                'strand': '-'}
    exp_exon = [{'id': 28, 'gene': 2, 'transcript': 5, 'chrom': '1', 'start': 14364, 'stop': 14830, 'strand': '-', 'feature_type': 'exon'},
                {'id': 27, 'gene': 2, 'transcript': 5, 'chrom': '1', 'start': 14971, 'stop': 15039, 'strand': '-', 'feature_type': 'exon'},
                {'id': 26, 'gene': 2, 'transcript': 5, 'chrom': '1', 'start': 15797, 'stop': 15902, 'strand': '-', 'feature_type': 'exon'},
                {'id': 25, 'gene': 2, 'transcript': 5, 'chrom': '1', 'start': 15905, 'stop': 15948, 'strand': '-', 'feature_type': 'exon'},
                {'id': 24, 'gene': 2, 'transcript': 5, 'chrom': '1', 'start': 16608, 'stop': 16766, 'strand': '-', 'feature_type': 'exon'},
                {'id': 23, 'gene': 2, 'transcript': 5, 'chrom': '1', 'start': 16855, 'stop': 17056, 'strand': '-', 'feature_type': 'exon'},
                {'id': 22, 'gene': 2, 'transcript': 5, 'chrom': '1', 'start': 17234, 'stop': 17365, 'strand': '-', 'feature_type': 'exon'},
                {'id': 21, 'gene': 2, 'transcript': 5, 'chrom': '1', 'start': 17603, 'stop': 17743, 'strand': '-', 'feature_type': 'exon'},
                {'id': 20, 'gene': 2, 'transcript': 5, 'chrom': '1', 'start': 17916, 'stop': 18062, 'strand': '-', 'feature_type': 'exon'},
                {'id': 19, 'gene': 2, 'transcript': 5, 'chrom': '1', 'start': 18269, 'stop': 18380, 'strand': '-', 'feature_type': 'exon'},
                {'id': 18, 'gene': 2, 'transcript': 5, 'chrom': '1', 'start': 24739, 'stop': 24892, 'strand': '-', 'feature_type': 'exon'},
                {'id': 17, 'gene': 2, 'transcript': 5, 'chrom': '1', 'start': 29322, 'stop': 29371, 'strand': '-', 'feature_type': 'exon'}]

    result = lookups.get_transcript('SweGen', 'ENST00000438504')
    assert result['id'] == expected['id']
    assert result['mim_annotation'] == expected['mim_annotation']
    assert result['transcript_id'] == expected['transcript_id']
    assert result['mim_gene_accession'] == expected['mim_gene_accession']
    assert result['chrom'] == expected['chrom']
    assert result['start'] == expected['start_pos']
    assert result['stop'] == expected['stop_pos']
    assert result['strand'] == expected['strand']
    assert result['exons'] == exp_exon

    # non-existing
    assert not lookups.get_transcript('SweGen', 'INCORRECT')


def test_get_transcripts_in_gene():
    """
    Test get_transcripts_in_gene()
    """
    res = lookups.get_transcripts_in_gene('SweGen', 'ENSG00000241670')
    expected = [{'id': 39, 'transcript_id': 'ENST00000424429', 'gene': 19,
                 'mim_gene_accession': None, 'mim_annotation': None,
                 'chrom': '1', 'start': 228293, 'stop': 228655, 'strand': '-'},
                {'id': 40, 'transcript_id': 'ENST00000450734', 'gene': 19,
                 'mim_gene_accession': None, 'mim_annotation': None,
                 'chrom': '1', 'start': 228320, 'stop': 228776, 'strand': '-'}]
    assert res == expected


def test_get_raw_variant():
    """
    Test get_raw_variant
    """
    result = lookups.get_raw_variant('SweGen', 55500283, '1', 'A', 'T')
    assert result['genes'] == ['ENSG00000169174']
    assert result['transcripts'] == ['ENST00000302118']
    assert not lookups.get_raw_variant('SweGen', 55500281, '1', 'A', 'T')


def test_get_variant():
    """
    Test get_variant()
    """
    result = lookups.get_variant('SweGen', 55500283, '1', 'A', 'T')
    assert result['genes'] == ['ENSG00000169174']
    assert result['transcripts'] == ['ENST00000302118']
    assert result['rsid'] == 'rs75050571'

    # missing rsid in result, multiple transcripts
    # slow, need to fix db
    result = lookups.get_variant('SweGen', 47730411, '21', 'TA', 'T')
    assert result['genes'] == ['ENSG00000160298']
    assert result['transcripts'] == ['ENST00000417060', 'ENST00000397682',
                                     'ENST00000397683', 'ENST00000397680',
                                     'ENST00000397685', 'ENST00000397679',
                                     'ENST00000291691', 'ENST00000445935',
                                     'ENST00000491666', 'ENST00000472607',
                                     'ENST00000475776']
    assert result['rsid'] == 'rs75050571'
    # TODO: add test for entry with missing rsid

    # incorrect position
    assert not lookups.get_variant(-1, '1', 'A', 'T')


def test_get_variants_by_rsid(caplog):
    '''
    Test get_variants_by_rsid()
    '''
    # normal
    result = lookups.get_variants_by_rsid('SweGen', 'rs373706802')
    assert result[0]['genes'] == ['ENSG00000229286', 'ENSG00000235265']
    assert result[0]['transcripts'] == ['ENST00000448070','ENST00000413156']

    # errors
    assert lookups.get_variants_by_rsid('incorrect_name', 'rs373706802') is None
    assert lookups.get_variants_by_rsid('SweGen', '373706802') is None
    assert lookups.get_variants_by_rsid('SweGen', 'rs3737o68o2') is None
    expected = ('get_dataset_version(incorrect_name, version=None): cannot retrieve dataset version',
                'get_variants_by_rsid(SweGen, 373706802): rsid not starting with rs',
                'get_variants_by_rsid(SweGen, rs3737o68o2): not an integer after rs')
    for comparison in zip(caplog.messages, expected):
        assert comparison[0] == comparison[1]

    # no variants with rsid available
    assert not lookups.get_variants_by_rsid('SweGen', 'rs1')


def test_get_variants_in_region():
    """
    Test get_variants_in_region()
    """
    # normal
    result = lookups.get_variants_in_region('SweGen', '22', 16079200, 16079400)
    expected_pos = [16079227, 16079234, 16079289, 16079350]
    assert [res['pos'] for res in result] == expected_pos

    # no positions covered
    result = lookups.get_variants_in_region('SweGen', '22', 16079200, 16079000)
    assert not result

    # incorrect dataset
    result = lookups.get_variants_in_region('Incorrect_dataset', '22', 16079200, 16079400)
    assert not result


def test_get_variants_in_transcript():
    """
    Test get_variants_in_transcript()
    """
    # res = lookups.get_variants_in_transcript('ENST00000302118')
    #  assert len(res) == 426
    assert False
