#!/usr/bin/env python3
import db

print("Updating dataset_version 2")
dv = db.DatasetVersion.select().where( db.DatasetVersion.dataset_version == 2 ).get()

newterms = ""
with open('/tmp/new-terms.txt') as f:
    newterms = "".join(f.readlines())

newdesc = ""
with open('/tmp/new-description.txt') as f
    newdesc = "".join(f.readlines())

dv.terms = newterms
dv.description = newdesc
dv.save()
