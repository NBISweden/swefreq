-- Patches a database that is using the master checkout of the
-- swefreq.sql schema definition to the develop version.


ALTER TABLE dataset_version
    ADD COLUMN (
    data_contact_name VARCHAR(100) DEFAULT NULL,
    data_contact_link VARCHAR(100) DEFAULT NULL);

CREATE OR REPLACE VIEW dataset_version_current AS
    SELECT * FROM dataset_version
    WHERE (dataset_pk, dataset_version_pk) IN (
        SELECT dataset_pk, MAX(dataset_version_pk) FROM dataset_version
        WHERE available_from < now()
        GROUP BY dataset_pk );
