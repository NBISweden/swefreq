#!/usr/bin/env python3
import argparse
import re
import sys

import db

def update(dataset):
    print("Updating dataset_version 2")
    dv = db.DatasetVersion.select().where( db.DatasetVersion.dataset_version == 2 ).get()

    newterms = ""
    with open('/tmp/new-terms.txt') as f:
        newterms = "".join(f.readlines())

    newdesc = ""
    with open('/tmp/new-description.txt') as f:
        newdesc = "".join(f.readlines())

    dv.terms = newterms
    dv.description = newdesc
    dv.save()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Manage datasets in database')
    parser.add_argument('--dataset', help='Dataset id', required=True)
    args = parser.parse_args()
    update(args.dataset, args.file)
