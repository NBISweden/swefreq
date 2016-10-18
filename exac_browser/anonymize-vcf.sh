#!/bin/bash -x

# Script to remove individuals' data from a VCF file.
# Output file will be compressed and a tabix index will be created.

vcf="$1"

if [[ ${vcf%.gz} == "$vcf" ]]; then
    prefilter="cat"
    outfile="anon-$vcf.gz"
else
    prefilter="zcat"
    outfile="anon-$vcf"
fi

$prefilter "$vcf" |
awk '
    BEGIN   { OFS = "\t" }
    /^##/   { print; next }
        { print $1,$2,$3,$4,$5,$6,$7,$8 }' |
bgzip >"$outfile"

tabix -p vcf "$outfile"
