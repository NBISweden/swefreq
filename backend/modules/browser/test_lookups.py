import lookups

def test_get_gene():
    expected = {'id': 1,
                'reference_set': 1,
                'gene_id': 'ENSG00000223972',
                'gene_name': 'DDX11L1',
                'full_name': 'DEAD/H (Asp-Glu-Ala-Asp/His) box helicase 11 like 1',
                'canonical_transcript': 'ENST00000456328',
                'chrom': '1',
                'start_pos': 11870,
                'strand': '+'}
    result = lookups.get_gene('ENSG00000223972')
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
    
    result = lookups.get_gene('NOT_A_GENE')
    assert not result
