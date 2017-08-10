-- Patches a database that is using the master checkout of the
-- swefreq.sql schema definition to the develop version.

USE swefreq;

-- Add the two new meta data tables.

CREATE TABLE IF NOT EXISTS study (
    study_pk            INTEGER         NOT NULL PRIMARY KEY AUTO_INCREMENT,
    pi_name             VARCHAR(100)    NOT NULL,
    pi_email            VARCHAR(100)    NOT NULL,
    contact_name        VARCHAR(100)    NOT NULL,
    contact_email       VARCHAR(100)    NOT NULL,
    title               VARCHAR(100)    NOT NULL,
    description         TEXT            DEFAULT NULL,
    ts                  TIMESTAMP       NOT NULL,
    ref_doi             VARCHAR(100)    DEFAULT NULL,
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS sample_set (
    sample_set_pk       INTEGER         NOT NULL PRIMARY KEY AUTO_INCREMENT,
    study_pk            INTEGER         NOT NULL,
    ethnicity           VARCHAR(50)     DEFAULT NULL,
    collection          VARCHAR(100)    DEFAULT NULL,
    sample_size         INTEGER         NOT NULL,
    CONSTRAINT FOREIGN KEY (study_pk) REFERENCES study(study_pk)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Add the new columns to the dataset table. We don't care about
-- ordering the columns in the same order as in the schema file.

ALTER TABLE dataset ADD COLUMN (
        sample_set_pk   INTEGER         NOT NULL,
        avg_seq_depth   FLOAT           DEFAULT NULL,
        seq_type        VARCHAR(50)     DEFAULT NULL,
        seq_tech        VARCHAR(50)     DEFAULT NULL,
        seq_center      VARCHAR(100)    DEFAULT NULL,
        dataset_size    INTEGER         UNSIGNED NOT NULL );

-- New foreign key in the dataset table.

ALTER TABLE dataset ADD CONSTRAINT
        FOREIGN KEY (sample_set_pk) REFERENCES sample_set(sample_set_pk);

-- Add new column to dataset_version.

ALTER TABLE dataset_version ADD COLUMN
        var_call_ref    VARCHAR(50)     DEFAULT NULL;
