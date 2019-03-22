#!/usr/bin/env python3
"""
Swefreq data importer.

Requires apt-packages:
    - python3-pip
    - sudo apt-get install libmysqlclient-dev

as well as pip3 packages:
    - mysqlclient
    - peewee-2.10.2
"""

from data_importer.reference_set_importer import ReferenceSetImporter
from data_importer.old_db_importer import OldDbImporter
from data_importer.raw_data_importer import RawDataImporter

if __name__ == '__main__':

    import os
    import argparse
    import logging

    PARSER = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    PARSER.add_argument("--batch_size", type=int, default=5000,
                        help=("Where batch insertion is possible, use this "
                              "number of inserts per batch."))
    PARSER.add_argument("--limit_chrom", default=None,
                        help="Limit chromosome to insert into the database.")
    PARSER.add_argument("--data_dir",
                        default=os.path.join(os.path.dirname(__file__),
                                             "downloaded_files"),
                        help="Default directory to download and look for files."
                        )

    # Reference versions
    PARSER.add_argument("--gencode_version", default=19, type=int,
                        help="Gencode version to download and use.")
    PARSER.add_argument("--ensembl_version", default="homo_sapiens_core_75_37",
                        help="Ensembl database to connect to.")
    PARSER.add_argument("--dbnsfp_version", default="2.9.3",
                        help="dbNSFP version to download and use.")

    # Dataset connections and naming
    PARSER.add_argument("--dataset", default="",
                        help="Which dataset to connect imported data to.")
    PARSER.add_argument("--version", default="",
                        help="Which dataset version to add imported data to.")
    PARSER.add_argument("--ref_name", default="",
                        help=("Reference name to use when creating a reference "
                              "set."))

    PARSER.add_argument("--dataset_size", type=int, default=0,
                        help="Set dataset size for this dataset")
    PARSER.add_argument("--set_vcf_sampleset_size", action="store_true",
                        help=("Set/update sampleset size to the value given in "
                              "the VCF. This is either the NS value, or the "
                              "number of stated samples"))
    PARSER.add_argument("--sampleset_size", type=int, default=0,
                        help="Set sampleset size for this dataset")
    PARSER.add_argument("--beacon_description", default="",
                        help="Set beacon description of the dataset.")
    PARSER.add_argument("--assembly_id", default="",
                        help=("Set reference assembly id (GRC notation, e.g. "
                              "GRCh37)"))

    # Raw data (coverage + variants) files
    PARSER.add_argument("--coverage_file", nargs="*",
                        help="Coverage file(s) to import.")
    PARSER.add_argument("--variant_file", nargs="*",
                        help="Variant file(s) to import.")

    # Actions
    PARSER.add_argument("--add_reference", action="store_true",
                        help="Insert new reference set.")
    PARSER.add_argument("--add_raw_data", action="store_true",
                        help="Adds a Coverage and Variants to the database.")
    PARSER.add_argument("--move_studies", action="store_true",
                        help=("Moves studies and datasets from an old database "
                              "to a new one."))
    PARSER.add_argument("--dry_run", action="store_true",
                        help="Do not insert anything into the database")

    # Logging and verbosity
    PARSER.add_argument("--disable_progress", action="store_true",
                        help="Do not show progress bars.")
    PARSER.add_argument("-v", "--verbose", action="count", default=3,
                        help="Increase output Verbosity.")
    PARSER.add_argument("-q", "--quiet", action="count", default=0,
                        help="Decrease output Verbosity.")

    # Beacon-only variants
    PARSER.add_argument("--beacon-only", action="store_true",
                        help=("Variants are intended only for Beacon, loosening"
                              " the requirements"))

    ARGS = PARSER.parse_args()

    logging.basicConfig(format="%(asctime)s %(levelname)s: %(message)s",
                        level=(5-ARGS.verbose+ARGS.quiet)*10,
                        datefmt="%H:%M:%S")

    if ARGS.add_reference:
        logging.info("Adding a new reference set using these sources:")
        logging.info("  - Gencode: %s", ARGS.gencode_version)
        logging.info("  - Ensembl: %s", ARGS.ensembl_version)
        logging.info("  - dbNSFP:  %s", ARGS.dbnsfp_version)

        IMPORTER = ReferenceSetImporter(ARGS)
        IMPORTER.prepare_data()
        if not ARGS.disable_progress:
            IMPORTER.count_entries()
        IMPORTER.start_import()

    if ARGS.move_studies:
        IMPORTER = OldDbImporter(ARGS)
        IMPORTER.prepare_data()
        IMPORTER.start_import()

    if ARGS.add_raw_data:
        logging.info("Adding raw data %s", "(dry run)" if ARGS.dry_run else '')
        IMPORTER = RawDataImporter(ARGS)
        IMPORTER.prepare_data()
        if not ARGS.disable_progress:
            IMPORTER.count_entries()
        IMPORTER.start_import()
