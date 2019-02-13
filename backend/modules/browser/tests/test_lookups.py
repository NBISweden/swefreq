"""
Tests for the functions available in lookups.py
"""

from .. import lookups


def test_add_rsid_to_variant():
    """
    Test add_rsid_to_variant()
    """
    variant = lookups.get_variant('SweGen', 34730985, '22', 'G', 'A')
    lookups.add_rsid_to_variant('SweGen', variant)
    assert variant['rsid'] == 'rs924645261'
    variant = lookups.get_variant('SweGen', 16113980, '22', 'C', 'T')
    rsid = variant['rsid']
    variant['rsid'] = ''
    lookups.add_rsid_to_variant('SweGen', variant)
    assert variant['rsid'] == 'rs9680543'


def test_get_awesomebar_result():
    """
    Test get_awesomebar_result()
    """
    result = lookups.get_awesomebar_result('SweGen', 'rs373706802')
    assert result == ('dbsnp_variant_set', 373706802)
    result = lookups.get_awesomebar_result('SweGen', 'rs783')
    assert result == ('variant', '22-29461622-G-A')
    result = lookups.get_awesomebar_result('SweGen', 'ADH6')
    assert result == ('gene', 'ENSG00000172955')
    result = lookups.get_awesomebar_result('SweGen', 'ENSG00000172955')
    assert result == ('gene', 'ENSG00000172955')
    result = lookups.get_awesomebar_result('SweGen', 'ENST00000237653')
    assert result == ('transcript', 'ENST00000237653')
    result = lookups.get_awesomebar_result('SweGen', '22-46615715-46615880')
    assert result == ('region', '22-46615715-46615880')
    result = lookups.get_awesomebar_result('SweGen', 'CHR22:46615715-46615880')
    assert result == ('region', '22-46615715-46615880')
    result = lookups.get_awesomebar_result('SweGen', 'CHR22-29461622-G-A')
    assert result == ('variant', '22-29461622-G-A')
    result = lookups.get_awesomebar_result('SweGen', 'DOES_NOT_EXIST')
    assert result == ('not_found', 'DOES_NOT_EXIST')


def test_get_coverage_for_bases():
    """
    Test get_coverage_for_bases()
    """
    # normal
    coverage = lookups.get_coverage_for_bases('SweGen', '22', 46546423, 46549652)
    assert len(coverage) == 323
    assert coverage[0] == {'chrom': '22', 'coverage': [1.0, 1.0, 0.993, 0.91, 0.697, 0.426, 0.2, 0.009, 0.0],
                           'dataset_version': 4, 'id': 2954967, 'mean': 24.94, 'median': 24.0, 'pos': 46546430}
    assert len(lookups.get_coverage_for_bases('SweGen', '22', 46615715, 46615880)) == 17

    # no end_pos
    coverage = lookups.get_coverage_for_bases('SweGen', '22', 46546430)
    assert coverage == [{'chrom': '22', 'coverage': [1.0, 1.0, 0.993, 0.91, 0.697, 0.426, 0.2, 0.009, 0.0],
                         'dataset_version': 4, 'id': 2954967, 'mean': 24.94, 'median': 24.0, 'pos': 46546430}]
    assert len(lookups.get_coverage_for_bases('SweGen', '22', 46615715, 46615880)) == 17

    # no hits
    coverage = lookups.get_coverage_for_bases('SweGen', '1', 55500283, 55500285)
    assert not coverage

    # incorrect dataset
    assert not lookups.get_coverage_for_bases('BAD_DATASET', '1', 55500283, 55500320)


def test_get_coverage_for_transcript():
    """
    Test get_coverage_for_transcript()
    """
    # normal
    coverage = lookups.get_coverage_for_bases('SweGen', '22', 46546423, 46549652)
    assert len(coverage) == 323
    assert coverage[0] == {'chrom': '22', 'coverage': [1.0, 1.0, 0.993, 0.91, 0.697, 0.426, 0.2, 0.009, 0.0],
                           'dataset_version': 4, 'id': 2954967, 'mean': 24.94, 'median': 24.0, 'pos': 46546430}
    assert len(lookups.get_coverage_for_bases('SweGen', '22', 46615715, 46615880)) == 17

    # no end_pos
    coverage = lookups.get_coverage_for_bases('SweGen', '22', 46546430)
    assert coverage == [{'chrom': '22', 'coverage': [1.0, 1.0, 0.993, 0.91, 0.697, 0.426, 0.2, 0.009, 0.0],
                         'dataset_version': 4, 'id': 2954967, 'mean': 24.94, 'median': 24.0, 'pos': 46546430}]
    assert len(lookups.get_coverage_for_bases('SweGen', '22', 46615715, 46615880)) == 17

    # no hits
    coverage = lookups.get_coverage_for_bases('SweGen', '1', 55500283, 55500285)
    assert not coverage

    # incorrect dataset
    assert not lookups.get_coverage_for_bases('BAD_DATASET', '1', 55500283, 55500320)


