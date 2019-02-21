"""
Test the browser handlers
"""

import requests

BASE_URL="http://localhost:4000"

def test_get_gene():
    """
    Test GetGene.get()
    """
    dataset = 'SweGen'
    gene = 'ENSG00000172955'
    response = requests.get('{}/api/datasets/{}/browser/gene/{}'.format(BASE_URL, dataset, gene))
    expected = '{"gene": {"id": 13918, "referenceSet": 1, "geneId": "ENSG00000172955", "name": "ADH6", "fullName": "alcohol dehydrogenase 6 (class V)", "canonicalTranscript": "ENST00000394899", "chrom": "4", "start": 100123795, "stop": 100140694, "strand": "-", "variants": null, "geneName": "ADH6", "fullGeneName": "alcohol dehydrogenase 6 (class V)"}, "exons": [{"start": 100123796, "stop": 100125400, "type": "exon"}, {"start": 100123796, "stop": 100125378, "type": "UTR"}, {"start": 100125379, "stop": 100125400, "type": "CDS"}, {"start": 100126082, "stop": 100126220, "type": "exon"}, {"start": 100126082, "stop": 100126220, "type": "CDS"}, {"start": 100128603, "stop": 100128738, "type": "exon"}, {"start": 100128603, "stop": 100128738, "type": "CDS"}, {"start": 100129825, "stop": 100130085, "type": "exon"}, {"start": 100129825, "stop": 100130085, "type": "CDS"}, {"start": 100131239, "stop": 100131455, "type": "exon"}, {"start": 100131239, "stop": 100131455, "type": "CDS"}, {"start": 100131572, "stop": 100131659, "type": "exon"}, {"start": 100131572, "stop": 100131659, "type": "CDS"}, {"start": 100134763, "stop": 100134904, "type": "exon"}, {"start": 100134763, "stop": 100134904, "type": "CDS"}, {"start": 100137318, "stop": 100137419, "type": "exon"}, {"start": 100137318, "stop": 100137419, "type": "CDS"}, {"start": 100140292, "stop": 100140403, "type": "exon"}, {"start": 100140292, "stop": 100140309, "type": "CDS"}, {"start": 100140310, "stop": 100140403, "type": "UTR"}], "transcripts": [{"transcriptId": "ENST00000394897"}, {"transcriptId": "ENST00000394899"}, {"transcriptId": "ENST00000512708"}, {"transcriptId": "ENST00000507484"}, {"transcriptId": "ENST00000407820"}, {"transcriptId": "ENST00000237653"}, {"transcriptId": "ENST00000508558"}, {"transcriptId": "ENST00000504257"}, {"transcriptId": "ENST00000513262"}]}'
    assert response.text == expected

