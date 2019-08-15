"""
Test the browser handlers
"""
import requests
import json

BASE_URL = "http://localhost:4000"


def test_get_autocomplete():
    """
    Test GetAutocomplete.get()
    """
    dataset = 'SweGen'

    query = 'PA'
    response = requests.get('{}/api/dataset/{}/browser/autocomplete/{}'.format(BASE_URL, dataset, query))
    data = json.loads(response.text)
    assert set(data["values"]) == set(["PABPC1P9", "PACSIN2", "PANX2", "PARP4P3",
                                       "PARVB", "PARVG", "PATZ1", "PAXBP1", "PAXBP1-AS1"])


def test_download():
    """
    Test Download.get()
    """
    dataset = 'SweGen'

    data_type = 'transcript'
    data_item = 'ENST00000438441'
    response = requests.get('{}/api/dataset/{}/browser/download/{}/{}'.format(BASE_URL, dataset, data_type, data_item))
    assert len(response.text.split('\n')) == 180  # header + 178 + \n
    response = requests.get('{}/api/dataset/{}/browser/download/{}/{}/filter/all~false'.format(BASE_URL, dataset, data_type, data_item))
    import logging
    logging.error(response.text.split('\n'))
    assert len(response.text.split('\n')) == 8
    response = requests.get('{}/api/dataset/{}/browser/download/{}/{}/filter/all~true'.format(BASE_URL, dataset, data_type, data_item))
    assert len(response.text.split('\n')) == 180
    response = requests.get('{}/api/dataset/{}/browser/download/{}/{}/filter/mislof~true'.format(BASE_URL, dataset, data_type, data_item))
    assert len(response.text.split('\n')) == 2
    data_type = 'region'
    data_item = '22-29450622-29465622'
    response = requests.get('{}/api/dataset/{}/browser/download/{}/{}/filter/mislof~false'.format(BASE_URL, dataset, data_type, data_item))
    assert len(response.text.split('\n')) == 3
    response = requests.get('{}/api/dataset/{}/browser/download/{}/{}/filter/lof~false'.format(BASE_URL, dataset, data_type, data_item))
    assert len(response.text.split('\n')) == 3


def test_get_coverage():
    """
    Test GetCoverage.get()
    """
    dataset = 'SweGen'

    data_type = 'transcript'
    data_item = 'ENST00000438441'
    response = requests.get('{}/api/dataset/{}/browser/coverage/{}/{}'.format(BASE_URL, dataset, data_type, data_item))
    data = json.loads(response.text)
    assert len(data['coverage']) == 144
    data_type = 'region'
    data_item = '1-1-1000000'
    response = requests.get('{}/api/dataset/{}/browser/coverage/{}/{}'.format(BASE_URL, dataset, data_type, data_item))
    assert response.status_code == 400
    data_item = '1-1-5'
    response = requests.get('{}/api/dataset/{}/browser/coverage/{}/{}'.format(BASE_URL, dataset, data_type, data_item))
    assert response.status_code == 404


def test_get_coverage_pos():
    """
    Test GetCoveragePos.get()
    """
    dataset = 'SweGen'
    data_type = 'region'
    data_item = '22-100001-100101'
    response = requests.get('{}/api/dataset/{}/browser/coverage_pos/{}/{}'.format(BASE_URL, dataset, data_type, data_item))
    cov_pos = json.loads(response.text)
    assert cov_pos['start'] == 100001
    assert cov_pos['stop'] == 100101
    assert cov_pos['chrom'] == '22'


def test_get_gene():
    """
    Test GetGene.get()
    """
    dataset = 'SweGen'
    gene_id = 'ENSG00000015475'
    response = requests.get('{}/api/dataset/{}/browser/gene/{}'.format(BASE_URL, dataset, gene_id))
    expected = {"name": "BID", "canonicalTranscript": "ENST00000317361", "chrom": "22", "strand": "-", "geneName": "BID"}
    gene = json.loads(response.text)

    for value in expected:
        assert gene['gene'][value] == expected[value]
    assert len(gene['exons']) == 14
    assert len(gene['transcripts']) == 10

    dataset = 'SweGen'
    gene_id = 'ENSG00000015475'
    response = requests.get('{}/api/dataset/{}/browser/gene/{}'.format(BASE_URL, dataset, gene_id))
    expected = {"name": "BID", "canonicalTranscript": "ENST00000317361", "chrom": "22", "strand": "-", "geneName": "BID"}
    gene = json.loads(response.text)

    dataset = 'SweGen'
    gene_id = 'BAD_GENE_ID'
    response = requests.get('{}/api/dataset/{}/browser/gene/{}'.format(BASE_URL, dataset, gene_id))
    assert response.status_code == 404


def test_get_region():
    """
    Test GetRegion.get()
    """
    dataset = 'SweGen'
    region_def = '22-46615715-46615880'
    response = requests.get('{}/api/dataset/{}/browser/region/{}'.format(BASE_URL, dataset, region_def))
    region = json.loads(response.text)
    expected = {'region': {'chrom': '22',
                           'start': 46615715,
                           'stop': 46615880,
                           'genes': [{'fullGeneName': 'peroxisome proliferator-activated receptor alpha',
                                      'geneId': 'ENSG00000186951',
                                      'geneName': 'PPARA'}]}}
    assert region == expected

    region_def = '22-16364870-16366200'
    response = requests.get('{}/api/dataset/{}/browser/region/{}'.format(BASE_URL, dataset, region_def))
    region = json.loads(response.text)
    expected = {'region': {'chrom': '22',
                           'start': 16364870,
                           'stop': 16366200,
                           'genes': [{'geneId': 'ENSG00000231565',
                                      'geneName': 'NEK2P2',
                                      'fullGeneName': 'NEK2 pseudogene 2'}]}}
    assert region == expected

    region_def = '22-46A1615715-46615880'
    response = requests.get('{}/api/dataset/{}/browser/region/{}'.format(BASE_URL, dataset, region_def))
    assert response.status_code == 400

    region_def = '22-1-1000000'
    response = requests.get('{}/api/dataset/{}/browser/region/{}'.format(BASE_URL, dataset, region_def))
    assert response.status_code == 400


