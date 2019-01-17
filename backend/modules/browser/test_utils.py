"""
Tests for utils.py
"""

import lookups
import utils

import json


def test_add_consequence_to_variants():
    """
    Test add_consequence_to_variants()
    """
    assert False


def test_add_consequence_to_variant():
    """
    Test add_consequence_to_variant()
    """
    # variant = lookups.get_variant('SweGen', 47730411, '21', 'TA', 'T')
    variant2 = lookups.get_variant('SweGen', 55500283, '1', 'A', 'T')
    # variant2['vep_annotations'] = 
    result = utils.add_consequence_to_variant(variant2)
    # result = utils.add_consequence_to_variant(variant)
    print(result)
    print(result['major_consequence'])
    print(result['category'])
    
    assert False


def test_annotation_severity():
    """
    Test annotation_severity()
    """
    variant = lookups.get_variant('SweGen', 55500283, '1', 'A', 'T')
    utils.annotation_severity(variant['vep_annotations'])


def test_worst_csq_from_csq():
    """
    Test worst_csq_from_csq()
    """
    variant = lookups.get_variant('SweGen', 55500283, '1', 'A', 'T')
    print(type(variant['vep_annotations']))
    print(variant['vep_annotations'])
    vep = json.loads(variant['vep_annotations'])[0]
    print(vep['Consequence'])
    utils.worst_csq_from_csq(vep['Consequence'])
    assert False
