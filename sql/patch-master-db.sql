-- Patches a database that is using the master checkout of the
-- swefreq.sql schema definition to the develop version.


-- Add mongodb_collection to the dataset table

ALTER TABLE dataset ADD COLUMN
    mongodb_collection VARCHAR(50);

UPDATE dataset SET mongodb_collection = 'exac'
    WHERE dataset_pk = 1;

ALTER TABLE dataset MODIFY COLUMN
    mongodb_collection VARCHAR(50) NOT NULL;

-- Add file size to dataset_file table

ALTER TABLE dataset_file ADD COLUMN
    bytes               BIGINT          NOT NULL;

-- Add file sizes to the files we already have

UPDATE dataset_file SET bytes=4957818880 WHERE name='swegen_20161223.tar';
UPDATE dataset_file SET bytes=4960460800 WHERE name='swegen_20170823.tar';
UPDATE dataset_file SET bytes=26154119   WHERE name='swegen_frequencies_SVDB_hg19_20171025.tar.gz';
UPDATE dataset_file SET bytes=4960460800 WHERE name='swegen_frequencies_hg19_20171025.tar';

-- Add some unique constraints
ALTER TABLE study ADD
    CONSTRAINT UNIQUE (pi_email, title);
ALTER TABLE dataset_version ADD
    CONSTRAINT UNIQUE (dataset_pk, version);
ALTER TABLE collection ADD
    CONSTRAINT UNIQUE (name, ethnicity);
ALTER TABLE sample_set ADD
    CONSTRAINT UNIQUE (dataset_pk, collection_pk);
ALTER TABLE dataset_file ADD
    CONSTRAINT UNIQUE (uri);
