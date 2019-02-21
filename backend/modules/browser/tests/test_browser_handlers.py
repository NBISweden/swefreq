"""
Test the browser handlers
"""

import requests
import json

BASE_URL="http://localhost:4000"

def test_get_autocomplete():
    """
    Test GetAutocomplete.get()
    """
    assert False


def test_download():
    """
    Test GetCoveragePos.get()
    """
    assert False


def test_get_coverage():
    """
    Test GetCoverage.get()
    """
    assert False


def test_get_coverage_pos():
    """
    Test GetCoveragePos.get()
    """
    assert False


def test_get_gene():
    """
    Test GetGene.get()
    """
    dataset = 'SweGen'
    gene_id = 'ENSG00000015475'
    response = requests.get('{}/api/datasets/{}/browser/gene/{}'.format(BASE_URL, dataset, gene_id))
    expected = {"name": "BID", "canonicalTranscript": "ENST00000317361", "chrom": "22", "strand": "-", "geneName": "BID"}
    gene = json.loads(response.text)

    for value in expected:
        assert gene['gene'][value] == expected[value]
    assert len(gene['exons']) == 14
    assert len(gene['transcripts']) == 10


def test_get_region():
    """
    Test GetRegion.get()
    """
    dataset = 'SweGen'
    region_def = '22-46615715-46615880'
    response = requests.get('{}/api/datasets/{}/browser/region/{}'.format(BASE_URL, dataset, region_def))
    region = json.loads(response.text)
    assert region == {'region': {'chrom': '22', 'start': 46615715, 'stop': 46615880, 'limit': 100000}}


def test_get_transcript():
    """
    Test GetTranscript.get()
    """
    dataset = 'SweGen'
    transcript_id = 'ENST00000317361'
    response = requests.get('{}/api/datasets/{}/browser/transcript/{}'.format(BASE_URL, dataset, transcript_id))
    transcript = json.loads(response.text)

    assert transcript['gene']['id'] == 'ENSG00000015475'
    assert len(transcript['exons']) == 14


def test_get_variant():
    """
    Test GetVariant.get()
    """
    assert False


def test_get_variants():
    """
    Test GetVariants.get()
    """
    assert False


def test_searhc():
    """
    Test Search.get()
    """
    assert False
