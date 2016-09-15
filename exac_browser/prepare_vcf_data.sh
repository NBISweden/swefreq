#!/bin/sh -x

# Script to remove individuals' data from VCF files.
# Assumes two compressed VCF files on the command line
# (one "indel" file and one "snp" file).
# Will merge these to create "swegen.vcf.gz" and a Tabix index.

# We use bcftools from a GitHub checkout since the Ubuntu version is too old.
bcftools_path="/home/andkaha/bcftools"

vcf1="$1"
vcf2="$2"

for vcf in "$vcf1" "$vcf2"
do
	(	zcat "$vcf" |
		awk '
		    BEGIN   { OFS = "\t" }
		    /^##/   { print; next }
			    { print $1,$2,$3,$4,$5,$6,$7,$8 }' |
		bgzip >"anon-$vcf"

		tabix -p vcf "anon-$vcf"
	) &
done

wait

"$bcftools_path"/bcftools concat -Oz -a "anon-$vcf1" "anon-$vcf2" >swegen.vcf.gz

tabix -f -p vcf swegen.vcf.gz
