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

    response = requests.get(f'{BASE_URL}/api/schema?url={BASE_URL}/dataset/{ds_name}/version/123456/browser')
    assert not response.text
    assert response.status_code == 404

    response = requests.get(f'{BASE_URL}/api/schema?url={BASE_URL}/dataset/bad_ds_name/browser')
    assert not response.text
    assert response.status_code == 404

    ds_name = 'SweGen2'
    response = requests.get(f'{BASE_URL}/api/schema?url={BASE_URL}/dataset/{ds_name}/version/UNRELEASED/browser')
    assert not response.text
    assert response.status_code == 403

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


def test_get_dataset():
    """
    Test GetDataset.get()
    """
    ds_name = 'SweGen'
    response = requests.get(f'{BASE_URL}/api/dataset/{ds_name}')
    data = json.loads(response.text)
    expected = {"study": 1,
                "shortName": "SweGen",
                "fullName": "SweGen",
                "version": {"version": "20180409",
                            "description": "desc",
                            "terms": "terms",
                            "availableFrom": "2001-01-04",
                            "refDoi": "doi",
                            "dataContactName": "place",
                            "dataContactLink": "email",
                            "numVariants": None,
                            "coverageLevels": [1, 5, 10, 15, 20, 25, 30, 50, 100],
                            "portalAvail": True,
                            "fileAccess": "REGISTERED",
                            "beaconAccess": "PUBLIC",
                            "dataset": 1,
                            "referenceSet": 1,
                            "varCallRef": None},
                "future": False}
    for value in expected:
        assert data[value] == expected[value]
    assert len(data) == 14

    ds_name = 'SweGen2'
    response = requests.get(f'{BASE_URL}/api/dataset/{ds_name}')
    data = json.loads(response.text)
    expected = {"study": 1,
                "shortName": "SweGen2",
                "fullName": "SweGen2",
                "version": {"version": "20190409",
                            "description": "desc",
                            "terms": "terms",
                            "availableFrom": "2001-01-05",
                            "refDoi": "doi",
                            "dataContactName": "place",
                            "dataContactLink": "email",
                            "numVariants": None,
                            "coverageLevels": [1, 5, 10, 15, 20, 25, 30, 50, 100],
                            "portalAvail": True,
                            "fileAccess": "REGISTERED",
                            "beaconAccess": "PUBLIC",
                            "dataset": 2,
                            "referenceSet": 1,
                            "varCallRef":None},
                "future": False}
    for value in expected:
        assert data[value] == expected[value]
    assert len(data) == 14

    ds_name = 'Unrel'
    response = requests.get(f'{BASE_URL}/api/dataset/{ds_name}')
    assert not response.text
    assert response.status_code == 404

