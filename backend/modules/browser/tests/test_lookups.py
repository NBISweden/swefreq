"""
Tests for the functions available in lookups.py
"""

from .. import lookups


def test_get_awesomebar_result():
    """
    Test get_awesomebar_result()
    """
    result = lookups.get_awesomebar_result('SweGen', 'rs373706802')
    assert result == ('dbsnp_variant_set', 373706802)
    result = lookups.get_awesomebar_result('SweGen', 'rs783')
    assert result == ('variant', '22-29461622-G-A')
    result = lookups.get_awesomebar_result('SweGen', 'NF1P3')
    assert result == ('gene', 'ENSG00000183249')
    result = lookups.get_awesomebar_result('SweGen', 'ENSG00000183249')
    assert result == ('gene', 'ENSG00000183249')
    result = lookups.get_awesomebar_result('SweGen', 'ENST00000457709')
    assert result == ('transcript', 'ENST00000457709')
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
    expected = {'chrom': '22', 'coverage': [1.0, 1.0, 0.993, 0.91, 0.697, 0.426, 0.2, 0.009, 0.0],
                           'dataset_version': 4, 'mean': 24.94, 'median': 24.0, 'pos': 46546430}
    for val in expected:
        assert coverage[0][val] == expected[val]

    assert len(lookups.get_coverage_for_bases('SweGen', '22', 46615715, 46615880)) == 17

    # no end_pos
    coverage = lookups.get_coverage_for_bases('SweGen', '22', 46546430)
    expected = {'chrom': '22', 'coverage': [1.0, 1.0, 0.993, 0.91, 0.697, 0.426, 0.2, 0.009, 0.0],
                'dataset_version': 4, 'mean': 24.94, 'median': 24.0, 'pos': 46546430}
    for val in expected:
        assert coverage[0][val] == expected[val]
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
    coverage = lookups.get_coverage_for_transcript('SweGen', '22', 46546423, 46549652)
    assert len(coverage) == 323
    expected = {'chrom': '22', 'coverage': [1.0, 1.0, 0.993, 0.91, 0.697, 0.426, 0.2, 0.009, 0.0],
                'dataset_version': 4, 'mean': 24.94, 'median': 24.0, 'pos': 46546430}
    for val in expected:
        assert coverage[0][val] == expected[val]
    assert len(lookups.get_coverage_for_transcript('SweGen', '22', 46615715, 46615880)) == 17

    # no end_pos
    coverage = lookups.get_coverage_for_transcript('SweGen', '22', 46546430)
    expected = {'chrom': '22', 'coverage': [1.0, 1.0, 0.993, 0.91, 0.697, 0.426, 0.2, 0.009, 0.0],
                'dataset_version': 4, 'mean': 24.94, 'median': 24.0, 'pos': 46546430}
    for val in expected:
        assert coverage[0][val] == expected[val]
    assert len(lookups.get_coverage_for_transcript('SweGen', '22', 46615715, 46615880)) == 17

    # no hits
    coverage = lookups.get_coverage_for_transcript('SweGen', '1', 55500283, 55500285)
    assert not coverage

    # incorrect dataset
    assert not lookups.get_coverage_for_transcript('BAD_DATASET', '1', 55500283, 55500320)


def test_get_exons_in_transcript():
    """
    Test get_exons_in_transcript()
    """
    result = lookups.get_exons_in_transcript('SweGen', 'ENST00000215855')
    assert len(result) == 14

    # bad dataset
    result = lookups.get_exons_in_transcript('NO_DATASET', 'ENST00000215855')
    assert not result

    # bad transcript
    result = lookups.get_exons_in_transcript('SweGen', 'BAD_TRANSCRIPT')
    assert not result


