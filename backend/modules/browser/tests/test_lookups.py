"""
Tests for the functions available in lookups.py
"""

import pytest

from .. import error
from .. import lookups


def test_autocomplete():
    """
    Test get_autocomplete()
    """
    res = lookups.autocomplete('SweGen', 'PA')
    expected = set(["PABPC1P9", "PACSIN2", "PANX2", "PARP4P3",
                    "PARVB", "PARVG", "PATZ1", "PAXBP1", "PAXBP1-AS1"])
    assert set(res) == expected
    with pytest.raises(error.NotFoundError):
        res = lookups.autocomplete('Bad_dataset', 'PA')


def test_get_awesomebar_result():
    """
    Test get_awesomebar_result()
    """
    result = lookups.get_awesomebar_result('SweGen', 'rs142856307')
    assert result == ('dbsnp_variant_set', 142856307)
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
    result = lookups.get_awesomebar_result('SweGen', '22-1234321-A-A')
    assert result == ('not_found', '22-1234321-A-A')
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
    with pytest.raises(error.NotFoundError):
        lookups.get_coverage_for_bases('SweGen', '1', 55500283, 55500285)

    # incorrect dataset
    with pytest.raises(error.NotFoundError):
        lookups.get_coverage_for_bases('BAD_DATASET', '1', 55500283, 55500320)


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
    with pytest.raises(error.NotFoundError):
        coverage = lookups.get_coverage_for_transcript('SweGen', '1', 55500283, 55500285)

    # incorrect dataset
    with pytest.raises(error.NotFoundError):
        assert not lookups.get_coverage_for_transcript('BAD_DATASET', '1', 55500283, 55500320)


def test_get_exons_in_transcript():
    """
    Test get_exons_in_transcript()
    """
    result = lookups.get_exons_in_transcript('SweGen', 'ENST00000215855')
    assert len(result) == 14

    # bad dataset
    with pytest.raises(error.NotFoundError):
        result = lookups.get_exons_in_transcript('NO_DATASET', 'ENST00000215855')

    # bad transcript
    with pytest.raises(error.NotFoundError):
        result = lookups.get_exons_in_transcript('SweGen', 'BAD_TRANSCRIPT')


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
    with pytest.raises(error.NotFoundError):
        result = lookups.get_gene('SweGen', 'NOT_A_GENE')

    # non-existing dataset
    with pytest.raises(error.NotFoundError):
        result = lookups.get_gene('NoDataset', 'ENSG00000223972')


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


def test_get_gene_by_name():
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
    with pytest.raises(error.NotFoundError):
        lookups.get_gene_by_name('SweGen', 'NOT_A_GENE')

    # non-existing dataset
    with pytest.raises(error.NotFoundError):
        lookups.get_gene_by_name('NoDataset', 'ENSG00000223972')

    # name in other_names
    result = lookups.get_gene_by_name('SweGen', 'BCL8C')
    assert result['gene_id'] == 'ENSG00000223875'


def test_get_genes_in_region():
    """
    Test get_genes_in_region()
    """
    # stop_pos missing in db, so needs to be updated when available
    # normal
    res = lookups.get_genes_in_region('SweGen', '22', 25595800, 25615800)
    expected_ids = set(['ENSG00000100053', 'ENSG00000236641', 'ENSG00000244752'])
    gene_ids = set(gene['gene_id'] for gene in res)
    assert gene_ids == expected_ids
    res = lookups.get_genes_in_region('SweGen', '22', 16364870, 16366200)
    expected_ids = ['ENSG00000231565']
    assert [gene['gene_id'] for gene in res] == expected_ids
    # bad dataset
    with pytest.raises(error.NotFoundError):
        lookups.get_genes_in_region('bad_dataset', '22', 25595800, 25615800)
    # nothing found
    assert not lookups.get_genes_in_region('SweGen', '22', 25595800, 25595801)


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
    with pytest.raises(error.NotFoundError):
        lookups.get_transcript('SweGen', 'INCORRECT')


def test_get_transcripts_in_gene():
    """
    Test get_transcripts_in_gene()
    """
    res = lookups.get_transcripts_in_gene('SweGen', 'ENSG00000228314')
    assert len(res) == 3

    with pytest.raises(error.NotFoundError):
        lookups.get_transcripts_in_gene('bad_dataset', 'ENSG00000241670')
    with pytest.raises(error.NotFoundError):
        lookups.get_transcripts_in_gene('SweGen', 'ENSGASDFG')