def test_get_transcript():
    """
    Test GetTranscript.get()
    """
    dataset = 'SweGen'
    transcript_id = 'ENST00000317361'
    response = requests.get('{}/api/dataset/{}/browser/transcript/{}'.format(BASE_URL, dataset, transcript_id))
    transcript = json.loads(response.text)
    assert transcript['gene']['id'] == 'ENSG00000015475'
    assert len(transcript['exons']) == 14

    dataset = 'SweGen'
    transcript_id = 'BAD_TRANSCRIPT'
    response = requests.get('{}/api/dataset/{}/browser/transcript/{}'.format(BASE_URL, dataset, transcript_id))
    assert response.status_code == 404


def test_get_variant():
    """
    Test GetVariant.get()
    """
    dataset = 'SweGen'
    variant_id = '22-16080482-CAT-C'
    response = requests.get('{}/api/dataset/{}/browser/variant/{}'.format(BASE_URL, dataset, variant_id))
    variant = json.loads(response.text)
    assert variant['variant']['variantId'] == '22-16080482-CAT-C'
    assert set(variant['variant']['genes']) == set(['ENSG00000229286', 'ENSG00000235265'])
    assert len(variant['variant']['genes']) == len(['ENSG00000229286', 'ENSG00000235265'])
    assert set(variant['variant']['transcripts']) == set(['ENST00000448070', 'ENST00000413156'])
    assert len(variant['variant']['transcripts']) == len(['ENST00000448070', 'ENST00000413156'])

    variant_id = '22-16269941-G-C'
    response = requests.get('{}/api/dataset/{}/browser/variant/{}'.format(BASE_URL, dataset, variant_id))
    variant = json.loads(response.text)
    assert variant['variant']['variantId'] == '22-16269941-G-C'
    assert set(variant['variant']['genes']) == set(['ENSG00000198062', 'ENSG00000236666'])
    assert len(variant['variant']['genes']) == len(['ENSG00000198062', 'ENSG00000236666'])
    assert set(variant['variant']['transcripts']) == set(['ENST00000452800', 'ENST00000343518', 'ENST00000422014'])
    assert len(variant['variant']['transcripts']) == len(['ENST00000452800', 'ENST00000343518', 'ENST00000422014'])

    variant_id = '21-9411609-G-T'
    version = '20161223'
    response = requests.get('{}/api/dataset/{}/browser/variant/{}'.format(BASE_URL, dataset, variant_id))
    assert response.status_code == 404
    response = requests.get('{}/api/dataset/{}/version/{}/browser/variant/{}'.format(BASE_URL, dataset, version, variant_id))
    variant = json.loads(response.text)
    assert variant['variant']['variantId'] == '21-9411609-G-T'

    variant_id = '22-94358sfsdfsdf52-T-C'
    response = requests.get('{}/api/dataset/{}/browser/variant/{}'.format(BASE_URL, dataset, variant_id))
    assert response.status_code == 400


def test_get_variants():
    """
    Test GetVariants.get()
    """
    dataset = 'SweGen'

    data_type = 'gene'
    data_item = 'ENSG00000231565'
    response = requests.get('{}/api/dataset/{}/browser/variants/{}/{}'.format(BASE_URL, dataset, data_type, data_item))
    data = json.loads(response.text)
    assert len(data['variants']) == 178

    data_type = 'region'
    data_item = '22-16360000-16361200'
    response = requests.get('{}/api/dataset/{}/browser/variants/{}/{}'.format(BASE_URL, dataset, data_type, data_item))
    data = json.loads(response.text)
    assert len(data['variants']) == 13

    data_type = 'region'
    data_item = '22-46615715-46715880'
    response = requests.get('{}/api/dataset/{}/browser/variants/{}/{}'.format(BASE_URL, dataset, data_type, data_item))
    assert response.status_code == 400

    data_type = 'transcript'
    data_item = 'ENST00000438441'
    response = requests.get('{}/api/dataset/{}/browser/variants/{}/{}'.format(BASE_URL, dataset, data_type, data_item))
    data = json.loads(response.text)
    assert len(data['variants']) == 178


def test_search():
    """
    Test Search.get()
    """
    dataset = 'SweGen'

    query = 'NF1P3'
    response = requests.get('{}/api/dataset/{}/browser/search/{}'.format(BASE_URL, dataset, query))
    data = json.loads(response.text)
    assert data['type'] == 'gene'
    assert data['value'] == 'ENSG00000183249'

    query = 'rs142856307'
    response = requests.get('{}/api/dataset/{}/browser/search/{}'.format(BASE_URL, dataset, query))
    data = json.loads(response.text)
    assert data['type'] == 'dbsnp'
    assert data['value'] == 142856307

    query = '22-1234321-A-T'
    response = requests.get('{}/api/dataset/{}/browser/search/{}'.format(BASE_URL, dataset, query))
    data = json.loads(response.text)
    assert data['type'] == 'not_found'
    assert data['value'] == '22-1234321-A-T'

    query = '21-29461622-G-A'
    version = '20161223'
    response = requests.get('{}/api/dataset/{}/version/{}/browser/search/{}'.format(BASE_URL, dataset, version, query))
    data = json.loads(response.text)
    assert data['type'] == 'variant'
    assert data['value'] == '21-29461622-G-A'
