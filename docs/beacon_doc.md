## Current api-version
1.0.1

## TODOs for nex api-version

- next version: 1.1.0
- handover (implementation started)
- mateNames for fusions (https://github.com/ga4gh-beacon/specification/pull/256)
- `info` is an object instead of array
- diff: https://github.com/ga4gh-beacon/specification/compare/develop

## Variant types

- Supported and existing in our current Beacon: `INS, DEL, SNP`

- Available from the datasets (although not used by the beacon):
    - in the SweGen dataset: `insertion, SNV, deletion, indel, sequence_alteration`
    - in the ACpop dataset: `insertion, SNV, deletion`

- What we don't have: `MNP, DUP, BND, INV, CNV, DUP:TANDEM, DEL:ME, INS:ME`

- What we don't know:
  - How do `indel` and `sequence_alteration` relate to the Beacon variant types? Do they require multiple tags (eg `indel => del + ins`)?
     `rs200774489` is annotated as `sequence_alteration`, but is an insertion according to https://www.ncbi.nlm.nih.gov/snp/rs200774489
  - How to communicate which types the datasets support?


## Alternate bases

- Allowed: `(ATCGN)+`. Extra value in our data: `*`.

    Should probably be expressed with `N` in the response (`*` is not allowed).
     - Example, as given in the Beacon response now:
       ```"referenceName": "22",
          "start": "16060517",
          "referenceBases": "T",
          "alternateBases": "*",
          "variantType": "SNP"
       ```
     In the VCF, this variation is not annotated with `rsid` or `variantType` in the CSQ field.

     From the VCF spec:
     > The ‘*’ allele is reserved to indicate that the allele is missing due to an overlapping deletion.

     Should rather be shown as (?):
     ```"referenceName": "22",
        "start": "16060517",
        "referenceBases": "T",
        "alternateBases": "N",
        "variantType": "DEL"
     ```
