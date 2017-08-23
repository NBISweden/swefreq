-- Patches a database that is using the master checkout of the
-- swefreq.sql schema definition to the develop version.

-- Add the three new meta data tables.

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

CREATE TABLE IF NOT EXISTS collection (
    collection_pk       INTEGER         NOT NULL PRIMARY KEY AUTO_INCREMENT,
    name                VARCHAR(100)    NOT NULL,
    ethnicity           VARCHAR(50)     DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS sample_set (
    sample_set_pk       INTEGER         NOT NULL PRIMARY KEY AUTO_INCREMENT,
    dataset_pk          INTEGER         NOT NULL,
    collection_pk       INTEGER         NOT NULL,
    sample_size         INTEGER         NOT NULL,
    phenotype           VARCHAR(50)     NOT NULL,
    CONSTRAINT FOREIGN KEY (dataset_pk) REFERENCES dataset(dataset_pk),
    CONSTRAINT FOREIGN KEY (collection_pk) REFERENCES collection(collection_pk)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Insert data into study, sample_set and collection:

INSERT INTO study
        (study_pk, pi_name, pi_email, contact_name, contact_email, title,
        publication_date, ref_doi)
VALUES  (1, "Ulf Gyllensten", "Ulf.Gyllensten@igp.uu.se",
        "the SweGen project", "swegen@scilifelab.se",
        "SweGen", '2016-12-23', "10.1038/ejhg.2017.130");

INSERT INTO collection (collection_pk, name, ethnicity)
VALUES  (1, "Swedish Twin Registry", "Swedish");

INSERT INTO sample_set
        (sample_set_pk, dataset_pk, collection_pk, sample_size, phenotype)
VALUES  (1, 1, 1, 1000, "None");

UPDATE dataset SET browser_uri="https://swegen-exac.nbis.se/" WHERE dataset_pk=1;

-- Add the new columns to the dataset table. We don't care about
-- ordering the columns in the same order as in the schema file.

ALTER TABLE dataset ADD COLUMN (
        study_pk        INTEGER         NOT NULL,
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

-- FIXME: (is this correct?)
UPDATE dataset SET study_pk = 1;

-- New foreign key in the dataset table.

ALTER TABLE dataset ADD CONSTRAINT
        FOREIGN KEY (study_pk) REFERENCES study(study_pk);

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

-- Summary view of user_log

CREATE OR REPLACE VIEW _user_log_summary AS
    SELECT MAX(user_log_pk) AS user_log_pk, user_pk, dataset_pk, action,
           MAX(ts) AS ts
    FROM user_log
    GROUP BY user_pk, dataset_pk, action;

-- Add dataset_version.avaliable_from_ts and dataset_version.ref_doi

ALTER TABLE dataset_version ADD COLUMN (
    available_from      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    ref_doi             VARCHAR(100)    DEFAULT NULL
);

ALTER TABLE dataset_version DROP COLUMN ts;

-- the above makes dataset_version.is_current superfluous

ALTER TABLE dataset_version DROP COLUMN is_current;

-- Add the ref_doi for the swegen dataset

UPDATE dataset_version SET ref_doi='10.17044/NBIS/G000003' WHERE dataset_version_pk=2;

-- add the dataset_version_current view

CREATE OR REPLACE VIEW dataset_version_current AS
    SELECT * FROM dataset_version
    WHERE (dataset_pk, dataset_version_pk) IN (
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
        (consent.action IS NOT NULL) AS has_consented,
        request.ts AS access_requested
    FROM dataset_access AS access
    JOIN ( SELECT user_pk, dataset_pk, MAX(ts) AS ts
           FROM user_log WHERE action = "access_requested"
           GROUP BY user_pk, dataset_pk ) AS request
        ON access.user_pk = request.user_pk AND
           access.dataset_pk = request.dataset_pk
    LEFT JOIN user_log AS consent
        ON access.user_pk = consent.user_pk AND
           access.dataset_pk = consent.dataset_pk AND
           consent.action = 'consent'
    WHERE (access.user_pk, access.dataset_pk) IN (
        -- gets user_pk for all users with current access
        -- from https://stackoverflow.com/a/39190423/4941495
        SELECT granted.user_pk, granted.dataset_pk
        FROM _user_log_summary AS granted
        LEFT JOIN _user_log_summary AS revoked
                ON granted.user_pk = revoked.user_pk AND
                   granted.dataset_pk = revoked.dataset_pk AND
                   revoked.action  = 'access_revoked'
        WHERE granted.action = 'access_granted' AND
            (revoked.user_pk IS NULL OR granted.ts > revoked.ts)
        GROUP BY granted.user_pk, granted.dataset_pk, granted.action
    );

-- add the dataset_access_pending view

CREATE OR REPLACE VIEW dataset_access_pending AS
    SELECT DISTINCT
        access.*,
        FALSE AS has_access,
        (consent.action IS NOT NULL) AS has_consented,
        request.ts AS access_requested
    FROM dataset_access AS access
    JOIN ( SELECT user_pk, dataset_pk, MAX(ts) AS ts
           FROM user_log WHERE action = "access_requested"
           GROUP BY user_pk, dataset_pk ) AS request
        ON access.user_pk = request.user_pk AND
           access.dataset_pk = request.dataset_pk
    LEFT JOIN user_log AS consent
        ON access.user_pk = consent.user_pk AND
           access.dataset_pk = consent.dataset_pk AND
           consent.action = 'consent'
    WHERE (access.user_pk, access.dataset_pk) IN (
        -- get user_pk for all users that have pending access requests
        SELECT requested.user_pk, requested.dataset_pk
        FROM _user_log_summary AS requested
        LEFT JOIN _user_log_summary AS granted
                ON requested.user_pk = granted.user_pk AND
                   requested.dataset_pk = granted.dataset_pk AND
                   granted.action  = 'access_granted'
        LEFT JOIN _user_log_summary AS revoked
                ON requested.user_pk = revoked.user_pk AND
                   requested.dataset_pk = revoked.dataset_pk AND
                   revoked.action  = 'access_revoked'
        WHERE requested.action = 'access_requested' AND
                (granted.user_pk IS NULL OR requested.ts > granted.ts) AND
                (revoked.user_pk IS NULL OR requested.ts > revoked.ts)
        GROUP BY requested.user_pk, requested.dataset_pk, requested.action
    );