def test_get_gene():
    """
    Test get_gene()
    """
    # normal entry
    expected = {'gene_id': 'ENSG00000251940',
                'name': 'SNORA15',
                'full_name': None,
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
    expected = {'gene_id': 'ENSG00000226444',
                'name': 'ACTR3BP6',
                'full_name': 'ACTR3B pseudogene 6',
                'canonical_transcript': 'ENST00000421366',
                'chrom': '22',
                'start': 16967410,
                'stop': 16969212,
                'strand': '+'}
    gene = lookups.get_gene('SweGen', 'ENSG00000226444')
    result = lookups.get_gene_by_dbid(gene['id'])
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
    expected = {'gene_id': 'ENSG00000226444',
                'name': 'ACTR3BP6',
                'full_name': 'ACTR3B pseudogene 6',
                'canonical_transcript': 'ENST00000421366',
                'chrom': '22',
                'start': 16967410,
                'stop': 16969212,
                'strand': '+'}
    result = lookups.get_gene_by_name('SweGen', 'ACTR3BP6')
    for val in expected:
        assert result[val] == expected[val]

    # non-existing gene
    result = lookups.get_gene_by_name('SweGen', 'NOT_A_GENE')
    assert not result
    assert caplog.messages[0] == 'get_gene_by_name(SweGen, NOT_A_GENE): unable to retrieve gene'

    # non-existing dataset
    result = lookups.get_gene_by_name('NoDataset', 'ENSG00000223972')
    assert not result

    # name in other_names
    result = lookups.get_gene_by_name('SweGen', 'BCL8C')
    print(result)
    assert result['gene_id'] == 'ENSG00000223875'


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
    assert res == {'filtered': 66, 'total': 309}

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
    expected = {'transcript_id': 'ENST00000398242',
                'chrom': '22',
                'start': 16122720,
                'stop': 16123768,
                'strand': '+'}

    result = lookups.get_transcript('SweGen', 'ENST00000398242')
    for val in expected:
        assert result[val] == expected[val]
    assert len(result['exons']) == 1

    # non-existing
    assert not lookups.get_transcript('SweGen', 'INCORRECT')


def test_get_transcripts_in_gene():
    """
    Test get_transcripts_in_gene()
    """
    res = lookups.get_transcripts_in_gene('SweGen', 'ENSG00000228314')
    assert len(res) == 3

    assert not lookups.get_transcripts_in_gene('bad_dataset', 'ENSG00000241670')
    assert not lookups.get_transcripts_in_gene('SweGen', 'ENSGASDFG')


def test_get_raw_variant():
    """
    Test get_raw_variant
    """
    result = lookups.get_variant('SweGen', 16057464, '22', 'G', 'A')
    assert result['genes'] == ['ENSG00000233866']
    assert result['transcripts'] == ['ENST00000424770']
    assert not lookups.get_raw_variant('SweGen', 55500281, '1', 'A', 'T')
    assert not lookups.get_raw_variant('bad_dataset', 55500283, '1', 'A', 'T')


def test_get_transcripts_in_gene_by_dbid():
    """
    Test get_transcripts_in_gene_by_dbid()
    """
    gene = lookups.get_gene('SweGen', 'ENSG00000228314')
    res = lookups.get_transcripts_in_gene_by_dbid(gene['id'])
    assert len(res) == 3
    res = lookups.get_transcripts_in_gene_by_dbid(-1)
    assert not res


def test_get_variant():
    """
    Test get_variant()
    """
    result = lookups.get_variant('SweGen', 16057464, '22', 'G', 'A')
    assert result['variant_id'] == '22-16057464-G-A'
    assert result['genes'] == ['ENSG00000233866']
    assert result['transcripts'] == ['ENST00000424770']
    result = lookups.get_variant('SweGen', 9435852, '21', 'T', 'C')
    assert not result

    # incorrect position
    assert not lookups.get_variant('SweGen', -1, '1', 'A', 'T')

    # with version
    result = lookups.get_variant('SweGen', 16057464, '22', 'G', 'A', "20161223")
    assert not result
    result = lookups.get_variant('SweGen', 9435852, '21', 'T', 'C', "20161223")
    assert result['variant_id'] == '21-9435852-T-C'


def test_get_variants_by_rsid():
    '''
    Test get_variants_by_rsid()
    '''
    # normal
    result = lookups.get_variants_by_rsid('SweGen', 'rs185758992')
    assert result[0]['pos'] == 38481311
    assert set(result[0]['genes']) == set(['ENSG00000100156', 'ENSG00000128298', 'ENSG00000272720'])
    assert len(result[0]['genes']) == 3
    assert len(result[0]['transcripts']) == 6
    assert not lookups.get_variants_by_rsid('SweGen', 'rs76676778')
    # with version
    assert not lookups.get_variants_by_rsid('SweGen', 'rs185758992', '20161223')
    result = lookups.get_variants_by_rsid('SweGen', 'rs76676778', '20161223')
    assert result[0]['variant_id'] == '21-9411609-G-T'

    # by position
    result = lookups.get_variants_by_rsid('SweGen', 'rs185758992', check_position=True)
    assert result[0]['pos'] == 38481311
    assert set(result[0]['genes']) == set(['ENSG00000100156', 'ENSG00000128298', 'ENSG00000272720'])
    assert len(result[0]['genes']) == 3
    assert len(result[0]['transcripts']) == 6
    assert not lookups.get_variants_by_rsid('SweGen', 'rs76676778', check_position=True)
    # with version
    assert not lookups.get_variants_by_rsid('SweGen', 'rs185758992', '20161223', check_position=True)
    result = lookups.get_variants_by_rsid('SweGen', 'rs76676778', '20161223', check_position=True)
    assert result[0]['variant_id'] == '21-9411609-G-T'

    # errors
    assert lookups.get_variants_by_rsid('incorrect_name', 'rs373706802') is None
    assert lookups.get_variants_by_rsid('SweGen', 'rs37356766700', check_position=True) is None
    assert lookups.get_variants_by_rsid('SweGen', '373706802') is None
    assert lookups.get_variants_by_rsid('SweGen', 'rs3737o68o2') is None

    # no variants with rsid available
    assert not lookups.get_variants_by_rsid('SweGen', 'rs1')


def test_get_variants_in_gene():
    """
    Test get_variants_in_gene()
    """
    res = lookups.get_variants_in_gene('SweGen', 'ENSG00000198062')
    assert len(res) == 1185
    assert not lookups.get_variants_in_gene('bad_dataset', 'ENSG00000198062')
    res = lookups.get_variants_in_gene('ACpop', 'ENSG00000040608')
    assert len(res) == 260
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
    assert len(res) == 1174
    res = lookups.get_variants_in_transcript('BAD_DATASET', 'ENST00000452800')
