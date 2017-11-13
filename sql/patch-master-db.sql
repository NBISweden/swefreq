-- Patches a database that is using the master checkout of the
-- swefreq.sql schema definition to the develop version.


-- Add mongodb_collection to the dataset table

ALTER TABLE dataset ADD COLUMN
    mongodb_collection VARCHAR(50);

UPDATE dataset SET mongodb_collection = 'exac'
    WHERE dataset_pk = 1;

ALTER TABLE dataset MODIFY COLUMN mongodb_collection
    mongodb_collection VARCHAR(50) NOT NULL;
