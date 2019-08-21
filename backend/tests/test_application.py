"""
Test the browser handlers
"""
import json

import requests

BASE_URL = "http://localhost:4000"

def test_get_schema():
    """
    Test GetSchema.get()
    """
    response = requests.get(f'{BASE_URL}/api/schema')
    data = json.loads(response.text)
    expected = {'@context': 'http://schema.org/',
                '@type': 'DataCatalog',
                'name': 'SweFreq',
                'alternateName': ['The Swedish Frequency resource for genomics']}
    assert len(data) == 10
    for value in expected:
        assert data[value] == expected[value]

    ds_name = 'SweGen'
    response = requests.get(f'{BASE_URL}/api/schema?url={BASE_URL}/dataset/{ds_name}/browser')
    data = json.loads(response.text)
    expected = {"@type": "Dataset",
                "url": f"{BASE_URL}/dataset/{ds_name}",
                "@id": f"{BASE_URL}/dataset/{ds_name}",
                "name": f"{ds_name}",
                "description": "desc",
                "identifier": f"{ds_name}",
                "citation": "doi"}
    assert data['dataset'] == expected

    response = requests.get(f'{BASE_URL}/api/schema?url={BASE_URL}/dataset/{ds_name}/beacon')
    data = json.loads(response.text)
    expected = {'@id': 'https://swefreq.nbis.se/api/beacon-elixir/',
                '@type': 'Beacon',
                'dct:conformsTo': 'https://bioschemas.org/specifications/drafts/Beacon/',
                'name': 'Swefreq Beacon',
                'provider': {'@type': 'Organization',
                             'name': 'National Bioinformatics Infrastructure Sweden',
                             'alternateName': ['NBIS', 'ELIXIR Sweden'],
                             'logo': 'http://nbis.se/assets/img/logos/nbislogo-green.svg',
                             'url': 'https://nbis.se/'},
                'supportedRefs': ['GRCh37'],
                'description': 'Beacon API Web Server based on the GA4GH Beacon API',
                'aggregator': False,
                'url': 'https://swefreq.nbis.se/api/beacon-elixir/'}
    for value in expected:
        assert data[value] == expected[value]


def test_get_countrylist():
    """
    Test CountryList.get()
    """
    response = requests.get(f'{BASE_URL}/api/countries')
    data = json.loads(response.text)

    assert len(data['countries']) == 240
