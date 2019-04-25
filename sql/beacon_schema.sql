-------------------------------------------------------------------------------
-- Modified beacon schema.
--
-- This schema is heavily based on the finnish beacon schema at:
-- https://github.com/CSCfi/beacon-python/blob/master/data/init.sql
--
-- but has been modified to use views instead of tables for the
-- beacon_dataset_table and beacon_data_table.
-- This was done so that the main swefreq-schema could be kept, without having
-- to store duplicate information.

CREATE SCHEMA IF NOT EXISTS beacon;

--------------------------------------------------------------------------------
-- Beacon dataset and data tables
--
-- These tables need to be represented as semi-complex views, as to avoid
-- storing redundant data.


CREATE TABLE IF NOT EXISTS beacon.beacon_dataset_counts_table (
    datasetid       varchar(128) PRIMARY KEY,
    dataset         integer      REFERENCES data.dataset_versions,
    callCount       integer      DEFAULT NULL,
    variantCount    integer      DEFAULT NULL
);


CREATE OR REPLACE VIEW beacon.beacon_dataset_table AS           -- original type
    SELECT v.id AS index,                                       -- serial
           d.short_name AS name,                                -- varchar(128)
           concat_ws(':', r.reference_build,
                          d.short_name,
                          v.dataset_version) AS datasetId,      -- varchar(128)
           d.beacon_description AS "description",               -- varchar(512)
           substr(r.reference_build, 0,  7) AS assemblyId,      -- varchar(16)
           v.available_from AS createDateTime,                  -- timestamp
           v.available_from AS updateDateTime,                  -- timstamp
           v.dataset_version AS "version",                      -- varchar(8)
           s.sample_size AS sampleCount,                        -- integer
           d.browser_uri AS externalUrl,                        -- varchar(256)
           CASE WHEN v.available_from < now() THEN 'PUBLIC'
                WHEN v.available_from > now() THEN 'CONTROLLED'
           END AS accessType                                    -- varchar(10)
      FROM data.datasets AS d
      JOIN data.dataset_version_current AS v
        ON v.dataset = d.id
      JOIN data.reference_sets AS r
        ON v.reference_set = r.id
      JOIN data.sample_sets AS s
        ON s.dataset = d.id
;


CREATE VIEW beacon.beacon_data_table AS
    SELECT dv.id AS index,                                      -- serial
           concat_ws(':', r.reference_build,
                          d.short_name,
                          v.dataset_version) AS datasetId,      -- varchar(128)
           dv.pos - 1 AS "start",                                -- integer
           substr(dv.chrom, 1, 2) AS chromosome,                -- varchar(2)
           dv.ref AS reference,                                 -- varchar(8192)
           dv.alt AS alternate,                                 -- varchar(8192)
           dv.pos - 1 + char_length(dv.ref) AS "end",           -- integer
           dv.allele_num AS callCount,                          -- integer
           dv.allele_freq AS frequency,                         -- integer
           dv.allele_count AS alleleCount,                      -- integer
           CASE WHEN length(dv.ref) = length(dv.alt) THEN 'SNP'
                WHEN length(dv.ref) > length(dv.alt) THEN 'DEL'
                WHEN length(dv.ref) < length(dv.alt) THEN 'INS'
           END AS variantType                                   -- varchar(16)
     FROM data.variants AS dv
      JOIN data.dataset_version_current as v
        ON dv.dataset_version = v.id
      JOIN data.datasets as d
        ON v.dataset = d.id
      JOIN data.reference_sets AS r
        ON v.reference_set = r.id
;


--------------------------------------------------------------------------------
-- Beacon views.
--
CREATE VIEW beacon.dataset_metadata(name, datasetId, description, assemblyId,
                                    createDateTime, updateDateTime, version,
                                    callCount, variantCount, sampleCount, externalUrl, accessType)
AS SELECT a.name, a.datasetId, a.description, a.assemblyId, a.createDateTime,
          a.updateDateTime, a.version, b.callCount,
          b.variantCount,
          a.sampleCount, a.externalUrl, a.accessType
FROM beacon.beacon_dataset_table a, beacon.beacon_dataset_counts_table b
WHERE a.datasetId=b.datasetId;

--------------------------------------------------------------------------------
-- Indexes
--
CREATE INDEX beacon_data_chrpos ON data.variants ((substr(chrom, 1, 2)),(pos-1));
-- Use if needed:
-- CREATE INDEX beacon_data_chrref ON data.variants ((substr(chrom, 1, 2)),ref);
