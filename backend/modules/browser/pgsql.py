"""
Replaces mongodb.py
"""

import logging

from . import db
from . import lookups
from .utils import get_xpos


def get_autocomplete(dataset, query):
    """
    Provide autocomplete suggestions based on the query
    NOTE: dataset is not used for sql
    Args:
        dataset (str): name of the dataset
        query (str): the query to compare to the available gene names
    Returns:
        list: A list of genes names whose beginning matches the query
    """
    genes = db.Gene.select(db.Gene.name).where(db.Gene.name.startswith(query))
    gene_names = [str(gene.name) for gene in genes]
    logging.error('Autocomplete: {}'.format(gene_names))
    return gene_names
