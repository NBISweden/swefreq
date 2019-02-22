"""
Tests for the functions available in pgsql.py
"""

from .. import pgsql


def test_get_autocomplete():
    """
    Test get_autocomplete()
    """
    res = pgsql.get_autocomplete('PA')
    expected = set(["PABPC1P9", "PACSIN2", "PANX2", "PARP4P3",
                "PARVB", "PARVG", "PATZ1", "PAXBP1", "PAXBP1-AS1"])
    assert set(res) == expected


def test_get_coverage():
    """
    Test get_coverage()
    """
    res = pgsql.get_coverage('SweGen', 'gene', 'ENSG00000231565')
    assert len(res['coverage']) == 144
    res = pgsql.get_coverage('SweGen', 'region', '22-46615715-46615880')
    assert len(res['coverage']) == 17
    res = pgsql.get_coverage('SweGen', 'transcript', 'ENST00000438441')
    assert len(res['coverage']) == 144

    assert not pgsql.get_coverage('BAD_SET', 'transcript', 'ENST00000438441')['coverage']


def test_get_coverage_pos():
    """
    Test get_coverage_pos()
    """
    res = pgsql.get_coverage_pos('SweGen', 'gene', 'ENSG00000231565')
    assert res['chrom'] == '22'
    assert res['start'] == 16364817
    assert res['stop'] == 16366254
    res = pgsql.get_coverage_pos('SweGen', 'region', '22-46615715-46615880')
    assert res['chrom'] == '22'
    assert res['start'] == 46615715
    assert res['stop'] == 46615880
    res = pgsql.get_coverage_pos('SweGen', 'transcript', 'ENST00000438441')
    assert res['chrom'] == '22'
    assert res['start'] == 16364817
    assert res['stop'] == 16366254

    res = pgsql.get_coverage_pos('BAD_SET', 'transcript', 'ENST00000438441')
    for value in res.values():
        assert not value


def test_get_variant_list():
    """
    Test get_variant_list()
    """
    res = pgsql.get_variant_list('SweGen', 'gene', 'ENSG00000231565')
    assert len(res['variants']) == 405
    res = pgsql.get_variant_list('SweGen', 'region', '22-46615715-46615880')
    assert len(res['variants']) == 3
    res = pgsql.get_variant_list('SweGen', 'transcript', 'ENST00000438441')
    assert len(res['variants']) == 405