def test_get_exons_in_transcript(caplog):
    """
    Test get_exons_in_transcript()
    """
    result = lookups.get_exons_in_transcript('SweGen', 'ENST00000215855')
    assert len(result) == 14

    # bad dataset
    result = lookups.get_exons_in_transcript('NO_DATASET', 'ENST00000215855')
    assert not result
    assert caplog.messages[0] == 'get_exons_in_transcript(NO_DATASET, ENST00000215855): unable to find dataset dbid'

    # bad transcript
    result = lookups.get_exons_in_transcript('SweGen', 'BAD_TRANSCRIPT')
    assert not result
    assert caplog.messages[1] == 'get_exons_in_transcript(SweGen, BAD_TRANSCRIPT): unable to retrieve transcript'


def test_get_gene():
    """
    Test get_gene()
    """
    # normal entry
    expected = {'gene_id': 'ENSG00000223972',
                'name': 'SNORA15',
                'full_name': '',
                'canonical_transcript': 'ENST00000516131',
                'chrom': '22',
                'start': 19237396,
                'stop': 19237489,
                'strand': '+'}
    
    result = lookups.get_gene('SweGen', 'ENSG00000251940')
    for val in expected:
        assert result[val] == expected[val]

    # non-existing gene
    result = lookups.get_gene('SweGen', 'NOT_A_GENE')
    assert not result

    # non-existing dataset
    result = lookups.get_gene('NoDataset', 'ENSG00000223972')
    assert not result


def test_get_gene_by_dbid():
    """
    Test get_gene_by_dbid()
    """
    # normal entry
    expected = {'id': 53626,
                'reference_set': 1,
                'gene_id': 'ENSG00000226444',
                'name': 'ACTR3BP6',
                'full_name': 'ACTR3B pseudogene 6',
                'canonical_transcript': 'ENST00000421366',
                'chrom': '22',
                'start': 16967411,
                'strand': '+'}
    result = lookups.get_gene_by_dbid(53626)
    for val in expected:
        assert result[val] == expected[val]

    # non-existing genes
    result = lookups.get_gene_by_dbid('NOT_A_GENE')
    assert not result
    result = lookups.get_gene_by_dbid(-1)
    assert not result

def test_get_gene_by_name(caplog):
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
    assert caplog.messages[0] == 'get_gene_by_name(SweGen, NOT_A_GENE): unable to retrieve gene'

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
    # stop_pos missing in db, so needs to be updated when available
    # normal
    res = lookups.get_genes_in_region('SweGen', '22', 25595800, 25615800)
    expected_names = set(['ENSG00000100053', 'ENSG00000236641', 'ENSG00000244752'])
    names = set(gene['gene_id'] for gene in res)
    assert names == expected_names
    # bad dataset
    res = lookups.get_genes_in_region('bad_dataset', '22', 25595800, 25615800)
    # nothing found
    res = lookups.get_genes_in_region('SweGen', '22', 25595800, 25595801)
    assert not res


def test_get_number_of_variants_in_transcript():
    """
    Test get_number_of_variants_in_transcripts()
    """
    # normal
    res = lookups.get_number_of_variants_in_transcript('SweGen', 'ENST00000424770')
    assert res == {'filtered': 243, 'total': 309}

    # bad transcript
    res = lookups.get_number_of_variants_in_transcript('SweGen', 'ENSTASDSADA')
    assert res is None

    # bad dataset
    res = lookups.get_number_of_variants_in_transcript('bad_dataset', 'ENST00000424770')
    assert res is None


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

    assert not lookups.get_transcripts_in_gene('bad_dataset', 'ENSG00000241670')
    assert not lookups.get_transcripts_in_gene('SweGen', 'ENSGASDFG')


def test_get_raw_variant():
    """
    Test get_raw_variant
    """
    result = lookups.get_raw_variant('SweGen', 55500283, '1', 'A', 'T')
    assert result['genes'] == ['ENSG00000169174']
    assert result['transcripts'] == ['ENST00000302118']
    assert not lookups.get_raw_variant('SweGen', 55500281, '1', 'A', 'T')
    assert not lookups.get_raw_variant('bad_dataset', 55500283, '1', 'A', 'T')


def test_get_transcripts_in_gene_by_dbid():
    """
    Test get_transcripts_in_gene_by_dbid()
    """
    res = lookups.get_transcripts_in_gene_by_dbid(53626)
    assert len(res) == 2
    res = lookups.get_transcripts_in_gene_by_dbid(-1)
    assert not res


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

    # incorrect position
    assert not lookups.get_variant('SweGen', -1, '1', 'A', 'T')


def test_get_variants_by_rsid(caplog):
    '''
    Test get_variants_by_rsid()
    '''
    # normal
    result = lookups.get_variants_by_rsid('SweGen', 'rs373706802')
    assert result[0]['pos'] == 16080482
    assert result[0]['genes'] == ['ENSG00000229286', 'ENSG00000235265']
    assert result[0]['transcripts'] == ['ENST00000448070','ENST00000413156']

    # by position
    result = lookups.get_variants_by_rsid('SweGen', 'rs373706802', check_position=True)
    assert result[0]['pos'] == 16080482
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


def test_get_variants_in_gene():
    """
    Test get_variants_in_gene()
    """
    res = lookups.get_variants_in_gene('SweGen', 'ENSG00000198062')
    assert len(res) == 1185
    assert not lookups.get_variants_in_gene('bad_dataset', 'ENSG00000198062')
    assert not lookups.get_variants_in_gene('bad_dataset', 'ENSGASDFG')


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
    res = lookups.get_variants_in_transcript('SweGen', 'ENST00000452800')
    assert len(res) == 1414