def test_get_raw_variant():
    """
    Test get_raw_variant
    """
    result = lookups.get_raw_variant('SweGen', 16080482, '22', 'CAT', 'C')
    assert set(result['genes']) == set(['ENSG00000229286', 'ENSG00000235265'])
    assert len(result['genes']) == len(['ENSG00000229286', 'ENSG00000235265'])
    assert set(result['transcripts']) == set(['ENST00000448070', 'ENST00000413156'])
    assert len(result['transcripts']) == len(['ENST00000448070', 'ENST00000413156'])
    with pytest.raises(error.NotFoundError):
        assert not lookups.get_raw_variant('SweGen', 55500281, '1', 'A', 'T')
    with pytest.raises(error.NotFoundError):
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
    result = lookups.get_variant('SweGen', 16080482, '22', 'CAT', 'C')
    assert result['variant_id'] == '22-16080482-CAT-C'
    assert set(result['genes']) == set(['ENSG00000229286', 'ENSG00000235265'])
    assert len(result['genes']) == len(['ENSG00000229286', 'ENSG00000235265'])
    assert set(result['transcripts']) == set(['ENST00000448070', 'ENST00000413156'])
    assert len(result['transcripts']) == len(['ENST00000448070', 'ENST00000413156'])

    # not found
    with pytest.raises(error.NotFoundError):
        result = lookups.get_variant('SweGen', 12321, '21', 'G', 'G')
    with pytest.raises(error.NotFoundError):
        result = lookups.get_variant('SweGen', 9411609, '21', 'G', 'T')

    # incorrect position
    with pytest.raises(error.NotFoundError):
        assert not lookups.get_variant('SweGen', -1, '1', 'A', 'T')

    # with version
    with pytest.raises(error.NotFoundError):
        result = lookups.get_variant('SweGen', 16057464, '22', 'G', 'A', "20161223")
    result = lookups.get_variant('SweGen', 9411609, '21', 'G', 'T', "20161223")
    assert result['variant_id'] == '21-9411609-G-T'


def test_get_variants_by_rsid():
    '''
    Test get_variants_by_rsid()
    '''
    # normal
    result = lookups.get_variants_by_rsid('SweGen', 'rs142856307')
    assert result[0]['pos'] == 16285954
    assert len(result) == 5
    with pytest.raises(error.NotFoundError):
        assert not lookups.get_variants_by_rsid('SweGen', 'rs76676778')
    # with version
    with pytest.raises(error.NotFoundError):
        lookups.get_variants_by_rsid('SweGen', 'rs185758992', '20161223')
    result = lookups.get_variants_by_rsid('SweGen', 'rs76676778', '20161223')
    assert result[0]['variant_id'] == '21-9411609-G-T'

    # errors
    with pytest.raises(error.NotFoundError):
        lookups.get_variants_by_rsid('incorrect_name', 'rs373706802')
    with pytest.raises(error.ParsingError):
        lookups.get_variants_by_rsid('SweGen', '373706802')
    with pytest.raises(error.ParsingError):
        lookups.get_variants_by_rsid('SweGen', 'rs3737o68o2')

    # no variants with rsid available
    with pytest.raises(error.NotFoundError):
        lookups.get_variants_by_rsid('SweGen', 'rs1')


def test_get_variants_in_gene():
    """
    Test get_variants_in_gene()
    """
    res = lookups.get_variants_in_gene('SweGen', 'ENSG00000198062')
    assert len(res) == 512

    # existing gene without variants
    assert not lookups.get_variants_in_gene('SweGen', 'ENSG00000128298')

    # bad requests
    with pytest.raises(error.NotFoundError):
        lookups.get_variants_in_gene('bad_dataset', 'ENSG00000198062')
    with pytest.raises(error.NotFoundError):
        lookups.get_variants_in_gene('bad_dataset', 'ENSGASDFG')
    with pytest.raises(error.NotFoundError):
        lookups.get_variants_in_gene('SweGen', 'ENSG00000198062', "BAD_VERSION")


def test_get_variants_in_region():
    """
    Test get_variants_in_region()
    """
    # normal
    result = lookups.get_variants_in_region('SweGen', '22', 16079200, 16079400)
    expected_pos = [16079227, 16079289]
    assert [res['pos'] for res in result] == expected_pos

    # no positions covered
    assert not lookups.get_variants_in_region('SweGen', '22', 16079200, 16079000)

    # no variants found
    assert not lookups.get_variants_in_region('SweGen', '22', 106079000, 106079200)

    # incorrect dataset
    with pytest.raises(error.NotFoundError):
        lookups.get_variants_in_region('Incorrect_dataset', '22', 16079200, 16079400)


def test_get_variants_in_transcript():
    """
    Test get_variants_in_transcript()
    """
    res = lookups.get_variants_in_transcript('SweGen', 'ENST00000452800')
    assert len(res) == 508

    # bad requests
    with pytest.raises(error.NotFoundError):
        assert not lookups.get_variants_in_transcript('BAD_DATASET', 'ENST00000452800')
    with pytest.raises(error.NotFoundError):
        assert not lookups.get_variants_in_transcript('SweGen', 'ENST123')
