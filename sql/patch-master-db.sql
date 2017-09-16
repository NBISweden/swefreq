-- Patches a database that is using the master checkout of the
-- swefreq.sql schema definition to the develop version.

-- Add the two new meta data tables.

CREATE TABLE IF NOT EXISTS study (
    study_pk            INTEGER         NOT NULL PRIMARY KEY AUTO_INCREMENT,
    pi_name             VARCHAR(100)    NOT NULL,
    pi_email            VARCHAR(100)    NOT NULL,
    contact_name        VARCHAR(100)    NOT NULL,
    contact_email       VARCHAR(100)    NOT NULL,
    title               VARCHAR(100)    NOT NULL,
    description         TEXT            DEFAULT NULL,
    publication_date    DATE            NOT NULL,
    ref_doi             VARCHAR(100)    DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS sample_set (
    sample_set_pk       INTEGER         NOT NULL PRIMARY KEY AUTO_INCREMENT,
    study_pk            INTEGER         NOT NULL,
    ethnicity           VARCHAR(50)     DEFAULT NULL,
    collection          VARCHAR(100)    DEFAULT NULL,
    sample_size         INTEGER         NOT NULL,
    CONSTRAINT FOREIGN KEY (study_pk) REFERENCES study(study_pk)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Insert study and sample set.

INSERT INTO study
        (study_pk, pi_name, pi_email, contact_name, contact_email, title,
        publication_date, ref_doi)
VALUES  (1, "Ulf Gyllensten", "Ulf.Gyllensten@igp.uu.se",
        "the SweGen project", "swegen@scilifelab.se",
        "SweGen", '2016-12-23', "10.1038/ejhg.2017.130");

INSERT INTO sample_set
        (study_pk, sample_size, ethnicity, collection)
VALUES  (1, 1000, "Swedish", "Swedish Twin Registry");

-- Add the new columns to the dataset table. We don't care about
-- ordering the columns in the same order as in the schema file.

ALTER TABLE dataset ADD COLUMN (
        sample_set_pk   INTEGER         NOT NULL,
        avg_seq_depth   FLOAT           DEFAULT NULL,
        seq_type        VARCHAR(50)     DEFAULT NULL,
        seq_tech        VARCHAR(50)     DEFAULT NULL,
        seq_center      VARCHAR(100)    DEFAULT NULL,
        dataset_size    INTEGER         UNSIGNED DEFAULT NULL );

-- Insert correct values into dataset.dataset_size.

UPDATE dataset SET dataset_size = 1000, seq_type = "WGS",
        seq_tech = "Illumina HiSeq X", avg_seq_depth= 36.7,
        seq_center = "NGI, Scilifelab";

-- Correct the dataset.dataset_size column.

ALTER TABLE dataset MODIFY COLUMN dataset_size INTEGER UNSIGNED NOT NULL;

-- Insert reference to the sample set.

UPDATE dataset SET sample_set_pk = 1;

-- New foreign key in the dataset table.

ALTER TABLE dataset ADD CONSTRAINT
        FOREIGN KEY (sample_set_pk) REFERENCES sample_set(sample_set_pk);

-- Add new column to dataset_version.

ALTER TABLE dataset_version ADD COLUMN
        var_call_ref    VARCHAR(50)     DEFAULT NULL;

UPDATE dataset_version SET var_call_ref="hg19";

-- Add the linkhash table

CREATE TABLE IF NOT EXISTS linkhash (
    linkhash_pk         INTEGER         NOT NULL PRIMARY KEY AUTO_INCREMENT,
    dataset_version_pk  INTEGER         NOT NULL,
    user_pk             INTEGER         NOT NULL,
    hash                VARCHAR(64)     NOT NULL,
    expires_on          TIMESTAMP       NOT NULL,
    CONSTRAINT FOREIGN KEY (dataset_version_pk)
        REFERENCES dataset_version(dataset_version_pk),
    CONSTRAINT FOREIGN KEY (user_pk) REFERENCES user(user_pk)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- There's a new action ENUM in user_log too.

ALTER TABLE user_log MODIFY COLUMN
    action  ENUM ('consent','download',
                  'access_requested','access_granted','access_revoked',
                  'private_link')       DEFAULT NULL;

-- Add dataset_version.avaliable_from_ts and dataset_version.ref_doi

ALTER TABLE dataset_version ADD COLUMN (
    available_from      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    ref_doi             VARCHAR(100)    DEFAULT NULL
);

ALTER TABLE dataset_version DROP COLUMN ts;

-- add the dataset_version_current view

CREATE OR REPLACE VIEW dataset_version_current AS
    SELECT * FROM dataset_version
    WHERE (dataset_pk,dataset_version_pk) IN (
        SELECT dataset_pk, MAX(dataset_version_pk) FROM dataset_version
        WHERE available_from < now()
        GROUP BY dataset_pk );

-- add the dataset_access_current view

ALTER TABLE dataset_access
    DROP COLUMN has_consented,
    DROP COLUMN has_access;

CREATE OR REPLACE VIEW dataset_access_current AS
    SELECT DISTINCT
        access.*,
        TRUE AS has_access,
        (consent.action IS NOT NULL) AS has_consented
    FROM dataset_access AS access
    LEFT JOIN user_log AS consent
        ON access.user_pk = consent.user_pk AND
           consent.action = 'consent'
    WHERE access.user_pk IN (
    -- gets user_pk for all users with current access
    -- from https://stackoverflow.com/a/39190423/4941495
    SELECT granted.user_pk FROM user_log granted
        LEFT JOIN user_log revoked
                ON granted.user_pk = revoked.user_pk AND
                   revoked.action  = 'access_revoked'
        WHERE granted.action = 'access_granted' AND
                (revoked.user_pk IS NULL OR granted.ts > revoked.ts)
        GROUP BY granted.user_pk, granted.action
    );

-- add the dataset_access_waiting view

CREATE OR REPLACE VIEW dataset_access_waiting AS
    SELECT DISTINCT
        access.*,
        FALSE AS has_access,
        (consent.action IS NOT NULL) AS has_consented
    FROM dataset_access AS access
    LEFT JOIN user_log AS consent
        ON access.user_pk = consent.user_pk AND
           consent.action = 'consent'
    WHERE access.user_pk IN (
    -- get user_pk for all users that have pending access requests
    SELECT requested.user_pk FROM user_log requested
        LEFT JOIN user_log granted
                ON requested.user_pk = granted.user_pk AND
                   granted.action  = 'access_granted'
        WHERE requested.action = 'access_requested' AND
                (granted.user_pk IS NULL OR requested.ts > granted.ts)
        GROUP BY requested.user_pk, requested.action
    );

