Additional index needs to be added for the Beacon to work smoothly:

	db.variants.createIndex({'chrom':1, 'pos': 1})
