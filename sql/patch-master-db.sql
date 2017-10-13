-- Patches a database that is using the master checkout of the
-- swefreq.sql schema definition to the develop version.

-- Rename user_log to user_access_log

RENAME TABLE user_log TO user_access_log;
ALTER TABLE user_access_log
    CHANGE user_log_pk
    user_access_log_pk  INTEGER;

DROP VIEW _user_log_summary;
CREATE OR REPLACE VIEW _user_access_log_summary AS
    SELECT MAX(user_access_log_pk) AS user_access_log_pk, user_pk,
        dataset_pk, action, MAX(ts) AS ts
    FROM user_access_log
    GROUP BY user_pk, dataset_pk, action;

CREATE OR REPLACE VIEW dataset_access_current AS
    SELECT DISTINCT
        access.*,
        TRUE AS has_access,
        request.ts AS access_requested
    FROM dataset_access AS access
    JOIN ( SELECT user_pk, dataset_pk, MAX(ts) AS ts
           FROM user_access_log WHERE action = "access_requested"
           GROUP BY user_pk, dataset_pk ) AS request
        ON access.user_pk = request.user_pk AND
           access.dataset_pk = request.dataset_pk
    WHERE (access.user_pk, access.dataset_pk) IN (
        -- gets user_pk for all users with current access
        -- from https://stackoverflow.com/a/39190423/4941495
        SELECT granted.user_pk, granted.dataset_pk
        FROM _user_access_log_summary AS granted
        LEFT JOIN _user_access_log_summary AS revoked
                ON granted.user_pk = revoked.user_pk AND
                   granted.dataset_pk = revoked.dataset_pk AND
                   revoked.action  = 'access_revoked'
        WHERE granted.action = 'access_granted' AND
            (revoked.user_pk IS NULL OR granted.ts > revoked.ts)
        GROUP BY granted.user_pk, granted.dataset_pk, granted.action
    );

CREATE OR REPLACE VIEW dataset_access_pending AS
    SELECT DISTINCT
        access.*,
        FALSE AS has_access,
        request.ts AS access_requested
    FROM dataset_access AS access
    JOIN ( SELECT user_pk, dataset_pk, MAX(ts) AS ts
           FROM user_access_log WHERE action = "access_requested"
           GROUP BY user_pk, dataset_pk ) AS request
        ON access.user_pk = request.user_pk AND
           access.dataset_pk = request.dataset_pk
    WHERE (access.user_pk, access.dataset_pk) IN (
        -- get user_pk for all users that have pending access requests
        SELECT requested.user_pk, requested.dataset_pk
        FROM _user_access_log_summary AS requested
        LEFT JOIN _user_access_log_summary AS granted
                ON requested.user_pk = granted.user_pk AND
                   requested.dataset_pk = granted.dataset_pk AND
                   granted.action  = 'access_granted'
        LEFT JOIN _user_access_log_summary AS revoked
                ON requested.user_pk = revoked.user_pk AND
                   requested.dataset_pk = revoked.dataset_pk AND
                   revoked.action  = 'access_revoked'
        WHERE requested.action = 'access_requested' AND
                (granted.user_pk IS NULL OR requested.ts > granted.ts) AND
                (revoked.user_pk IS NULL OR requested.ts > revoked.ts)
        GROUP BY requested.user_pk, requested.dataset_pk, requested.action
    );

-- Create user_consent_log

CREATE TABLE IF NOT EXISTS user_consent_log (
    user_consent_log_pk INTEGER         NOT NULL PRIMARY KEY AUTO_INCREMENT,
    user_pk             INTEGER         NOT NULL,
    dataset_version_pk  INTEGER         NOT NULL,
    ts                  TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT FOREIGN KEY (user_pk)    REFERENCES user(user_pk),
    CONSTRAINT FOREIGN KEY (dataset_version_pk)
        REFERENCES dataset_version(dataset_version_pk)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Insert data into user_consent_log.  This is assuming that the dataset
-- that the user has consented to is the most current version of the
-- dataset.

INSERT INTO user_consent_log (user_pk, dataset_version_pk, ts)
    SELECT ul.user_pk, dvc.dataset_version_pk, ul.ts
    FROM user_access_log AS ul
    JOIN dataset_version_current AS dvc
        ON (dvc.dataset_pk = ul.dataset_pk)
    WHERE ul.action = 'consent';

-- Create user_download_log

CREATE TABLE IF NOT EXISTS user_download_log (
    user_download_log_pk
                        INTEGER         NOT NULL PRIMARY KEY AUTO_INCREMENT,
    user_pk             INTEGER         NOT NULL,
    dataset_file_pk     INTEGER         NOT NULL,
    ts                  TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT FOREIGN KEY (user_pk)    REFERENCES user(user_pk),
    CONSTRAINT FOREIGN KEY (dataset_file_pk)
        REFERENCES dataset_file(dataset_file_pk)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Insert data into user_download_log.  This is assuming that the
-- dataset that the user has downloaded is the most current version of
-- the dataset.

INSERT INTO user_download_log (user_pk, dataset_file_pk, ts)
    SELECT ul.user_pk, df.dataset_file_pk, ul.ts
    FROM user_access_log AS ul
    JOIN dataset_version_current AS dvc
        ON (dvc.dataset_pk = ul.dataset_pk)
    JOIN dataset_file AS df
        ON (df.dataset_version_pk = dvc.dataset_version_pk)
    WHERE ul.action = 'download';

-- Add unique constraint on linkhash.hash

ALTER TABLE linkhash
    ADD CONSTRAINT UNIQUE (hash);

-- Remove "consent" and "download" enums from user_access_log

DELETE FROM user_access_log
    WHERE action IN ('consent', 'download');

ALTER TABLE user_access_log
    CHANGE action
        action  ENUM ('access_requested','access_granted','access_revoked',
                      'private_link');
