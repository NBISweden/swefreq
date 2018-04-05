-- Patches a database that is using the master checkout of the
-- swefreq.sql schema definition to the develop version.


ALTER TABLE dataset_version
    ADD COLUMN (
    data_contact_name VARCHAR(100) DEFAULT NULL,
    data_contact_link VARCHAR(100) DEFAULT NULL);